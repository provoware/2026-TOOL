import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("provoware_server", ROOT / "app/server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class ShellTests(unittest.TestCase):
    def test_manifest_and_areas(self):
        manifest = json.loads((ROOT / "projekt-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["app"]["version"], "0.4.0")
        self.assertEqual(server.APP_VERSION, manifest["app"]["version"])
        self.assertEqual(manifest["app"]["status"], "iteration-4-sorter-preview")
        self.assertEqual(manifest["iteration"]["number"], 4)
        self.assertEqual(manifest["iteration"]["stage"], "4.0")
        self.assertEqual(manifest["iteration"]["release"], "0.4.0")
        self.assertEqual(manifest["iteration"]["scope"], "sorter-preview")
        self.assertEqual(manifest["iteration"]["risk"], "R3")
        self.assertEqual(manifest["development"]["active_iteration"], 4)
        self.assertEqual(manifest["development"]["current_version"], "0.4.0")
        self.assertEqual(manifest["development"]["stage"], "sorter-preview")
        self.assertEqual(manifest["development"]["risk"], "R3")
        self.assertEqual(manifest["development"]["release_status"], "release-candidate")
        self.assertEqual(manifest["ui"]["areas"], list("ABCDEFGHIJKLMN"))
        self.assertEqual(len(manifest["ui"]["themes"]), 5)
        self.assertFalse(manifest["quality"]["manual_user_acceptance_required"])
        self.assertEqual(manifest["data"]["engine"], "sqlite3")
        self.assertEqual(manifest["data"]["schema_version"], 2)
        self.assertEqual(manifest["data"]["journal_mode"], "WAL")
        self.assertEqual(manifest["data"]["calendar_source"], "todos")
        self.assertTrue(manifest["quality"]["self_repair_guarded"])
        self.assertEqual(manifest["quality"]["risk_model"], "R0-R4")
        self.assertTrue(manifest["jobs"]["checkpoint_resume"])
        self.assertTrue(manifest["jobs"]["automatic_watchdog"])
        self.assertFalse(manifest["file_actions"]["destructive_delete_supported"])
        sorter = manifest["sorter_preview"]
        self.assertTrue(sorter["source_read_only"])
        self.assertFalse(sorter["recursive_default"])
        self.assertFalse(sorter["include_hidden_default"])
        self.assertFalse(sorter["follow_symlinks"])
        self.assertEqual(sorter["mutating_operations"], [])
        self.assertEqual(sorter["test"], "tests/test_sorter_preview.py")

    def test_html_contains_every_area_and_data_ui(self):
        html = (ROOT / "app/static/index.html").read_text(encoding="utf-8")
        for area in "ABCDEFGHIJKLMN":
            self.assertIn(f'data-area="{area}"', html)
        for expected in (
            'id="startup-bar"', 'id="project-dialog"', 'id="todo-form"',
            'id="calendar-prev"', '/static/js/data.js', '/static/js/feedback.js'
        ):
            self.assertIn(expected, html)

    def test_theme_css_contains_all_themes(self):
        css = (ROOT / "app/static/css/design.css").read_text(encoding="utf-8")
        for theme in ("carbon", "violet", "steel", "nordic", "terminal"):
            self.assertIn(f'data-theme="{theme}"', css)

    def test_project_creation_is_isolated_persistent_and_has_database(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "config"
            base = Path(td) / "projects"
            store = server.ProjectStore(config)
            project = store.create_project(str(base), "Test Projekt")
            self.assertTrue(project["available"])
            target = Path(project["path"])
            self.assertTrue((target / ".provoware/project.json").is_file())
            for dirname in server.PROJECT_DIRS:
                self.assertTrue((target / dirname).is_dir())
            self.assertTrue((target / "datenbanken/provoware.sqlite3").is_file())
            self.assertEqual(server.ProjectStore(config).bootstrap()["project"]["path"], str(target))

    def test_nonempty_foreign_folder_is_not_adopted(self):
        with tempfile.TemporaryDirectory() as td:
            store = server.ProjectStore(Path(td) / "config")
            base = Path(td) / "projects"
            target = base / "Fremd"
            target.mkdir(parents=True)
            (target / "fremd.txt").write_text("x", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                store.create_project(str(base), "Fremd")
            self.assertEqual((target / "fremd.txt").read_text(encoding="utf-8"), "x")

    def test_invalid_marker_disables_active_project_without_erasing_configured_path(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "config"
            store = server.ProjectStore(config)
            project = store.create_project(str(Path(td) / "projects"), "P")
            target = Path(project["path"])
            marker = target / ".provoware/project.json"
            marker.write_text("{kaputt", encoding="utf-8")
            reloaded = server.ProjectStore(config)
            self.assertEqual(reloaded.configured_project_path(), target)
            self.assertIsNone(reloaded.active_project_path())
            self.assertFalse(reloaded.bootstrap()["project"]["available"])
            self.assertFalse(reloaded.bootstrap()["project"]["marker_valid"])

    def test_quick_save_appends(self):
        with tempfile.TemporaryDirectory() as td:
            store = server.ProjectStore(Path(td) / "config")
            store.create_project(str(Path(td) / "projects"), "P")
            path = store.quick_save("Ideen", "eins")
            store.quick_save("Ideen", "zwei")
            text = path.read_text(encoding="utf-8")
            self.assertIn("eins", text)
            self.assertIn("zwei", text)
            self.assertLess(text.index("eins"), text.index("zwei"))

    def test_help_is_machine_readable_and_documents_recovery(self):
        help_data = json.loads((ROOT / "app/static/help.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(help_data["sections"]), 9)
        joined = " ".join(section["text"] for section in help_data["sections"])
        for token in ("WAL", "Archiv", "Sicherung", "Self-Repair", "Prozessleiste"):
            self.assertIn(token, joined)


if __name__ == "__main__":
    unittest.main()
