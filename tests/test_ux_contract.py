from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class UxContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "app/static/index.html").read_text(encoding="utf-8")
        cls.app = (ROOT / "app/static/js/app.js").read_text(encoding="utf-8")
        cls.feedback = (ROOT / "app/static/js/feedback.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "app/static/css/feedback.css").read_text(encoding="utf-8")
        cls.standard = (ROOT / "docs/UX_STANDARD.md").read_text(encoding="utf-8")

    def test_global_feedback_surface_is_accessible(self):
        for token in ('id="global-process"', 'id="global-live"', 'aria-live="assertive"', 'id="toast-stack"', 'global-count-skipped', 'Direkt zum Hauptarbeitsbereich'):
            self.assertIn(token, self.html)

    def test_font_scale_and_high_contrast_contract(self):
        self.assertIn('max="200"', self.html)
        self.assertIn('id="contrast-select"', self.html)
        self.assertIn('data-contrast="high"', self.css)
        self.assertIn('min-height:44px', self.css)

    def test_feedback_api_supports_real_process_lifecycle(self):
        for token in ('function begin(', 'function progress(', 'function finish(', 'function skipped(', 'async function busy('):
            self.assertIn(token, self.feedback)
        self.assertIn('Number.isFinite(job.total)', self.feedback)
        self.assertIn('"läuft"', self.feedback)

    def test_beginner_next_step_and_busy_protection_exist(self):
        self.assertIn('id="next-step"', self.html)
        self.assertIn('function updateNextStep()', self.app)
        self.assertIn('Feedback.busy', self.app)
        self.assertIn('aria-current', self.app)

    def test_future_file_workflow_requires_preview_skip_reason_and_recovery(self):
        for token in ('Vorschau/Trockenlauf', 'Grund für jedes Überspringen', 'Undo/Recovery', 'Kein stilles Überschreiben'):
            self.assertIn(token, self.standard)

if __name__ == "__main__":
    unittest.main()
