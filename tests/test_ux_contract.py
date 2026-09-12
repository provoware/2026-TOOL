import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UxContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "app/static/index.html").read_text(encoding="utf-8")
        cls.app_js = (ROOT / "app/static/js/app.js").read_text(encoding="utf-8")
        cls.data_js = (ROOT / "app/static/js/data.js").read_text(encoding="utf-8")
        cls.feedback_js = (ROOT / "app/static/js/feedback.js").read_text(encoding="utf-8")
        cls.feedback_css = (ROOT / "app/static/css/feedback.css").read_text(encoding="utf-8")

    def test_global_process_feedback_contract(self):
        for token in (
            'id="process-center"', 'id="process-label"', 'id="process-detail"',
            'id="process-progress"', 'id="warning-count"', 'id="error-count"',
            'id="toast-region"', 'aria-live="polite"',
        ):
            self.assertIn(token, self.html)
        self.assertIn("function begin", self.feedback_js)
        self.assertIn("function record", self.feedback_js)
        self.assertIn("aria-busy", self.feedback_js)

    def test_keyboard_and_zoom_contract(self):
        self.assertIn('min="100" max="200"', self.html)
        self.assertIn("Math.max(100, Math.min(200", self.app_js)
        self.assertIn('event.key === "0"', self.app_js)
        self.assertIn('event.key === "-"', self.app_js)
        self.assertIn("event.ctrlKey", self.app_js)
        self.assertIn("passive: false", self.app_js)

    def test_skip_link_focus_and_large_targets(self):
        self.assertIn('class="skip-link" href="#main-content"', self.html)
        self.assertIn('id="main-content"', self.html)
        self.assertIn('tabindex="-1"', self.html)
        self.assertIn("min-height:44px", self.feedback_css)
        self.assertIn("prefers-reduced-motion", self.feedback_css)

    def test_busy_protection_for_user_actions(self):
        self.assertIn('button.setAttribute("aria-busy", "true")', self.app_js)
        self.assertIn('button.setAttribute("aria-busy", "true")', self.data_js)
        self.assertIn("button.disabled = true", self.app_js)
        self.assertIn("button.disabled = true", self.data_js)

    def test_help_explains_feedback_model(self):
        help_data = json.loads((ROOT / "app/static/help.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(help_data.get("version", 0), 4)
        titles = {section["title"] for section in help_data["sections"]}
        self.assertIn("Prozessleiste – Was passiert gerade?", titles)
        self.assertIn("Hinweise und Fehler", titles)
        self.assertIn("Zoom und Tastatur", titles)

    def test_ux_standard_is_documented(self):
        standard = (ROOT / "docs/UX_STANDARD.md").read_text(encoding="utf-8")
        for token in ("Was passiert gerade?", "BEREIT", "ARBEITET", "ERFOLG", "HINWEIS", "FEHLER", "100–200 %", "Layoutstabilität"):
            self.assertIn(token, standard)


if __name__ == "__main__":
    unittest.main()
