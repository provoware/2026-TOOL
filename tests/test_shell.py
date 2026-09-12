import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("provoware_server",ROOT/"app/server.py")
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
class ShellTests(unittest.TestCase):
    def test_manifest_and_areas(self):
        m=json.loads((ROOT/"projekt-manifest.json").read_text(encoding="utf-8"));self.assertEqual(m["ui"]["areas"],list("ABCDEFGHIJKLMN"));self.assertEqual(len(m["ui"]["themes"]),5);self.assertFalse(m["quality"]["manual_user_acceptance_required"])
    def test_html_contains_every_area(self):
        html=(ROOT/"app/static/index.html").read_text(encoding="utf-8")
        for area in "ABCDEFGHIJKLMN": self.assertIn(f'data-area="{area}"',html)
        self.assertIn('id="startup-bar"',html);self.assertIn('id="project-dialog"',html)
    def test_theme_css_contains_all_themes(self):
        css=(ROOT/"app/static/css/design.css").read_text(encoding="utf-8")
        for theme in ("carbon","violet","steel","nordic","terminal"): self.assertIn(f'data-theme="{theme}"',css)
    def test_project_creation_is_isolated_and_persistent(self):
        with tempfile.TemporaryDirectory() as td:
            config=Path(td)/"config";base=Path(td)/"projects";store=server.ProjectStore(config);project=store.create_project(str(base),"Test Projekt");self.assertTrue(project["available"]);target=Path(project["path"]);self.assertTrue((target/".provoware/project.json").is_file())
            for d in server.PROJECT_DIRS: self.assertTrue((target/d).is_dir())
            self.assertEqual(server.ProjectStore(config).bootstrap()["project"]["path"],str(target))
    def test_nonempty_foreign_folder_is_not_adopted(self):
        with tempfile.TemporaryDirectory() as td:
            store=server.ProjectStore(Path(td)/"config");base=Path(td)/"projects";target=base/"Fremd";target.mkdir(parents=True);(target/"fremd.txt").write_text("x")
            with self.assertRaises(FileExistsError): store.create_project(str(base),"Fremd")
            self.assertEqual((target/"fremd.txt").read_text(),"x")
    def test_quick_save_appends(self):
        with tempfile.TemporaryDirectory() as td:
            store=server.ProjectStore(Path(td)/"config");store.create_project(str(Path(td)/"projects"),"P");path=store.quick_save("Ideen","eins");store.quick_save("Ideen","zwei");text=path.read_text(encoding="utf-8");self.assertIn("eins",text);self.assertIn("zwei",text);self.assertLess(text.index("eins"),text.index("zwei"))
    def test_help_is_machine_readable(self):
        h=json.loads((ROOT/"app/static/help.json").read_text(encoding="utf-8"));self.assertGreaterEqual(len(h["sections"]),5)
if __name__=="__main__": unittest.main()
