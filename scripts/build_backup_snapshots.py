#!/usr/bin/env python3
"""Erzeugt zwei verifizierte ZIP-Snapshots vorheriger Git-Stände."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import zipfile


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} fehlgeschlagen")
    return result.stdout.strip()


def require_commit(repo: Path, ref: str) -> str:
    if not ref or set(ref) == {"0"}:
        raise ValueError("Kein gültiger Vorgänger-Commit angegeben.")
    sha = run_git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    return sha


def first_parent(repo: Path, commit: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", f"{commit}^1"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_zip(path: Path) -> tuple[int, int]:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Backup-ZIP fehlt oder ist leer: {path}")
    with zipfile.ZipFile(path, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP-Prüfung fehlgeschlagen bei: {bad}")
        members = [item for item in archive.infolist() if not item.is_dir()]
        if not members:
            raise RuntimeError("Backup-ZIP enthält keine Dateien.")
        unpacked_bytes = sum(item.file_size for item in members)
    return len(members), unpacked_bytes


def archive_commit(repo: Path, commit: str, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.unlink(missing_ok=True)
    subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=zip", f"--output={destination}", commit],
        check=True,
    )
    files, unpacked_bytes = verify_zip(destination)
    return {
        "commit": commit,
        "file": destination.name,
        "sha256": sha256(destination),
        "zip_bytes": destination.stat().st_size,
        "files": files,
        "unpacked_bytes": unpacked_bytes,
    }


def build_snapshots(repo: Path, before: str, output_dir: Path) -> dict:
    repo = repo.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("previous-*.zip"):
        stale.unlink()

    previous_1 = require_commit(repo, before)
    previous_2 = first_parent(repo, previous_1)

    slots: list[dict] = []
    first = archive_commit(repo, previous_1, output_dir / "previous-1.zip")
    first["slot"] = "previous-1"
    slots.append(first)

    if previous_2:
        second = archive_commit(repo, previous_2, output_dir / "previous-2.zip")
        second["slot"] = "previous-2"
        slots.append(second)

    manifest = {
        "schema_version": 1,
        "strategy": "verified-git-archive-zip",
        "source": "main-first-parent-history",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "slots": slots,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--before", required=True, help="github.event.before bzw. letzter Hauptstand vor dem neuen Push")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = build_snapshots(Path(args.repo), args.before, Path(args.out))
    for slot in manifest["slots"]:
        print(f"OK   {slot['slot']} -> {slot['commit']} | {slot['files']} Dateien | SHA-256 {slot['sha256']}")
    if len(manifest["slots"]) < 2:
        print("HINWEIS: Ein zweiter Vorgänger ist in der Git-Historie noch nicht vorhanden.")
    print("OK   Backup-Manifest erzeugt und ZIP-Integrität geprüft.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
