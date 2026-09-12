from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from data_core import DataCore, DataValidationError, SCHEMA_VERSION


class DataCoreTests(unittest.TestCase):
    def make_core(self, td: str) -> DataCore:
        project = Path(td) / "project"
        project.mkdir()
        return DataCore(project)

    def test_wal_schema_and_health(self):
        with tempfile.TemporaryDirectory() as td:
            health = self.make_core(td).ensure_ready()
            self.assertEqual(health.status, "ok")
            self.assertEqual(health.schema_version, SCHEMA_VERSION)
            self.assertEqual(health.journal_mode, "wal")
            self.assertEqual(health.integrity, "ok")

    def test_todo_archive_restore_and_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            todo = core.create_todo("Arzttermin vorbereiten", due_date="2026-09-14", due_time="09:30", priority="hoch")
            self.assertEqual(len(core.list_todos("active")), 1)
            archived = core.archive_todo(todo["id"])
            self.assertEqual(archived["status"], "archived")
            self.assertEqual(core.list_todos("active"), [])
            self.assertEqual(len(core.list_todos("archive")), 1)
            reopened = DataCore(core.project_root)
            self.assertEqual(len(reopened.list_todos("archive")), 1)
            restored = reopened.restore_todo(todo["id"])
            self.assertEqual(restored["status"], "open")
            self.assertEqual(len(reopened.list_todos("active")), 1)

    def test_calendar_is_projection_of_active_todos(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            archived = core.create_todo("A", due_date="2026-09-12", due_time="08:00")
            core.create_todo("B", due_date="2026-09-12")
            core.create_todo("C", due_date="2026-10-01")
            core.archive_todo(archived["id"])
            month = core.calendar_month("2026-09")
            self.assertEqual([item["title"] for item in month["days"]["2026-09-12"]], ["B"])
            self.assertNotIn("2026-10-01", month["days"])

    def test_invalid_time_without_date_is_rejected_without_partial_row(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            with self.assertRaises(DataValidationError):
                core.create_todo("Ungültig", due_time="12:00")
            self.assertEqual(core.list_todos("all"), [])

    def test_transaction_rolls_back(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            core.ensure_ready()
            with self.assertRaises(RuntimeError):
                with core.transaction() as conn:
                    now = core._now()
                    conn.execute("INSERT INTO todos(title,description,priority,status,created_at,updated_at) VALUES('Rollback','','normal','open',?,?)", (now, now))
                    raise RuntimeError("absichtlich")
            self.assertEqual(core.list_todos("all"), [])

    def test_process_crash_leaves_uncommitted_transaction_out(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            core.ensure_ready()
            script = r'''import os, sqlite3, sys
conn=sqlite3.connect(sys.argv[1], isolation_level=None)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("BEGIN IMMEDIATE")
conn.execute("INSERT INTO todos(title,description,priority,status,created_at,updated_at) VALUES('Crash','','normal','open','x','x')")
os._exit(23)'''
            proc = subprocess.run([sys.executable, "-c", script, str(core.db_path)], check=False)
            self.assertEqual(proc.returncode, 23)
            self.assertEqual(DataCore(core.project_root).list_todos("all"), [])

    def test_verified_backup_and_recovery_from_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            core.create_todo("Bleibt erhalten", due_date="2026-09-20")
            backup = core.create_verified_backup("test")
            self.assertTrue(backup.is_file())
            for suffix in ("-wal", "-shm"):
                Path(str(core.db_path) + suffix).unlink(missing_ok=True)
            core.db_path.write_bytes(b"KEINE SQLITE DATENBANK")
            recovered = DataCore(core.project_root)
            health = recovered.ensure_ready()
            self.assertTrue(health.recovered)
            self.assertEqual(len(recovered.list_todos("active")), 1)
            quarantined = list((core.project_root / "datenbanken").glob("provoware.sqlite3.corrupt-*"))
            self.assertEqual(len(quarantined), 1)
            self.assertTrue((core.project_root / "logs" / "recovery.jsonl").is_file())

    def test_backup_retention_is_two(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            core.create_todo("x")
            for number in range(4):
                core.create_verified_backup(f"b{number}")
            backups = list((core.project_root / "sicherungen" / "datenbank").glob("db-*.sqlite3"))
            self.assertEqual(len(backups), 2)


if __name__ == "__main__":
    unittest.main()
