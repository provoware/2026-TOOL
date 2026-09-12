#!/usr/bin/env python3
"""Lokaler, dependency-freier Server für PROVOWARE HEADQUARTER."""
from __future__ import annotations

import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

APP_ID = "provoware-headquarter"
APP_NAME = "PROVOWARE HEADQUARTER"
APP_VERSION = "0.2.1"
ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
STATIC_ROOT = APP_DIR / "static"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_core import DataCore, DataIntegrityError, DataNotFoundError, DataValidationError
from project_store import PROJECT_DIRS, ProjectStore, load_json
from self_repair import RepairReport, SelfRepairCoordinator


def _config_dir() -> Path:
    override = os.environ.get("PROVOWARE_CONFIG_DIR")
    return Path(override).expanduser() if override else Path.home() / ".config" / APP_ID


class AppContext:
    def __init__(self) -> None:
        self.config_dir = _config_dir()
        self.repair = SelfRepairCoordinator(self.config_dir, PROJECT_DIRS)
        self._last_repair = self.repair.repair_config()
        self.store = ProjectStore(self.config_dir)
        self.previous_unclean = self.store.session_marker.exists()
        self.store.session_marker.write_text(str(os.getpid()), encoding="utf-8")
        self.logger = self._build_logger()
        self._data_lock = threading.RLock()
        self._data_path: Path | None = None
        self._data: DataCore | None = None

        project_path = self.store.active_project_path()
        if project_path is not None:
            self._last_repair.extend(self.repair.repair_project(project_path, DataCore))
        self._log_repair_summary(self._last_repair, "startup")

    def _build_logger(self) -> logging.Logger:
        log_dir = self.store.config_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger(APP_ID)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = RotatingFileHandler(log_dir / "server.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(handler)
        return logger

    def _log_repair_summary(self, report: RepairReport, source: str) -> None:
        level = logging.ERROR if report.blocking else logging.WARNING if report.status in {"warning", "repaired"} else logging.INFO
        self.logger.log(level, "Self-Repair %s: status=%s changed=%s blocking=%s events=%d", source, report.status, report.changed, report.blocking, len(report.events))

    def bootstrap(self) -> dict:
        payload = self.store.bootstrap()
        payload.update({
            "app_id": APP_ID,
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "self_repair": self._last_repair.as_dict(),
        })
        return payload

    def data_core(self) -> DataCore:
        project_path = self.store.active_project_path()
        if project_path is None:
            raise RuntimeError("Kein verfügbares Projekt eingerichtet.")
        with self._data_lock:
            if self._data is None or self._data_path != project_path:
                self._data = DataCore(project_path)
                self._data_path = project_path
            return self._data

    def invalidate_project_services(self) -> None:
        with self._data_lock:
            self._data = None
            self._data_path = None

    def diagnose_self_repair(self) -> RepairReport:
        return self.repair.diagnose(self.store.active_project_path())

    def run_self_repair(self) -> RepairReport:
        report = self.repair.repair_config()
        if any(event.code == "CONFIG_RESTORED" for event in report.events):
            self.store = ProjectStore(self.config_dir)
        project_path = self.store.active_project_path()
        report.extend(self.repair.repair_project(project_path, DataCore))
        self._last_repair = report
        if not report.blocking:
            self.invalidate_project_services()
        self._log_repair_summary(report, "manual")
        return report

    def repair_after_project_change(self) -> RepairReport:
        report = self.repair.repair_project(self.store.active_project_path(), DataCore)
        self._last_repair = report
        self.invalidate_project_services()
        self._log_repair_summary(report, "project-change")
        return report

    def clean_shutdown(self) -> None:
        try:
            with self._data_lock:
                if self._data is not None and self._data.db_path.exists():
                    try:
                        self._data.create_verified_backup("clean")
                    except Exception:
                        self.logger.exception("Saubere Datenbanksicherung beim Beenden fehlgeschlagen")
            self.store.session_marker.unlink(missing_ok=True)
        except OSError:
            self.logger.exception("Sessionmarker konnte nicht entfernt werden")


class Handler(BaseHTTPRequestHandler):
    server_version = "PROVOWARE/0.2.1"

    @property
    def app(self) -> AppContext:
        return self.server.app

    def log_message(self, format: str, *args) -> None:
        self.app.logger.info("HTTP " + format, *args)

    def _json(self, status: int, payload: dict | list) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 1_000_000:
            raise ValueError("Anfrage zu groß.")
        raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON-Objekt erwartet.")
        return data

    def _data(self) -> DataCore:
        return self.app.data_core()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        try:
            if path == "/api/health":
                self._json(HTTPStatus.OK, {"status": "ok", "app_id": APP_ID, "version": APP_VERSION})
                return
            if path == "/api/bootstrap":
                payload = self.app.bootstrap()
                payload["previous_unclean"] = self.app.previous_unclean
                self._json(HTTPStatus.OK, payload)
                return
            if path == "/api/manifest":
                manifest = load_json(ROOT / "projekt-manifest.json", {})
                status = HTTPStatus.OK if manifest else HTTPStatus.INTERNAL_SERVER_ERROR
                self._json(status, manifest or {"error": "Manifest fehlt oder ist ungültig.", "code": "MANIFEST"})
                return
            if path == "/api/project/pick-base":
                self._pick_project_base()
                return
            if path == "/api/self-repair/status":
                self._json(HTTPStatus.OK, self.app.diagnose_self_repair().as_dict())
                return
            if path == "/api/data/health":
                self._json(HTTPStatus.OK, self._data().ensure_ready().as_dict())
                return
            if path == "/api/data/summary":
                self._json(HTTPStatus.OK, self._data().summary())
                return
            if path == "/api/todos":
                scope = query.get("scope", ["active"])[0]
                self._json(HTTPStatus.OK, {"scope": scope, "items": self._data().list_todos(scope)})
                return
            if path == "/api/calendar":
                month = query.get("month", [""])[0]
                self._json(HTTPStatus.OK, self._data().calendar_month(month))
                return
            self._serve_static(path)
        except Exception as exc:
            self._handle_api_exception(exc)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            data = self._read_json()
            if path == "/api/project/create":
                project = self.app.store.create_project(str(data.get("base_path", "")), str(data.get("name", "")))
                repair = self.app.repair_after_project_change()
                if repair.blocking:
                    raise DataIntegrityError("Projekt wurde angelegt, bestand aber die automatische Nachvalidierung nicht.")
                self._json(HTTPStatus.CREATED, {"project": project, "self_repair": repair.as_dict()})
                return
            if path == "/api/self-repair/run":
                report = self.app.run_self_repair()
                status = HTTPStatus.SERVICE_UNAVAILABLE if report.blocking else HTTPStatus.OK
                self._json(status, report.as_dict())
                return
            if path == "/api/quick-save":
                saved = self.app.store.quick_save(str(data.get("title", "")), str(data.get("text", "")))
                self._json(HTTPStatus.OK, {"saved": True, "path": str(saved)})
                return
            if path == "/api/todos":
                item = self._data().create_todo(
                    str(data.get("title", "")),
                    description=str(data.get("description", "")),
                    priority=str(data.get("priority", "normal")),
                    due_date=data.get("due_date"),
                    due_time=data.get("due_time"),
                )
                self._json(HTTPStatus.CREATED, {"todo": item})
                return
            match = re.fullmatch(r"/api/todos/(\d+)/(archive|restore)", path)
            if match:
                todo_id = int(match.group(1))
                item = self._data().archive_todo(todo_id) if match.group(2) == "archive" else self._data().restore_todo(todo_id)
                self._json(HTTPStatus.OK, {"todo": item})
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "Unbekannter API-Endpunkt.", "code": "NOT-FOUND"})
        except Exception as exc:
            self._handle_api_exception(exc)

    def _pick_project_base(self) -> None:
        picker = shutil.which("kdialog")
        if not picker:
            self._json(HTTPStatus.NOT_IMPLEMENTED, {"error": "KDialog ist nicht verfügbar.", "fallback": str(Path.home()), "code": "PICKER-UNAVAILABLE"})
            return
        try:
            result = subprocess.run([picker, "--getexistingdirectory", str(Path.home())], check=False, text=True, capture_output=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(exc), "code": "PICKER-ERROR"})
            return
        selected = result.stdout.strip()
        self._json(HTTPStatus.OK, {"path": selected, "cancelled": not bool(selected)})

    def _handle_api_exception(self, exc: Exception) -> None:
        if isinstance(exc, FileExistsError):
            self._json(HTTPStatus.CONFLICT, {"error": str(exc), "code": "PROJECT-CONFLICT"})
        elif isinstance(exc, PermissionError):
            self._json(HTTPStatus.FORBIDDEN, {"error": str(exc), "code": "PERMISSION"})
        elif isinstance(exc, (DataValidationError, ValueError, json.JSONDecodeError)):
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc), "code": "VALIDATION"})
        elif isinstance(exc, DataNotFoundError):
            self._json(HTTPStatus.NOT_FOUND, {"error": str(exc), "code": "NOT-FOUND"})
        elif isinstance(exc, RuntimeError) and not isinstance(exc, DataIntegrityError):
            self._json(HTTPStatus.CONFLICT, {"error": str(exc), "code": "CONFLICT"})
        elif isinstance(exc, DataIntegrityError):
            self.app.logger.exception("Datenintegritätsfehler")
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(exc), "code": "DATA-INTEGRITY"})
        else:
            self.app.logger.exception("Unbehandelter API-Fehler")
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Interner Fehler. Details wurden protokolliert.", "code": "INTERNAL"})

    def _serve_static(self, request_path: str) -> None:
        relative = "index.html" if request_path == "/" else unquote(request_path.lstrip("/"))
        if relative.startswith("static/"):
            relative = relative.removeprefix("static/")
        candidate = (STATIC_ROOT / relative).resolve(strict=False)
        if STATIC_ROOT not in candidate.parents and candidate != STATIC_ROOT:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        mime = "application/octet-stream"
        if candidate.suffix == ".html": mime = "text/html; charset=utf-8"
        elif candidate.suffix == ".css": mime = "text/css; charset=utf-8"
        elif candidate.suffix == ".js": mime = "text/javascript; charset=utf-8"
        elif candidate.suffix == ".json": mime = "application/json; charset=utf-8"
        raw = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def open_browser(url: str) -> None:
    for candidate in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        binary = shutil.which(candidate)
        if binary:
            subprocess.Popen([binary, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    opener = shutil.which("xdg-open")
    if opener:
        subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> int:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0, help="0 = freien Port automatisch wählen")
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        parser.error("Aus Sicherheitsgründen ist nur localhost erlaubt.")
    app = AppContext()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.app = app
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/"
    app.logger.info("Start %s %s auf %s", APP_NAME, APP_VERSION, url)
    print(f"{APP_NAME} {APP_VERSION}: {url}", flush=True)
    stop_event = threading.Event()
    def shutdown_handler(signum, frame):
        if not stop_event.is_set():
            stop_event.set()
            threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    if args.open_browser:
        threading.Timer(0.25, open_browser, args=(url,)).start()
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()
        app.clean_shutdown()
        app.logger.info("Sauber beendet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
