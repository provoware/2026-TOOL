from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("provoware_server_api_test", ROOT / "app/server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class ApiContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous_config = os.environ.get("PROVOWARE_CONFIG_DIR")
        os.environ["PROVOWARE_CONFIG_DIR"] = str(Path(self.temp.name) / "config")
        self.app = server.AppContext()
        self.http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.http.app = self.app
        host, port = self.http.server_address[:2]
        self.base = f"http://{host}:{port}"
        self.thread = threading.Thread(target=self.http.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.http.shutdown()
        self.thread.join(timeout=2)
        self.http.server_close()
        self.app.clean_shutdown()
        if self.previous_config is None:
            os.environ.pop("PROVOWARE_CONFIG_DIR", None)
        else:
            os.environ["PROVOWARE_CONFIG_DIR"] = self.previous_config
        self.temp.cleanup()

    def request(self, path: str, method: str = "GET", payload: dict | None = None):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            self.base + path,
            method=method,
            data=data,
            headers={"Content-Type": "application/json"} if payload is not None else {},
        )
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def create_project(self):
        status, payload = self.request(
            "/api/project/create",
            "POST",
            {"base_path": str(Path(self.temp.name) / "projects"), "name": "API Projekt"},
        )
        self.assertEqual(status, 201)
        self.assertTrue(payload["project"]["available"])
        return Path(payload["project"]["path"])

    def wait_job(self, job_id: str, wanted: set[str] | None = None, timeout: float = 3.0) -> dict:
        wanted = wanted or {"completed", "failed", "cancelled", "paused", "interrupted"}
        deadline = time.monotonic() + timeout
        last = None
        while time.monotonic() < deadline:
            status, payload = self.request(f"/api/jobs/{job_id}")
            self.assertEqual(status, 200)
            last = payload["job"]
            if last["status"] in wanted:
                return last
            time.sleep(0.03)
        self.fail(f"Job {job_id} erreichte Zielstatus nicht; zuletzt: {last}")

    def test_health_reports_runtime_version(self):
        status, payload = self.request("/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["version"], "0.4.0")

    def test_todo_calendar_archive_restore_contract(self):
        self.create_project()
        status, health = self.request("/api/data/health")
        self.assertEqual(status, 200)
        self.assertEqual(health["integrity"], "ok")
        self.assertEqual(health["journal_mode"], "wal")
        self.assertEqual(health["schema_version"], 2)

        status, created = self.request(
            "/api/todos",
            "POST",
            {"title": "Terminierte Aufgabe", "due_date": "2026-09-18", "due_time": "14:30", "priority": "hoch"},
        )
        self.assertEqual(status, 201)
        todo_id = created["todo"]["id"]

        status, calendar = self.request("/api/calendar?month=2026-09")
        self.assertEqual(status, 200)
        self.assertEqual(calendar["days"]["2026-09-18"][0]["id"], todo_id)

        status, archived = self.request(f"/api/todos/{todo_id}/archive", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(archived["todo"]["status"], "archived")

        status, active = self.request("/api/todos?scope=active")
        self.assertEqual(status, 200)
        self.assertEqual(active["items"], [])
        status, archive = self.request("/api/todos?scope=archive")
        self.assertEqual(status, 200)
        self.assertEqual(len(archive["items"]), 1)
        status, calendar = self.request("/api/calendar?month=2026-09")
        self.assertEqual(status, 200)
        self.assertNotIn("2026-09-18", calendar["days"])

        status, restored = self.request(f"/api/todos/{todo_id}/restore", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(restored["todo"]["status"], "open")
        status, active = self.request("/api/todos?scope=active")
        self.assertEqual(len(active["items"]), 1)

    def test_invalid_due_time_does_not_create_partial_todo(self):
        self.create_project()
        status, payload = self.request("/api/todos", "POST", {"title": "Ungültig", "due_time": "12:00"})
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "VALIDATION")
        self.assertIn("Datum", payload["error"])
        status, active = self.request("/api/todos?scope=all")
        self.assertEqual(status, 200)
        self.assertEqual(active["items"], [])

    def test_job_api_create_control_and_read_only_journal_views(self):
        self.create_project()
        status, created = self.request(
            "/api/jobs", "POST", {"kind": "file-sort", "payload": {"source": "/tmp/in"}}
        )
        self.assertEqual(status, 201)
        job = created["job"]
        job_id = job["id"]
        self.assertEqual(job["status"], "queued")

        status, listed = self.request("/api/jobs?status=queued")
        self.assertEqual(status, 200)
        self.assertEqual([item["id"] for item in listed["items"]], [job_id])

        manager = self.app.job_manager()
        manager.start_job(job_id)
        status, pause = self.request(f"/api/jobs/{job_id}/pause", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(pause["job"]["requested_control"], "pause")
        manager.acknowledge_pause(job_id)

        status, resumed = self.request(f"/api/jobs/{job_id}/resume", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(resumed["job"]["status"], "running")

        action = manager.plan_action(
            job_id,
            "move",
            source_path="/tmp/in/a.txt",
            destination_path="/tmp/out/a.txt",
            reversible=True,
        )
        status, actions = self.request(f"/api/jobs/{job_id}/actions")
        self.assertEqual(status, 200)
        self.assertEqual(actions["items"][0]["id"], action["id"])
        self.assertEqual(actions["items"][0]["status"], "planned")

        status, cancelling = self.request(f"/api/jobs/{job_id}/cancel", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(cancelling["job"]["status"], "cancelling")
        manager.acknowledge_cancel(job_id)

        status, fetched = self.request(f"/api/jobs/{job_id}")
        self.assertEqual(status, 200)
        self.assertEqual(fetched["job"]["status"], "cancelled")
        status, events = self.request(f"/api/jobs/{job_id}/events")
        self.assertEqual(status, 200)
        event_names = [item["event_type"] for item in events["items"]]
        for expected in ("created", "started", "pause-requested", "paused", "resumed", "action-planned", "cancel-requested", "cancelled"):
            self.assertIn(expected, event_names)

    def test_job_api_invalid_kind_returns_stable_validation_code(self):
        self.create_project()
        status, payload = self.request("/api/jobs", "POST", {"kind": "!!!", "payload": {}})
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "VALIDATION")
        status, jobs = self.request("/api/jobs")
        self.assertEqual(status, 200)
        self.assertEqual(jobs["items"], [])

    def test_sorter_api_runs_async_and_returns_summary_and_paged_preview(self):
        self.create_project()
        source = Path(self.temp.name) / "downloads"
        source.mkdir()
        (source / "SUNO_track.mp3").write_bytes(b"audio")
        (source / "bild.png").write_bytes(b"image")
        before = {path.name: path.read_bytes() for path in source.iterdir()}
        rules = [
            {"id": "audio", "name": "Audio", "priority": 10, "category": "Audio", "target_group": "Audio"},
            {"id": "suno", "name": "Suno", "priority": 100, "contains_any": ["suno"], "target_group": "Suno"},
        ]

        status, created = self.request(
            "/api/sorter/scans",
            "POST",
            {"source_path": str(source), "rules": rules, "recursive": False, "include_hidden": False},
        )
        self.assertEqual(status, 202)
        self.assertTrue(created["read_only"])
        job_id = created["job"]["id"]
        final = self.wait_job(job_id)
        self.assertEqual(final["status"], "completed")

        status, summary = self.request(f"/api/sorter/{job_id}/summary")
        self.assertEqual(status, 200)
        self.assertTrue(summary["read_only"])
        self.assertEqual(summary["files"], 2)
        self.assertEqual(summary["decisions"]["matched"], 1)
        self.assertEqual(summary["decisions"]["unmatched"], 1)
        self.assertFalse(summary["worker_active"])

        status, page = self.request(f"/api/sorter/{job_id}/preview?offset=0&limit=1")
        self.assertEqual(status, 200)
        self.assertEqual(page["total"], 2)
        self.assertEqual(len(page["items"]), 1)
        status, matched = self.request(f"/api/sorter/{job_id}/preview?decision=matched&limit=10")
        self.assertEqual(status, 200)
        self.assertEqual(matched["total"], 1)
        self.assertEqual(matched["items"][0]["target_group"], "Suno")
        self.assertEqual(before, {path.name: path.read_bytes() for path in source.iterdir()})

    def test_sorter_api_rejects_symlink_source_with_validation_code(self):
        self.create_project()
        source = Path(self.temp.name) / "real-source"
        source.mkdir()
        link = Path(self.temp.name) / "source-link"
        link.symlink_to(source, target_is_directory=True)
        status, payload = self.request(
            "/api/sorter/scans", "POST", {"source_path": str(link), "rules": []}
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "VALIDATION")
        self.assertIn("Symlink", payload["error"])

    def test_sorter_resume_endpoint_relaunches_worker(self):
        self.create_project()
        source = Path(self.temp.name) / "resume-source"
        source.mkdir()
        for index in range(3):
            (source / f"datei-{index}.txt").write_text("x", encoding="utf-8")

        sorter = self.app.sorter_preview()
        manager = self.app.job_manager()
        job = sorter.create_scan_job(str(source))
        manager.start_job(job["id"])
        manager.request_pause(job["id"])
        paused = manager.acknowledge_pause(job["id"])
        self.assertEqual(paused["status"], "paused")
        self.assertFalse(self.app.active_scan_worker(job["id"]))

        status, resumed = self.request(f"/api/sorter/{job['id']}/resume", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(resumed["job"]["status"], "running")
        final = self.wait_job(job["id"])
        self.assertEqual(final["status"], "completed")
        status, preview = self.request(f"/api/sorter/{job['id']}/preview?limit=10")
        self.assertEqual(status, 200)
        self.assertEqual(preview["total"], 3)

    def test_sorter_preview_filter_validation_is_stable(self):
        self.create_project()
        source = Path(self.temp.name) / "filter-source"
        source.mkdir()
        (source / "x.txt").write_text("x", encoding="utf-8")
        status, created = self.request("/api/sorter/scans", "POST", {"source_path": str(source)})
        self.assertEqual(status, 202)
        job_id = created["job"]["id"]
        self.assertEqual(self.wait_job(job_id)["status"], "completed")
        status, payload = self.request(f"/api/sorter/{job_id}/preview?decision=nicht-erlaubt")
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "VALIDATION")

    def test_self_repair_status_is_read_only_and_run_repairs_missing_standard_dir(self):
        project = self.create_project()
        cache = project / "cache"
        cache.rmdir()

        status, diagnosis = self.request("/api/self-repair/status")
        self.assertEqual(status, 200)
        self.assertEqual(diagnosis["status"], "warning")
        self.assertFalse(cache.exists(), "Diagnose-Endpunkt darf nichts verändern")
        self.assertTrue(any(item["code"] == "PROJECT_DIR_MISSING" for item in diagnosis["events"]))

        status, repaired = self.request("/api/self-repair/run", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(repaired["status"], "repaired")
        self.assertTrue(cache.is_dir())
        self.assertTrue(any(item["code"] == "PROJECT_DIR_RECREATED" for item in repaired["events"]))

        status, diagnosis = self.request("/api/self-repair/status")
        self.assertEqual(status, 200)
        self.assertFalse(diagnosis["blocking"])
        self.assertNotEqual(diagnosis["status"], "warning")

    def test_invalid_project_marker_is_reported_and_not_repaired(self):
        project = self.create_project()
        marker = project / ".provoware" / "project.json"
        marker.write_text("{kaputt", encoding="utf-8")

        status, diagnosis = self.request("/api/self-repair/status")
        self.assertEqual(status, 200)
        self.assertTrue(diagnosis["blocking"])
        self.assertTrue(any(item["code"] == "PROJECT_MARKER_INVALID" for item in diagnosis["events"]))

        before = marker.read_text(encoding="utf-8")
        status, repaired = self.request("/api/self-repair/run", "POST", {})
        self.assertEqual(status, 503)
        self.assertTrue(repaired["blocking"])
        self.assertEqual(marker.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
