#!/usr/bin/env python3
"""Erzeugt und verifiziert das reproduzierbare PROVOWARE-Release-ZIP aus einem Git-Commit."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "projekt-manifest.json"
REQUIRED_PACKAGE_PATHS = (
    "README.md",
    "start.sh",
    "projekt-manifest.json",
    "app/server.py",
    "app/sorter_preview.py",
    "app/static/index.html",
    "app/static/js/sorter.js",
    "app/static/css/sorter.css",
    "scripts/validate_all.sh",
)


def _run(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "Git-Befehl fehlgeschlagen.").strip())
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version(repo_root: Path) -> str:
    manifest = json.loads((repo_root / "projekt-manifest.json").read_text(encoding="utf-8"))
    version = str(manifest.get("app", {}).get("version", "")).strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise RuntimeError("Manifest enthält keine gültige Releaseversion.")
    return version


def build_release_package(repo_root: Path, output_dir: Path, commit: str = "HEAD") -> dict:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    version = _version(repo_root)
    commit_sha = _run(repo_root, "rev-parse", f"{commit}^{{commit}}")
    prefix = f"PROVOWARE-HEADQUARTER-v{version}/"
    filename = f"PROVOWARE-HEADQUARTER-v{version}.zip"
    output_dir.mkdir(parents=True, exist_ok=True)
    final = output_dir / filename
    temp = output_dir / f".{filename}.tmp"
    checksum_file = output_dir / f"{filename}.sha256"
    metadata_file = output_dir / "release-package.json"

    for path in (temp, final, checksum_file, metadata_file):
        path.unlink(missing_ok=True)

    try:
        result = subprocess.run(
            [
                "git", "archive", "--format=zip", f"--prefix={prefix}",
                f"--output={temp}", commit_sha,
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout or "git archive fehlgeschlagen.").strip())

        with zipfile.ZipFile(temp, "r") as archive:
            broken = archive.testzip()
            if broken is not None:
                raise RuntimeError(f"ZIP-Integritätsprüfung fehlgeschlagen bei: {broken}")
            names = set(archive.namelist())
            for required in REQUIRED_PACKAGE_PATHS:
                expected = prefix + required
                if expected not in names:
                    raise RuntimeError(f"Pflichtdatei fehlt im Release-ZIP: {required}")
            if any(name.startswith(prefix + ".git/") or "/.git/" in name for name in names):
                raise RuntimeError("Release-ZIP darf keine .git-Daten enthalten.")
            file_count = sum(1 for info in archive.infolist() if not info.is_dir())

        os.replace(temp, final)
        digest = _sha256(final)
        checksum_file.write_text(f"{digest}  {filename}\n", encoding="utf-8")
        metadata = {
            "artifact": filename,
            "bytes": final.stat().st_size,
            "commit": commit_sha,
            "file_count": file_count,
            "prefix": prefix,
            "sha256": digest,
            "version": version,
            "zip_integrity": "ok",
        }
        metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return metadata
    except Exception:
        temp.unlink(missing_ok=True)
        final.unlink(missing_ok=True)
        checksum_file.unlink(missing_ok=True)
        metadata_file.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="PROVOWARE Release-ZIP reproduzierbar erzeugen")
    parser.add_argument("--repo", default=str(ROOT))
    parser.add_argument("--output", default="release-artifacts")
    parser.add_argument("--commit", default="HEAD")
    args = parser.parse_args()
    repo = Path(args.repo)
    output = Path(args.output)
    if not output.is_absolute():
        output = repo / output
    metadata = build_release_package(repo, output, args.commit)
    print(json.dumps(metadata, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
