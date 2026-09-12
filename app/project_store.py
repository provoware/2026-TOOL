#!/usr/bin/env python3
"""Projekt- und Konfigurationspersistenz für PROVOWARE HEADQUARTER."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import time

from data_core import DataCore
from self_repair import SelfRepairCoordinator

APP_NAME = "PROVOWARE HEADQUARTER"
PROJECT_DIRS = (
    "datenbanken", "archiv", "todo", "notizen", "schnellspeicher",
    "logs", "export", "sicherungen", "cache",
)
BLOCKED_BASE_PATHS = {
    Path("/"), Path("/bin"), Path("/boot"), Path("/dev"),
    Path("/etc"), Path("/proc"), Path("/sys"), Path("/usr"),
}


def _fsync_directory(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _copy_with_sync(source: Path, destination: Path) -> None:
    shutil.copy2(source, destination)
    with destination.open("rb") as handle:
        os.fsync(handle.fileno())


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bak1 = path.with_suffix(path.suffix + ".bak1")
    bak2 = path.with_suffix(path.suffix + ".bak2")
    if bak1.exists():
        _copy_with_sync(bak1, bak2)
    if path.exists():
        _copy_with_sync(path, bak1)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    _fsync_directory(path.parent)


def load_json(path: Path, default: dict) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else default.copy()
    except (OSError, json.JSONDecodeError, UnicodeError):
        return default.copy()


def sanitize_project_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/\x00-\x1f]+", "-", value)
    value = re.sub(r"\s+", " ", value)
    if not value or value in {".", ".."}:
        raise ValueError("Projektname fehlt oder ist ungültig.")
    if len(value) > 80:
        raise ValueError("Projektname darf höchstens 80 Zeichen lang sein.")
    return value


class ProjectStore:
    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir
        self.config_path = self.config_dir / "config.json"
        self.session_marker = self.config_dir / "session.lock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = load_json(
            self.config_path,
            {"config_version": 1, "active_project": None, "profile": {"name": "Lokaler Nutzer"}},
        )

    @staticmethod
    def _project_marker_valid(path: Path) -> bool:
        valid, _ = SelfRepairCoordinator.valid_project_marker(path)
        return valid

    def bootstrap(self) -> dict:
        active = self.config.get("active_project")
        project_status = {"configured": False, "available": False, "path": None, "name": None}
        if isinstance(active, dict) and active.get("path"):
            path = Path(active["path"]).expanduser().resolve(strict=False)
            marker_valid = self._project_marker_valid(path)
            project_status = {
                "configured": True,
                "available": path.is_dir() and marker_valid,
                "path": str(path),
                "name": active.get("name") or path.name,
                "marker_valid": marker_valid,
            }
        return {
            "profile": self.config.get("profile", {"name": "Lokaler Nutzer"}),
            "project": project_status,
        }

    def active_project_path(self) -> Path | None:
        project = self.bootstrap()["project"]
        if not project["available"] or not project["path"]:
            return None
        return Path(project["path"]).resolve(strict=False)

    def create_project(self, base_path: str, name: str) -> dict:
        project_name = sanitize_project_name(name)
        base = Path(base_path).expanduser().resolve(strict=False)
        if base in BLOCKED_BASE_PATHS:
            raise ValueError("Dieser Systemordner ist als Projektbasis gesperrt.")
        base.mkdir(parents=True, exist_ok=True)
        if not base.is_dir() or not os.access(base, os.W_OK):
            raise PermissionError("Projektbasis ist nicht beschreibbar.")

        target = (base / project_name).resolve(strict=False)
        if base not in target.parents:
            raise ValueError("Projektpfad verlässt die gewählte Projektbasis.")

        marker = target / ".provoware" / "project.json"
        if target.exists() and any(target.iterdir()) and not self._project_marker_valid(target):
            raise FileExistsError(
                "Zielordner ist nicht leer oder besitzt keinen gültigen PROVOWARE-Projektmarker. "
                "Aus Sicherheitsgründen wird er nicht automatisch übernommen."
            )

        target.mkdir(parents=True, exist_ok=True)
        for dirname in PROJECT_DIRS:
            destination = target / dirname
            if destination.exists() and not destination.is_dir():
                raise FileExistsError(f"Standardpfad '{dirname}' ist bereits als Datei vorhanden.")
            destination.mkdir(exist_ok=True)
        marker.parent.mkdir(exist_ok=True)
        if not marker.exists():
            atomic_write_json(marker, {
                "schema_version": 1,
                "name": project_name,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "app": APP_NAME,
            })
        if not self._project_marker_valid(target):
            raise RuntimeError("Projektmarker bestand die Nachvalidierung nicht.")

        DataCore(target).ensure_ready()
        self.config["active_project"] = {"name": project_name, "path": str(target)}
        atomic_write_json(self.config_path, self.config)
        return self.bootstrap()["project"]

    def quick_save(self, title: str, text: str) -> Path:
        project_path = self.active_project_path()
        if project_path is None:
            raise RuntimeError("Kein verfügbares Projekt eingerichtet.")
        clean_title = re.sub(r"[^\w .-]+", "_", title.strip(), flags=re.UNICODE).strip(" .")
        if not clean_title:
            raise ValueError("Titel fehlt.")
        if len(clean_title) > 100:
            clean_title = clean_title[:100].rstrip()
        if not text.strip():
            raise ValueError("Text fehlt.")
        path = project_path / "schnellspeicher" / f"{clean_title}.md"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## {timestamp}\n\n{text.rstrip()}\n")
            handle.flush()
            os.fsync(handle.fileno())
        return path
