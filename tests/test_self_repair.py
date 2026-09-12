from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
if str(ROOT / "app") not in sys.path:
    sys.path.insert(0, str(ROOT / "app"))

from self_repair import SelfRepairCoordinator

PROJECT_DIRS = ("datenbanken", "archiv", "todo", "notizen", "schnellspeicher", "logs", "export", "sicherungen", "cache")


def valid_config(path: Path, project: Path | None = None) -> None:
    payload = {
        "config_version": 1,
        "active_project": None if project is None else {"name": project.name, "path": str(project)},
        "profile": {"name": "Test"},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def valid_marker(project: Path) -> None:
    marker = project / ".provoware" / "project.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({
        "schema_version": 1,
        "name": project.name,
        "created_at": "2026-09-12T00:00:00+02:00",
        "app": "PROVOWARE HEADQUARTER",
    }), encoding="utf-8")


class _Health:
    recovered = False
    db_path = "/tmp/test.sqlite3"


class _FakeCore:
    def __init__(self, root: Path):
        self.root = root

    def ensure_ready(self):
        return _Health()


class SelfRepairTests(unittest.TestCase):
    def test_invalid_config_restores_verified_backup_and_quarantines_original(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "config"
            config.mkdir()
            current = config / "config.json"
            current.write_text("{kaputt", encoding="utf-8")
            valid_config(config / "config.json.bak1")
            repair = SelfRepairCoordinator(config, PROJECT_DIRS)
            report = repair.repair_config()
            self.assertEqual(report.status, "repaired")
            self.assertFalse(report.blocking)
            self.assertEqual(json.loads(current.read_text(encoding="utf-8"))["config_version"], 1)
            self.assertEqual(len(list(config.glob("config.json.corrupt-*"))), 1)

    def test_invalid_config_without_verified_backup_is_left_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "config"
            config.mkdir()
            current = config / "config.json"
            original = "{kaputt"
            current.write_text(original, encoding="utf-8")
            (config / "config.json.bak1").write_text("[]", encoding="utf-8")
            repair = SelfRepairCoordinator(config, PROJECT_DIRS)
            report = repair.repair_config()
            self.assertTrue(report.blocking)
            self.assertEqual(current.read_text(encoding="utf-8"), original)
            self.assertEqual(list(config.glob("config.json.corrupt-*")), [])

    def test_valid_temp_config_can_recover_interrupted_atomic_write(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "config"
            config.mkdir()
            (config / "config.json").write_text("{kaputt", encoding="utf-8")
            valid_config(config / "config.json.tmp")
            repair = SelfRepairCoordinator(config, PROJECT_DIRS)
            report = repair.repair_config()
            self.assertEqual(report.status, "repaired")
            self.assertTrue(SelfRepairCoordinator._valid_config(config / "config.json"))

    def test_project_directories_are_recreated_only_with_valid_marker(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "project"
            project.mkdir()
            valid_marker(project)
            repair = SelfRepairCoordinator(Path(td) / "config", PROJECT_DIRS)
            report = repair.repair_project(project, _FakeCore)
            self.assertFalse(report.blocking)
            self.assertTrue(all((project / name).is_dir() for name in PROJECT_DIRS))
            self.assertTrue(any(event.code == "PROJECT_DIR_RECREATED" for event in report.events))

    def test_foreign_project_is_never_adopted_or_modified(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "foreign"
            project.mkdir()
            sentinel = project / "privat.txt"
            sentinel.write_text("behalten", encoding="utf-8")
            repair = SelfRepairCoordinator(Path(td) / "config", PROJECT_DIRS)
            report = repair.repair_project(project, _FakeCore)
            self.assertTrue(report.blocking)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "behalten")
            self.assertFalse((project / "datenbanken").exists())

    def test_path_collision_is_reported_and_not_replaced(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "project"
            project.mkdir()
            valid_marker(project)
            collision = project / "logs"
            collision.write_text("nutzerdaten", encoding="utf-8")
            repair = SelfRepairCoordinator(Path(td) / "config", PROJECT_DIRS)
            report = repair.repair_project(project, _FakeCore)
            self.assertTrue(report.blocking)
            self.assertEqual(collision.read_text(encoding="utf-8"), "nutzerdaten")
            self.assertTrue(any(event.code == "PROJECT_PATH_COLLISION" for event in report.events))

    def test_diagnose_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "project"
            project.mkdir()
            valid_marker(project)
            repair = SelfRepairCoordinator(Path(td) / "config", PROJECT_DIRS)
            before = sorted(str(path.relative_to(project)) for path in project.rglob("*"))
            report = repair.diagnose_project(project)
            after = sorted(str(path.relative_to(project)) for path in project.rglob("*"))
            self.assertEqual(before, after)
            self.assertEqual(report.status, "warning")


if __name__ == "__main__":
    unittest.main()
