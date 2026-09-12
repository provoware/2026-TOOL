from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BackupWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / ".github/workflows/backup.yml").read_text(encoding="utf-8")

    def test_rotation_uses_github_ref_api_not_force_git_push(self):
        self.assertIn("gh api", self.workflow)
        self.assertIn("git/refs/heads/${name}", self.workflow)
        self.assertIn("force=true", self.workflow)
        self.assertNotIn("git push --force", self.workflow)

    def test_two_previous_refs_are_explicit_and_verified(self):
        self.assertIn('backup/previous-1', self.workflow)
        self.assertIn('backup/previous-2', self.workflow)
        self.assertIn('verify_ref "backup/previous-1"', self.workflow)
        self.assertIn('verify_ref "backup/previous-2"', self.workflow)
        self.assertIn("git ls-remote", self.workflow)

    def test_missing_ref_has_controlled_create_fallback(self):
        self.assertIn("--method PATCH", self.workflow)
        self.assertIn("--method POST", self.workflow)
        self.assertIn('ref="refs/heads/${name}"', self.workflow)


if __name__ == "__main__":
    unittest.main()
