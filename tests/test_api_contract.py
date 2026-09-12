from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
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

    def test_todo_calendar_archive_restore_contract(self):
        self.create_project()
        status, health = self.request("/api/data/health")
        self.assertEqual(status, 200)
        self.assertEqual(health["integrity"], "ok")
        self.assertEqual(health["journal_mode"], "wal")

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
        self.assertIn("Datum", payload["error"])
        status, active = self.request("/api/todos?scope=all")
        self.assertEqual(status, 200)
        self.assertEqual(active["items"], [])


if __name__ == "__main__":
    unittest.main()
