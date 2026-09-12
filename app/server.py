#!/usr/bin/env python3
"""Lokaler, dependency-freier Server für die PROVOWARE HEADQUARTER Expert Shell."""
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
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

APP_ID = "provoware-headquarter"
APP_NAME = "PROVOWARE HEADQUARTER"
APP_VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = ROOT / "app" / "static"
PROJECT_DIRS = ("datenbanken", "archiv", "todo", "notizen", "schnellspeicher", "logs", "export", "sicherungen", "cache")
BLOCKED_BASE_PATHS = {Path("/"), Path("/bin"), Path("/boot"), Path("/dev"), Path("/etc"), Path("/proc"), Path("/sys"), Path("/usr")}

def _config_dir() -> Path:
    override = os.environ.get("PROVOWARE_CONFIG_DIR")
    return Path(override).expanduser() if override else Path.home() / ".config" / APP_ID

def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bak1 = path.with_suffix(path.suffix + ".bak1")
    bak2 = path.with_suffix(path.suffix + ".bak2")
    if bak1.exists(): shutil.copy2(bak1, bak2)
    if path.exists(): shutil.copy2(path, bak1)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
    os.replace(temp, path)

def load_json(path: Path, default: dict) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle: data = json.load(handle)
        return data if isinstance(data, dict) else default.copy()
    except (OSError, json.JSONDecodeError):
        return default.copy()

def sanitize_project_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/\x00-\x1f]+", "-", value)
    value = re.sub(r"\s+", " ", value)
    if not value or value in {".", ".."}: raise ValueError("Projektname fehlt oder ist ungültig.")
    if len(value) > 80: raise ValueError("Projektname darf höchstens 80 Zeichen lang sein.")
    return value

class ProjectStore:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or _config_dir()
        self.config_path = self.config_dir / "config.json"
        self.session_marker = self.config_dir / "session.lock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = load_json(self.config_path, {"config_version": 1, "active_project": None, "profile": {"name": "Lokaler Nutzer"}})

    def bootstrap(self) -> dict:
        active = self.config.get("active_project")
        project_status = {"configured": False, "available": False, "path": None, "name": None}
        if isinstance(active, dict) and active.get("path"):
            path = Path(active["path"]); marker = path / ".provoware" / "project.json"
            project_status = {"configured": True, "available": path.is_dir() and marker.is_file(), "path": str(path), "name": active.get("name") or path.name}
        return {"app_id": APP_ID, "app_name": APP_NAME, "version": APP_VERSION, "profile": self.config.get("profile", {"name": "Lokaler Nutzer"}), "project": project_status}

    def create_project(self, base_path: str, name: str) -> dict:
        project_name = sanitize_project_name(name)
        base = Path(base_path).expanduser().resolve(strict=False)
        if base in BLOCKED_BASE_PATHS: raise ValueError("Dieser Systemordner ist als Projektbasis gesperrt.")
        base.mkdir(parents=True, exist_ok=True)
        if not base.is_dir() or not os.access(base, os.W_OK): raise PermissionError("Projektbasis ist nicht beschreibbar.")
        target = (base / project_name).resolve(strict=False)
        if base not in target.parents: raise ValueError("Projektpfad verlässt die gewählte Projektbasis.")
        marker = target / ".provoware" / "project.json"
        if target.exists() and any(target.iterdir()) and not marker.is_file(): raise FileExistsError("Zielordner ist nicht leer und noch kein PROVOWARE-Projekt.")
        target.mkdir(parents=True, exist_ok=True)
        for dirname in PROJECT_DIRS: (target / dirname).mkdir(exist_ok=True)
        marker.parent.mkdir(exist_ok=True)
        atomic_write_json(marker, {"schema_version": 1, "name": project_name, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "app": APP_NAME})
        self.config["active_project"] = {"name": project_name, "path": str(target)}
        atomic_write_json(self.config_path, self.config)
        return self.bootstrap()["project"]

    def quick_save(self, title: str, text: str) -> Path:
        project = self.bootstrap()["project"]
        if not project["available"]: raise RuntimeError("Kein verfügbares Projekt eingerichtet.")
        clean_title = re.sub(r"[^\w .-]+", "_", title.strip(), flags=re.UNICODE).strip(" .")
        if not clean_title: raise ValueError("Titel fehlt.")
        if len(clean_title) > 100: clean_title = clean_title[:100].rstrip()
        if not text.strip(): raise ValueError("Text fehlt.")
        path = Path(project["path"]) / "schnellspeicher" / f"{clean_title}.md"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## {timestamp}\n\n{text.rstrip()}\n"); handle.flush(); os.fsync(handle.fileno())
        return path

class AppContext:
    def __init__(self) -> None:
        self.store = ProjectStore(); self.previous_unclean = self.store.session_marker.exists()
        self.store.session_marker.write_text(str(os.getpid()), encoding="utf-8"); self.logger = self._build_logger()
    def _build_logger(self) -> logging.Logger:
        log_dir = self.store.config_dir / "logs"; log_dir.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger(APP_ID); logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = RotatingFileHandler(log_dir / "server.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s")); logger.addHandler(handler)
        return logger
    def clean_shutdown(self) -> None:
        try: self.store.session_marker.unlink(missing_ok=True)
        except OSError: self.logger.exception("Sessionmarker konnte nicht entfernt werden")

