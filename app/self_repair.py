#!/usr/bin/env python3
"""Konservative Self-Repair-Schicht für PROVOWARE HEADQUARTER."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
from typing import Callable, Iterable

APP_NAME = "PROVOWARE HEADQUARTER"
CONFIG_VERSION = 1


@dataclass(frozen=True)
class RepairEvent:
    code: str
    status: str
    message: str
    changed: bool = False
    path: str | None = None

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "status": self.status,
            "message": self.message,
            "changed": self.changed,
            "path": self.path,
        }


@dataclass
class RepairReport:
    events: list[RepairEvent] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return any(event.changed for event in self.events)

    @property
    def blocking(self) -> bool:
        return any(event.status == "error" for event in self.events)

    @property
    def status(self) -> str:
        if self.blocking:
            return "error"
        if self.changed:
            return "repaired"
        if any(event.status == "warning" for event in self.events):
            return "warning"
        return "ok"

    def extend(self, other: "RepairReport") -> None:
        self.events.extend(other.events)

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "changed": self.changed,
            "blocking": self.blocking,
            "events": [event.as_dict() for event in self.events],
        }


class SelfRepairCoordinator:
    """Nur eindeutig sichere, reversible Reparaturen. Keine Nutzdatenlöschung."""

    def __init__(self, config_dir: Path | str, project_dirs: Iterable[str]) -> None:
        self.config_dir = Path(config_dir).expanduser().resolve(strict=False)
        self.project_dirs = tuple(project_dirs)
        self.config_path = self.config_dir / "config.json"

    @staticmethod
    def _now() -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")

    @staticmethod
    def _read_json_object(path: Path) -> dict | None:
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else None
        except (OSError, json.JSONDecodeError, UnicodeError):
            return None

    @classmethod
    def _valid_config(cls, path: Path) -> bool:
        data = cls._read_json_object(path)
        if data is None or data.get("config_version") != CONFIG_VERSION:
            return False
        active = data.get("active_project")
        if active is not None:
            if not isinstance(active, dict) or not isinstance(active.get("path"), str) or not active["path"].strip():
                return False
        profile = data.get("profile")
        return profile is None or isinstance(profile, dict)

    @classmethod
    def valid_project_marker(cls, project_root: Path | str) -> tuple[bool, str]:
        root = Path(project_root).expanduser().resolve(strict=False)
        marker = root / ".provoware" / "project.json"
        if not root.is_dir():
            return False, "Projektordner ist nicht erreichbar."
        if not marker.is_file():
            return False, "PROVOWARE-Projektmarker fehlt."
        data = cls._read_json_object(marker)
        if data is None:
            return False, "PROVOWARE-Projektmarker ist kein gültiges JSON-Objekt."
        if data.get("schema_version") != 1:
            return False, "PROVOWARE-Projektmarker hat eine unbekannte Schema-Version."
        if data.get("app") != APP_NAME:
            return False, "Projektmarker gehört nicht zur erwarteten Anwendung."
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return False, "Projektmarker enthält keinen gültigen Projektnamen."
        return True, "Projektmarker gültig."

    @staticmethod
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

    @classmethod
    def _atomic_copy(cls, source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp = destination.with_name(destination.name + ".repairing")
        shutil.copy2(source, temp)
        with temp.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temp, destination)
        cls._fsync_directory(destination.parent)

    @classmethod
    def _quarantine(cls, path: Path, label: str) -> Path:
        target = path.with_name(f"{path.name}.{label}-{cls._timestamp()}")
        os.replace(path, target)
        cls._fsync_directory(path.parent)
        return target

    def diagnose_config(self) -> RepairReport:
        report = RepairReport()
        if not self.config_path.exists():
            report.events.append(RepairEvent("CONFIG_ABSENT", "ok", "Noch keine Konfiguration vorhanden."))
            return report
        if self._valid_config(self.config_path):
            report.events.append(RepairEvent("CONFIG_OK", "ok", "Konfiguration ist gültig.", path=str(self.config_path)))
        else:
            report.events.append(RepairEvent("CONFIG_INVALID", "error", "Konfiguration ist beschädigt oder strukturell ungültig.", path=str(self.config_path)))
        return report

    def repair_config(self) -> RepairReport:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        report = RepairReport()
        if not self.config_path.exists():
            report.events.append(RepairEvent("CONFIG_ABSENT", "ok", "Noch keine Konfiguration vorhanden."))
            self._log(report, None)
            return report
        if self._valid_config(self.config_path):
            report.events.append(RepairEvent("CONFIG_OK", "ok", "Konfiguration ist gültig.", path=str(self.config_path)))
            stale = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
            if stale.exists():
                quarantined = self._quarantine(stale, "stale")
                report.events.append(RepairEvent("CONFIG_TEMP_QUARANTINED", "repaired", "Verwaiste temporäre Konfiguration wurde quarantänisiert.", True, str(quarantined)))
            self._log(report, None)
            return report

        candidates = (
            self.config_path.with_suffix(self.config_path.suffix + ".tmp"),
            self.config_path.with_suffix(self.config_path.suffix + ".bak1"),
            self.config_path.with_suffix(self.config_path.suffix + ".bak2"),
        )
        source = next((candidate for candidate in candidates if candidate.is_file() and self._valid_config(candidate)), None)
        if source is None:
            report.events.append(RepairEvent(
                "CONFIG_UNRECOVERABLE",
                "error",
                "Konfiguration ist ungültig; keine verifizierte Rückfallkopie vorhanden. Original bleibt unverändert.",
                path=str(self.config_path),
            ))
            self._log(report, None)
            return report

        quarantine = self._quarantine(self.config_path, "corrupt")
        try:
            self._atomic_copy(source, self.config_path)
        except OSError as exc:
            if quarantine.exists() and not self.config_path.exists():
                os.replace(quarantine, self.config_path)
                self._fsync_directory(self.config_path.parent)
            report.events.append(RepairEvent(
                "CONFIG_RESTORE_IO_FAILED",
                "error",
                f"Konfiguration konnte nicht sicher wiederhergestellt werden: {exc}",
                path=str(self.config_path),
            ))
            self._log(report, None)
            return report
        if not self._valid_config(self.config_path):
            if self.config_path.exists():
                self._quarantine(self.config_path, "failed-repair")
            self._atomic_copy(quarantine, self.config_path)
            report.events.append(RepairEvent(
                "CONFIG_RESTORE_FAILED",
                "error",
                "Wiederhergestellte Konfiguration bestand die Nachvalidierung nicht; Original wurde zurückgesetzt.",
                path=str(self.config_path),
            ))
            self._log(report, None)
            return report
        report.events.append(RepairEvent(
            "CONFIG_RESTORED",
            "repaired",
            f"Konfiguration aus verifizierter Rückfallkopie wiederhergestellt ({source.name}); beschädigtes Original wurde quarantänisiert.",
            True,
            str(self.config_path),
        ))
        self._log(report, None)
        return report

    def diagnose_project(self, project_root: Path | str | None) -> RepairReport:
        report = RepairReport()
        if project_root is None:
            report.events.append(RepairEvent("PROJECT_NOT_CONFIGURED", "warning", "Noch kein aktives Projekt eingerichtet."))
            return report
        root = Path(project_root).expanduser().resolve(strict=False)
        valid, message = self.valid_project_marker(root)
        if not valid:
            report.events.append(RepairEvent("PROJECT_MARKER_INVALID", "error", message, path=str(root)))
            return report
        report.events.append(RepairEvent("PROJECT_MARKER_OK", "ok", message, path=str(root)))
        for dirname in self.project_dirs:
            target = root / dirname
            if target.is_dir():
                continue
            if target.exists():
                report.events.append(RepairEvent("PROJECT_PATH_COLLISION", "error", f"Standardpfad '{dirname}' ist kein Ordner; keine automatische Änderung.", path=str(target)))
            else:
                report.events.append(RepairEvent("PROJECT_DIR_MISSING", "warning", f"Standardordner '{dirname}' fehlt.", path=str(target)))
        return report

    def repair_project(
        self,
        project_root: Path | str | None,
        data_core_factory: Callable[[Path], object] | None = None,
    ) -> RepairReport:
        report = RepairReport()
        if project_root is None:
            report.events.append(RepairEvent("PROJECT_NOT_CONFIGURED", "warning", "Noch kein aktives Projekt eingerichtet."))
            self._log(report, None)
            return report
        root = Path(project_root).expanduser().resolve(strict=False)
        valid, message = self.valid_project_marker(root)
        if not valid:
            report.events.append(RepairEvent("PROJECT_MARKER_INVALID", "error", message + " Keine automatische Reparatur.", path=str(root)))
            self._log(report, None)
            return report
        report.events.append(RepairEvent("PROJECT_MARKER_OK", "ok", message, path=str(root)))

        for dirname in self.project_dirs:
            target = root / dirname
            if target.is_dir():
                continue
            if target.exists():
                report.events.append(RepairEvent("PROJECT_PATH_COLLISION", "error", f"Standardpfad '{dirname}' ist kein Ordner; keine automatische Änderung.", path=str(target)))
                continue
            try:
                target.mkdir(parents=False, exist_ok=False)
                self._fsync_directory(root)
                report.events.append(RepairEvent("PROJECT_DIR_RECREATED", "repaired", f"Fehlender Standardordner '{dirname}' wurde neu angelegt.", True, str(target)))
            except OSError as exc:
                report.events.append(RepairEvent("PROJECT_DIR_REPAIR_FAILED", "error", f"Standardordner '{dirname}' konnte nicht sicher angelegt werden: {exc}", path=str(target)))

        if data_core_factory is not None and not report.blocking:
            try:
                core = data_core_factory(root)
                health = core.ensure_ready()
                if getattr(health, "recovered", False):
                    report.events.append(RepairEvent("DATABASE_RECOVERED", "repaired", "SQLite-Datenbank wurde aus verifizierter Sicherung wiederhergestellt.", True, getattr(health, "db_path", None)))
                else:
                    report.events.append(RepairEvent("DATABASE_OK", "ok", "SQLite-Datenkern ist integer und betriebsbereit.", path=getattr(health, "db_path", None)))
            except Exception as exc:
                report.events.append(RepairEvent("DATABASE_REPAIR_BLOCKED", "error", f"SQLite-Self-Repair konnte keinen sicheren Zustand herstellen: {exc}"))
        self._log(report, root)
        return report

    def run(
        self,
        project_root: Path | str | None,
        data_core_factory: Callable[[Path], object] | None = None,
    ) -> RepairReport:
        report = self.repair_config()
        report.extend(self.repair_project(project_root, data_core_factory))
        return report

    def diagnose(self, project_root: Path | str | None) -> RepairReport:
        report = self.diagnose_config()
        report.extend(self.diagnose_project(project_root))
        return report

    def _log(self, report: RepairReport, project_root: Path | None) -> None:
        try:
            log_dir = (project_root / "logs") if project_root is not None and project_root.is_dir() else (self.config_dir / "logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            path = log_dir / "selfrepair.jsonl"
            payload = {"at": self._now(), **report.as_dict()}
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError:
            # Logging darf eine ansonsten sichere Reparatur nicht in einen neuen Fehler verwandeln.
            pass
