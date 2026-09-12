from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BackupWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / ".github/workflows/backup.yml").read_text(encoding="utf-8")

    def test_workflow_requires_only_read_access(self):
        self.assertIn("contents: read", self.workflow)
        self.assertNotIn("contents: write", self.workflow)
        self.assertNotIn("git push --force", self.workflow)
        self.assertNotIn("gh api", self.workflow)

    def test_exact_two_previous_source_archives_are_created(self):
        self.assertIn("previous-1.tar.gz", self.workflow)
        self.assertIn("previous-2.tar.gz", self.workflow)
        self.assertIn('git archive --format=tar.gz', self.workflow)
        self.assertIn('PREV2="$(git rev-parse "$BEFORE^1"', self.workflow)

    def test_git_bundle_and_checksums_are_verified(self):
        self.assertIn("git bundle create", self.workflow)
        self.assertIn("git bundle verify", self.workflow)
        self.assertIn("sha256sum", self.workflow)
        self.assertIn("sha256sum -c SHA256SUMS", self.workflow)
        self.assertIn("tar -tzf backup-artifact/previous-1.tar.gz", self.workflow)
        self.assertIn("tar -tzf backup-artifact/previous-2.tar.gz", self.workflow)

    def test_verified_backup_is_uploaded_as_artifact(self):
        self.assertIn("actions/upload-artifact@v4", self.workflow)
        self.assertIn("if-no-files-found: error", self.workflow)
        self.assertIn("retention-days: 30", self.workflow)
        self.assertIn("backup-artifact/", self.workflow)


if __name__ == "__main__":
    unittest.main()
