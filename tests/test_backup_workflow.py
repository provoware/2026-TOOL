from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BackupWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / ".github/workflows/backup.yml").read_text(encoding="utf-8")

    def test_rotation_avoids_historical_ref_rewrites(self):
        self.assertNotIn("gh api", self.workflow)
        self.assertNotIn("git push --force", self.workflow)
        self.assertNotIn("refs/heads/backup/previous-1", self.workflow)
        self.assertIn("backup/snapshots", self.workflow)

    def test_two_verified_snapshot_slots_are_published(self):
        self.assertIn("build_backup_snapshots.py", self.workflow)
        self.assertIn("version-backups", self.workflow)
        self.assertIn("backup-manifest.json", self.workflow)
        self.assertIn("sha256", self.workflow)
        self.assertIn("BACKUP_BEFORE", self.workflow)

    def test_snapshot_branch_changes_are_path_limited(self):
        self.assertIn("git diff --exit-code -- .github/workflows", self.workflow)
        self.assertIn("grep -v '^version-backups/'", self.workflow)
        self.assertIn("BLOCKIERT: unerwartete Änderungen außerhalb version-backups/", self.workflow)

    def test_snapshot_storage_branch_must_exist_explicitly(self):
        self.assertIn("git ls-remote --exit-code --heads origin refs/heads/backup/snapshots", self.workflow)
        self.assertIn("wird bewusst einmalig außerhalb des Actions-Tokens angelegt", self.workflow)


if __name__ == "__main__":
    unittest.main()
