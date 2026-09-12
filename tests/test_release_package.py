from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("provoware_release_package", ROOT / "scripts/build_release_package.py")
release_package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_package)


class ReleasePackageTests(unittest.TestCase):
    def test_release_package_matches_manifest_commit_and_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "out"
            metadata = release_package.build_release_package(ROOT, output, "HEAD")
            manifest = json.loads((ROOT / "projekt-manifest.json").read_text(encoding="utf-8"))
            version = manifest["app"]["version"]
            expected_name = f"PROVOWARE-HEADQUARTER-v{version}.zip"
            archive_path = output / expected_name
            checksum_path = output / f"{expected_name}.sha256"
            self.assertTrue(archive_path.is_file())
            self.assertTrue(checksum_path.is_file())
            self.assertEqual(metadata["artifact"], expected_name)
            self.assertEqual(metadata["version"], version)
            expected_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(metadata["commit"], expected_commit)
            digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
            self.assertEqual(metadata["sha256"], digest)
            self.assertIn(digest, checksum_path.read_text(encoding="utf-8"))
            with zipfile.ZipFile(archive_path, "r") as archive:
                self.assertIsNone(archive.testzip())
                prefix = f"PROVOWARE-HEADQUARTER-v{version}/"
                names = set(archive.namelist())
                for required in release_package.REQUIRED_PACKAGE_PATHS:
                    self.assertIn(prefix + required, names)
                self.assertFalse(any("/.git/" in name for name in names))


if __name__ == "__main__":
    unittest.main()
