from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from build_backup_snapshots import build_snapshots


class BackupSnapshotTests(unittest.TestCase):
    def git(self, repo: Path, *args: str) -> str:
        result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=True)
        return result.stdout.strip()

    def commit(self, repo: Path, message: str) -> str:
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-m", message)
        return self.git(repo, "rev-parse", "HEAD")

    def test_two_exact_verified_snapshots_include_workflows(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            out = root / "out"
            repo.mkdir()
            self.git(repo, "init", "-b", "main")
            self.git(repo, "config", "user.email", "test@example.invalid")
            self.git(repo, "config", "user.name", "Test")

            workflow = repo / ".github/workflows/quality.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("name: gate-v1\n", encoding="utf-8")
            (repo / "version.txt").write_text("v1\n", encoding="utf-8")
            first = self.commit(repo, "v1")

            workflow.write_text("name: gate-v2\n", encoding="utf-8")
            (repo / "version.txt").write_text("v2\n", encoding="utf-8")
            second = self.commit(repo, "v2")

            (repo / "version.txt").write_text("v3\n", encoding="utf-8")
            self.commit(repo, "v3")

            manifest = build_snapshots(repo, second, out)
            self.assertEqual([slot["commit"] for slot in manifest["slots"]], [second, first])
            self.assertEqual(len(manifest["slots"]), 2)

            expectations = {
                "previous-1.zip": ("v2\n", "name: gate-v2\n"),
                "previous-2.zip": ("v1\n", "name: gate-v1\n"),
            }
            for filename, (version, workflow_text) in expectations.items():
                path = out / filename
                self.assertTrue(path.is_file())
                with zipfile.ZipFile(path) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(archive.read("version.txt").decode(), version)
                    self.assertEqual(archive.read(".github/workflows/quality.yml").decode(), workflow_text)
                slot = next(item for item in manifest["slots"] if item["file"] == filename)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), slot["sha256"])

            persisted = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted["strategy"], "verified-git-archive-zip")
            self.assertEqual(len(persisted["slots"]), 2)

    def test_single_initial_commit_is_explicitly_supported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            out = root / "out"
            repo.mkdir()
            self.git(repo, "init", "-b", "main")
            self.git(repo, "config", "user.email", "test@example.invalid")
            self.git(repo, "config", "user.name", "Test")
            (repo / "only.txt").write_text("one", encoding="utf-8")
            first = self.commit(repo, "first")
            manifest = build_snapshots(repo, first, out)
            self.assertEqual(len(manifest["slots"]), 1)
            self.assertTrue((out / "previous-1.zip").is_file())
            self.assertFalse((out / "previous-2.zip").exists())


if __name__ == "__main__":
    unittest.main()