class Handler(BaseHTTPRequestHandler):
    server_version = "PROVOWARE/0.1"
    @property
    def app(self) -> AppContext: return self.server.app
    def log_message(self, format: str, *args) -> None: self.app.logger.info("HTTP " + format, *args)
    def _json(self, status: int, payload: dict) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8"); self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Cache-Control", "no-store"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 1_000_000: raise ValueError("Anfrage zu groß.")
        raw = self.rfile.read(length) if length else b"{}"; data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict): raise ValueError("JSON-Objekt erwartet.")
        return data
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health": self._json(HTTPStatus.OK, {"status": "ok", "app_id": APP_ID, "version": APP_VERSION}); return
        if path == "/api/bootstrap":
            payload = self.app.store.bootstrap(); payload["previous_unclean"] = self.app.previous_unclean; self._json(HTTPStatus.OK, payload); return
        if path == "/api/manifest":
            manifest = load_json(ROOT / "projekt-manifest.json", {}); status = HTTPStatus.OK if manifest else HTTPStatus.INTERNAL_SERVER_ERROR
            self._json(status, manifest or {"error": "Manifest fehlt oder ist ungültig."}); return
        if path == "/api/project/pick-base":
            picker = shutil.which("kdialog")
            if not picker: self._json(HTTPStatus.NOT_IMPLEMENTED, {"error": "KDialog ist nicht verfügbar.", "fallback": str(Path.home())}); return
            try: result = subprocess.run([picker, "--getexistingdirectory", str(Path.home())], check=False, text=True, capture_output=True, timeout=120)
            except (OSError, subprocess.TimeoutExpired) as exc: self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(exc)}); return
            selected = result.stdout.strip(); self._json(HTTPStatus.OK, {"path": selected, "cancelled": not bool(selected)}); return
        self._serve_static(path)
    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            data = self._read_json()
            if path == "/api/project/create": self._json(HTTPStatus.CREATED, {"project": self.app.store.create_project(str(data.get("base_path", "")), str(data.get("name", "")))}); return
            if path == "/api/quick-save": self._json(HTTPStatus.OK, {"saved": True, "path": str(self.app.store.quick_save(str(data.get("title", "")), str(data.get("text", ""))))}); return
            self._json(HTTPStatus.NOT_FOUND, {"error": "Unbekannter API-Endpunkt."})
        except FileExistsError as exc: self._json(HTTPStatus.CONFLICT, {"error": str(exc)})
        except PermissionError as exc: self._json(HTTPStatus.FORBIDDEN, {"error": str(exc)})
        except (ValueError, json.JSONDecodeError) as exc: self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except RuntimeError as exc: self._json(HTTPStatus.CONFLICT, {"error": str(exc)})
        except Exception: self.app.logger.exception("Unbehandelter API-Fehler"); self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Interner Fehler. Details wurden protokolliert."})
    def _serve_static(self, request_path: str) -> None:
        relative = "index.html" if request_path == "/" else unquote(request_path.lstrip("/"))
        if relative.startswith("static/"): relative = relative.removeprefix("static/")
        candidate = (STATIC_ROOT / relative).resolve(strict=False)
        if STATIC_ROOT not in candidate.parents and candidate != STATIC_ROOT: self.send_error(HTTPStatus.FORBIDDEN); return
        if not candidate.is_file(): self.send_error(HTTPStatus.NOT_FOUND); return
        mime = "application/octet-stream"
        if candidate.suffix == ".html": mime = "text/html; charset=utf-8"
        elif candidate.suffix == ".css": mime = "text/css; charset=utf-8"
        elif candidate.suffix == ".js": mime = "text/javascript; charset=utf-8"
        elif candidate.suffix == ".json": mime = "application/json; charset=utf-8"
        raw = candidate.read_bytes(); self.send_response(HTTPStatus.OK); self.send_header("Content-Type", mime); self.send_header("Cache-Control", "no-cache"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

def open_browser(url: str) -> None:
    for candidate in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        binary = shutil.which(candidate)
        if binary: subprocess.Popen([binary, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return
    opener = shutil.which("xdg-open")
    if opener: subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main() -> int:
    parser = argparse.ArgumentParser(description=APP_NAME); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=0, help="0 = freien Port automatisch wählen"); parser.add_argument("--open-browser", action="store_true"); args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost"}: parser.error("Aus Sicherheitsgründen ist in v0.1 nur localhost erlaubt.")
    app = AppContext(); server = ThreadingHTTPServer((args.host, args.port), Handler); server.app = app
    host, port = server.server_address[:2]; url = f"http://{host}:{port}/"; app.logger.info("Start %s %s auf %s", APP_NAME, APP_VERSION, url); print(f"{APP_NAME} {APP_VERSION}: {url}", flush=True)
    stop_event = threading.Event()
    def shutdown_handler(signum, frame):
        if not stop_event.is_set(): stop_event.set(); threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGINT, shutdown_handler); signal.signal(signal.SIGTERM, shutdown_handler)
    if args.open_browser: threading.Timer(0.25, open_browser, args=(url,)).start()
    try: server.serve_forever(poll_interval=0.25)
    finally: server.server_close(); app.clean_shutdown(); app.logger.info("Sauber beendet")
    return 0

if __name__ == "__main__": raise SystemExit(main())
