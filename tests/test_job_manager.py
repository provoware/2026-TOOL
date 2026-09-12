from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from data_core import DataCore, DataValidationError, SCHEMA_VERSION
from job_manager import JobManager


class JobManagerTests(unittest.TestCase):
    def make_core(self, td: str) -> DataCore:
        project = Path(td) / "project"
        project.mkdir()
        return DataCore(project)

    def test_schema_v1_migrates_to_v2_and_keeps_todo(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            core._prepare_dirs()
            conn = sqlite3.connect(str(core.db_path), isolation_level=None)
            try:
                conn.execute("BEGIN IMMEDIATE")
                DataCore._migrate_0_to_1(conn)
                conn.execute("PRAGMA user_version = 1")
                conn.execute(
                    """INSERT INTO todos(title,description,priority,status,created_at,updated_at)
                       VALUES('Bestand','','normal','open','x','x')"""
                )
                conn.execute("COMMIT")
            finally:
                conn.close()
            health = core.ensure_ready()
            self.assertEqual(health.schema_version, SCHEMA_VERSION)
            self.assertEqual(SCHEMA_VERSION, 2)
            self.assertEqual([item["title"] for item in core.list_todos("active")], ["Bestand"])
            backups = list((core.project_root / "sicherungen" / "datenbank").glob("db-*.sqlite3"))
            self.assertGreaterEqual(len(backups), 1)

    def test_job_lifecycle_checkpoint_and_completion(self):
        with tempfile.TemporaryDirectory() as td:
            manager = JobManager(self.make_core(td))
            job = manager.create_job("file-sort", {"source": "/tmp/in"})
            self.assertEqual(job["status"], "queued")
            running = manager.start_job(job["id"])
            self.assertEqual(running["status"], "running")
            checked = manager.checkpoint(
                job["id"], phase="scan", progress_done=3, progress_total=10,
                bytes_done=120, bytes_total=1000, checkpoint={"cursor": "abc"},
            )
            self.assertEqual(checked["checkpoint"], {"cursor": "abc"})
            self.assertEqual(checked["progress_done"], 3)
            completed = manager.complete_job(job["id"], {"files": 10})
            self.assertEqual(completed["status"], "completed")
            self.assertEqual(completed["result"], {"files": 10})
            events = [item["event_type"] for item in manager.list_events(job["id"])]
            self.assertEqual(events, ["created", "started", "checkpoint", "completed"])

    def test_invalid_transition_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            manager = JobManager(self.make_core(td))
            job = manager.create_job("file-sort")
            with self.assertRaises(DataValidationError):
                manager.complete_job(job["id"])
            with self.assertRaises(DataValidationError):
                manager.request_pause(job["id"])
            self.assertEqual(manager.get_job(job["id"])["status"], "queued")

    def test_pause_resume_and_resume_counter(self):
        with tempfile.TemporaryDirectory() as td:
            manager = JobManager(self.make_core(td))
            job = manager.create_job("file-sort")
            manager.start_job(job["id"])
            manager.request_pause(job["id"])
            paused = manager.acknowledge_pause(job["id"])
            self.assertEqual(paused["status"], "paused")
            resumed = manager.resume_job(job["id"])
            self.assertEqual(resumed["status"], "running")
            self.assertEqual(resumed["resume_count"], 1)

    def test_cancel_running_requires_acknowledgement(self):
        with tempfile.TemporaryDirectory() as td:
            manager = JobManager(self.make_core(td))
            job = manager.create_job("file-sort")
            manager.start_job(job["id"])
            cancelling = manager.request_cancel(job["id"])
            self.assertEqual(cancelling["status"], "cancelling")
            self.assertEqual(cancelling["requested_control"], "cancel")
            cancelled = manager.acknowledge_cancel(job["id"])
            self.assertEqual(cancelled["status"], "cancelled")
            self.assertIsNotNone(cancelled["finished_at"])

    def test_startup_recovery_interrupts_active_job_and_resume_keeps_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            first = JobManager(core)
            job = first.create_job("file-sort")
            first.start_job(job["id"])
            first.checkpoint(job["id"], phase="scan", progress_done=7, progress_total=20, checkpoint={"index": 7})
            second = JobManager(DataCore(core.project_root), recover_incomplete=True)
            recovered = second.get_job(job["id"])
            self.assertEqual(recovered["status"], "interrupted")
            self.assertEqual(recovered["checkpoint"], {"index": 7})
            resumed = second.resume_job(job["id"])
            self.assertEqual(resumed["status"], "running")
            self.assertEqual(resumed["resume_count"], 1)

    def test_watchdog_interrupts_stale_heartbeat_only(self):
        with tempfile.TemporaryDirectory() as td:
            core = self.make_core(td)
            manager = JobManager(core)
            stale = manager.create_job("file-sort")
            fresh = manager.create_job("file-sort")
            manager.start_job(stale["id"])
            manager.start_job(fresh["id"])
            now = datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc)
            old = (now - timedelta(minutes=5)).isoformat(timespec="seconds")
            new = (now - timedelta(seconds=5)).isoformat(timespec="seconds")
            with core.transaction() as conn:
                conn.execute("UPDATE jobs SET heartbeat_at=?,updated_at=? WHERE id=?", (old, old, stale["id"]))
                conn.execute("UPDATE jobs SET heartbeat_at=?,updated_at=? WHERE id=?", (new, new, fresh["id"]))
            interrupted = manager.watchdog(stale_after_seconds=30, now=now)
            self.assertEqual(interrupted, [stale["id"]])
            self.assertEqual(manager.get_job(stale["id"])["status"], "interrupted")
            self.assertEqual(manager.get_job(fresh["id"])["status"], "running")

    def test_action_journal_sequence_and_undo_contract(self):
        with tempfile.TemporaryDirectory() as td:
            manager = JobManager(self.make_core(td))
            job = manager.create_job("file-sort")
            first = manager.plan_action(
                job["id"], "move", source_path="/quelle/a.txt", destination_path="/ziel/a.txt",
                reversible=True, before={"size": 12},
            )
            second = manager.plan_action(
                job["id"], "copy", source_path="/quelle/b.txt", destination_path="/ziel/b.txt",
                reversible=False,
            )
            self.assertEqual((first["sequence"], second["sequence"]), (1, 2))
            applied = manager.mark_action_applied(first["id"], after={"size": 12})
            self.assertEqual(applied["status"], "applied")
            candidates = manager.undo_candidates(job["id"])
            self.assertEqual([item["id"] for item in candidates], [first["id"]])
            undone = manager.mark_action_undone(first["id"], after={"restored": True})
            self.assertEqual(undone["status"], "undone")
            self.assertEqual(undone["after"], {"restored": True})
            skipped = manager.mark_action_skipped(second["id"], "Quelldatei während Lauf verschwunden")
            self.assertEqual(skipped["status"], "skipped")
            self.assertIn("verschwunden", skipped["reason"])

    def test_non_reversible_action_cannot_be_marked_undone(self):
        with tempfile.TemporaryDirectory() as td:
            manager = JobManager(self.make_core(td))
            job = manager.create_job("file-sort")
            action = manager.plan_action(
                job["id"], "copy", source_path="/q/a", destination_path="/z/a", reversible=False
            )
            manager.mark_action_applied(action["id"])
            with self.assertRaises(DataValidationError):
                manager.mark_action_undone(action["id"])
            self.assertEqual(manager.get_action(action["id"])["status"], "applied")

    def test_action_planning_rolls_back_if_event_write_fails(self):
        with tempfile.TemporaryDirectory() as td:
            manager = JobManager(self.make_core(td))
            job = manager.create_job("file-sort")
            original = manager._job_event

            def explode(*args, **kwargs):
                raise RuntimeError("absichtlicher Testfehler")

            manager._job_event = explode
            try:
                with self.assertRaises(RuntimeError):
                    manager.plan_action(
                        job["id"], "move", source_path="/q/a", destination_path="/z/a", reversible=True
                    )
            finally:
                manager._job_event = original
            self.assertEqual(manager.list_actions(job["id"]), [])


if __name__ == "__main__":
    unittest.main()
