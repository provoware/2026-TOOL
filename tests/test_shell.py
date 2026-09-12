import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('provoware_server',ROOT/'app/server.py'); server=importlib.util.module_from_spec(spec); spec.loader.exec_module(server)

class ShellTests(unittest.TestCase):
    def test_manifest_and_areas(self):
        m=json.loads((ROOT/'projekt-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(m['app']['version'],'0.2.2'); self.assertEqual(m['iteration']['stage'],'2.2'); self.assertEqual(m['ui']['areas'],list('ABCDEFGHIJKLMN')); self.assertEqual(len(m['ui']['themes']),5); self.assertFalse(m['quality']['manual_user_acceptance_required']); self.assertEqual(m['data']['engine'],'sqlite3'); self.assertEqual(m['data']['journal_mode'],'WAL'); self.assertEqual(m['data']['calendar_source'],'todos'); self.assertTrue(m['quality']['self_repair_guarded']); self.assertEqual(m['quality']['risk_model'],'R0-R4'); self.assertEqual(server.APP_VERSION,'0.2.2')
    def test_html_contains_every_area_and_data_ui(self):
        html=(ROOT/'app/static/index.html').read_text(encoding='utf-8')
        for area in 'ABCDEFGHIJKLMN': self.assertIn(f'data-area="{area}"',html)
        for expected in ('id="startup-bar"','id="project-dialog"','id="todo-form"','id="calendar-prev"','/static/js/data.js','/static/js/feedback.js'): self.assertIn(expected,html)
    def test_theme_css_contains_all_themes(self):
        css=(ROOT/'app/static/css/design.css').read_text(encoding='utf-8')
        for theme in ('carbon','violet','steel','nordic','terminal'): self.assertIn(f'data-theme="{theme}"',css)
    def test_project_creation_is_isolated_persistent_and_has_database(self):
        with tempfile.TemporaryDirectory() as td:
            config=Path(td)/'config'; base=Path(td)/'projects'; store=server.ProjectStore(config); project=store.create_project(str(base),'Test Projekt'); self.assertTrue(project['available']); target=Path(project['path']); self.assertTrue((target/'.provoware/project.json').is_file())
            for dirname in server.PROJECT_DIRS: self.assertTrue((target/dirname).is_dir())
            self.assertTrue((target/'datenbanken/provoware.sqlite3').is_file()); self.assertEqual(server.ProjectStore(config).bootstrap()['project']['path'],str(target))
    def test_nonempty_foreign_folder_is_not_adopted(self):
        with tempfile.TemporaryDirectory() as td:
            store=server.ProjectStore(Path(td)/'config'); base=Path(td)/'projects'; target=base/'Fremd'; target.mkdir(parents=True); (target/'fremd.txt').write_text('x',encoding='utf-8')
            with self.assertRaises(FileExistsError): store.create_project(str(base),'Fremd')
            self.assertEqual((target/'fremd.txt').read_text(encoding='utf-8'),'x')
    def test_invalid_marker_disables_active_project_without_erasing_configured_path(self):
        with tempfile.TemporaryDirectory() as td:
            config=Path(td)/'config'; store=server.ProjectStore(config); project=store.create_project(str(Path(td)/'projects'),'P'); target=Path(project['path']); (target/'.provoware/project.json').write_text('{kaputt',encoding='utf-8'); reloaded=server.ProjectStore(config); self.assertEqual(reloaded.configured_project_path(),target); self.assertIsNone(reloaded.active_project_path()); self.assertFalse(reloaded.bootstrap()['project']['available']); self.assertFalse(reloaded.bootstrap()['project']['marker_valid'])
    def test_quick_save_appends(self):
        with tempfile.TemporaryDirectory() as td:
            store=server.ProjectStore(Path(td)/'config'); store.create_project(str(Path(td)/'projects'),'P'); path=store.quick_save('Ideen','eins'); store.quick_save('Ideen','zwei'); text=path.read_text(encoding='utf-8'); self.assertIn('eins',text); self.assertIn('zwei',text); self.assertLess(text.index('eins'),text.index('zwei'))
    def test_help_is_machine_readable_and_documents_recovery(self):
        data=json.loads((ROOT/'app/static/help.json').read_text(encoding='utf-8')); self.assertGreaterEqual(len(data['sections']),9); joined=' '.join(s['text'] for s in data['sections']); self.assertIn('Self-Repair',joined); self.assertIn('200',joined); self.assertIn('Überspr',joined)

if __name__=='__main__': unittest.main()
