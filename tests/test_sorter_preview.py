from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from data_core import DataCore, DataValidationError
from job_manager import JobManager
from sorter_preview import SorterPreviewService


class SorterPreviewTests(unittest.TestCase):
    def make_service(self, td: str) -> tuple[SorterPreviewService, Path, DataCore, JobManager]:
        project = Path(td) / "project"
        project.mkdir()
        core = DataCore(project)
        jobs = JobManager(core)
        service = SorterPreviewService(core, jobs)
        source = Path(td) / "source"
        source.mkdir()
        return service, source, core, jobs

    def run_scan(self, service: SorterPreviewService, source: Path, **kwargs) -> dict:
        job = service.create_scan_job(str(source), **kwargs)
        return service.run_scan(job["id"])

    def test_feature_schema_is_idempotent_and_backed_up_before_first_create(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "project"
            project.mkdir()
            core = DataCore(project)
            jobs = JobManager(core)
            before = list(core.backup_dir.glob("db-*.sqlite3"))
            self.assertEqual(before, [])
            first = SorterPreviewService(core, jobs)
            backups = list(core.backup_dir.glob("db-*.sqlite3"))
            self.assertGreaterEqual(len(backups), 1)
            status = first.feature_status()
            self.assertEqual(status["schema_version"], 1)
            self.assertTrue(status["read_only_source"])
            backup_count = len(backups)
            second = SorterPreviewService(core, jobs)
            self.assertEqual(second.feature_status()["schema_version"], 1)
            self.assertEqual(len(list(core.backup_dir.glob("db-*.sqlite3"))), backup_count)

    def test_source_root_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            link = Path(td) / "source-link"
            link.symlink_to(source, target_is_directory=True)
            with self.assertRaises(DataValidationError):
                service.create_scan_job(str(link))

    def test_non_recursive_scan_stays_in_selected_folder(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            (source / "oben.txt").write_text("oben", encoding="utf-8")
            sub = source / "unterordner"
            sub.mkdir()
            (sub / "unten.txt").write_text("unten", encoding="utf-8")
            result = self.run_scan(service, source, recursive=False)
            self.assertEqual(result["status"], "completed")
            preview = service.preview(result["id"], limit=50)
            paths = [item["relative_path"] for item in preview["items"]]
            self.assertEqual(paths, ["oben.txt"])

    def test_recursive_scan_does_not_follow_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            sub = source / "echt"
            sub.mkdir()
            (sub / "song.mp3").write_bytes(b"abc")
            (source / "link-zum-ordner").symlink_to(sub, target_is_directory=True)
            result = self.run_scan(service, source, recursive=True)
            preview = service.preview(result["id"], limit=50)
            by_path = {item["relative_path"]: item for item in preview["items"]}
            self.assertIn("echt/song.mp3", by_path)
            self.assertIn("link-zum-ordner", by_path)
            self.assertEqual(by_path["link-zum-ordner"]["decision"], "skipped")
            self.assertIn("Symlink", by_path["link-zum-ordner"]["skip_reason"])
            self.assertEqual(sum(1 for path in by_path if path.endswith("song.mp3")), 1)

    def test_hidden_and_cache_content_is_skipped_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            (source / ".geheim.txt").write_text("x", encoding="utf-8")
            cache = source / ".cache"
            cache.mkdir()
            (cache / "cache.txt").write_text("x", encoding="utf-8")
            (source / "sichtbar.pdf").write_bytes(b"pdf")
            result = self.run_scan(service, source, recursive=True)
            preview = service.preview(result["id"], limit=50)
            by_path = {item["relative_path"]: item for item in preview["items"]}
            self.assertEqual(by_path[".geheim.txt"]["decision"], "skipped")
            self.assertEqual(by_path[".cache"]["decision"], "skipped")
            self.assertNotIn(".cache/cache.txt", by_path)
            self.assertEqual(by_path["sichtbar.pdf"]["category"], "Dokumente")

    def test_categories_are_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            service, _, _, _ = self.make_service(td)
            cases = {
                "bild.JPG": "Bilder",
                "clip.mkv": "Video",
                "song.FLAC": "Audio",
                "brief.pdf": "Dokumente",
                "paket.7z": "Archive",
                "script.py": "Text / Code",
                "ohne.xyzabc": "Sonstige",
            }
            for name, expected in cases.items():
                with self.subTest(name=name):
                    _, category = service.classify_extension(name)
                    self.assertEqual(category, expected)

    def test_higher_priority_word_rule_overrides_general_audio_rule(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            (source / "SUNO_neuer_song.mp3").write_bytes(b"abc")
            rules = [
                {"id": "audio", "name": "Alle Audios", "priority": 10, "category": "Audio", "target_group": "Audio"},
                {"id": "suno", "name": "Suno", "priority": 100, "contains_any": ["suno"], "target_group": "Suno"},
            ]
            result = self.run_scan(service, source, rules=rules)
            item = service.preview(result["id"])["items"][0]
            self.assertEqual(item["decision"], "matched")
            self.assertEqual(item["target_group"], "Suno")
            self.assertEqual([match["id"] for match in item["matches"]], ["suno", "audio"])

    def test_equal_priority_different_targets_create_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            (source / "suno.mp3").write_bytes(b"abc")
            rules = [
                {"id": "a", "priority": 50, "category": "Audio", "target_group": "Audio"},
                {"id": "b", "priority": 50, "contains_any": ["suno"], "target_group": "Suno"},
            ]
            result = self.run_scan(service, source, rules=rules)
            item = service.preview(result["id"])["items"][0]
            self.assertEqual(item["decision"], "conflict")
            self.assertEqual(item["target_group"], "")
            self.assertEqual(len(item["matches"]), 2)

    def test_disappearing_entry_is_skipped_instead_of_aborting_scan(self):
        class FakeStatEntry:
            name = "weg.txt"
            path = ""

            def is_symlink(self):
                return False

            def is_dir(self, follow_symlinks=False):
                return False

            def is_file(self, follow_symlinks=False):
                return True

            def stat(self, follow_symlinks=False):
                raise FileNotFoundError("weg")

        class FakeScan:
            def __init__(self, entry):
                self.entry = entry

            def __enter__(self):
                return iter([self.entry])

            def __exit__(self, exc_type, exc, tb):
                return False

        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            entry = FakeStatEntry()
            entry.path = str(source / entry.name)
            job = service.create_scan_job(str(source))
            with mock.patch("sorter_preview.os.scandir", return_value=FakeScan(entry)):
                result = service.run_scan(job["id"])
            self.assertEqual(result["status"], "completed")
            item = service.preview(result["id"])["items"][0]
            self.assertEqual(item["decision"], "skipped")
            self.assertIn("nicht verfügbar", item["skip_reason"])

    def test_unreadable_subdirectory_is_recorded_and_rest_continues(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            blocked = source / "blockiert"
            blocked.mkdir()
            (source / "ok.txt").write_text("ok", encoding="utf-8")
            original_scandir = os.scandir

            def guarded_scandir(path):
                if Path(path) == blocked:
                    raise PermissionError("absichtlich")
                return original_scandir(path)

            job = service.create_scan_job(str(source), recursive=True)
            with mock.patch("sorter_preview.os.scandir", side_effect=guarded_scandir):
                result = service.run_scan(job["id"])
            self.assertEqual(result["status"], "completed")
            preview = service.preview(result["id"], limit=50)
            by_path = {item["relative_path"]: item for item in preview["items"]}
            self.assertIn("ok.txt", by_path)
            self.assertIn("blockiert", by_path)
            self.assertEqual(by_path["blockiert"]["decision"], "skipped")
            self.assertIn("nicht lesbar", by_path["blockiert"]["skip_reason"])

    def test_preview_is_persistent_paginated_and_summary_matches(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, core, jobs = self.make_service(td)
            for index in range(5):
                (source / f"datei-{index}.txt").write_text("x" * (index + 1), encoding="utf-8")
            result = self.run_scan(service, source)
            first = service.preview(result["id"], offset=0, limit=2)
            second = service.preview(result["id"], offset=2, limit=2)
            self.assertEqual(first["total"], 5)
            self.assertEqual(len(first["items"]), 2)
            self.assertEqual(len(second["items"]), 2)
            fresh = SorterPreviewService(DataCore(core.project_root), JobManager(DataCore(core.project_root), recover_incomplete=False))
            self.assertEqual(fresh.preview(result["id"], limit=10)["total"], 5)
            summary = fresh.scan_summary(result["id"])
            self.assertEqual(summary["files"], 5)
            self.assertEqual(summary["decisions"]["unmatched"], 5)
            final_job = jobs.get_job(result["id"])
            self.assertEqual(final_job["progress_done"], 5)
            self.assertEqual(final_job["progress_total"], 5)

    def test_scan_does_not_modify_source_files(self):
        with tempfile.TemporaryDirectory() as td:
            service, source, _, _ = self.make_service(td)
            paths = [source / "a.txt", source / "b.mp3"]
            paths[0].write_text("alpha", encoding="utf-8")
            paths[1].write_bytes(b"beta")
            before = {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
            result = self.run_scan(service, source)
            self.assertEqual(result["status"], "completed")
            after = {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
            self.assertEqual(before, after)
            self.assertEqual(sorted(path.name for path in source.iterdir()), ["a.txt", "b.mp3"])


if __name__ == "__main__":
    unittest.main()
