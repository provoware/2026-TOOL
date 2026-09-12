#!/usr/bin/env python3
"""Deterministische, risikobasierte Gates für die PROVOWARE-Subagenten."""
from __future__ import annotations

import argparse
import subprocess

MODES = ("analyse", "risk", "rootcause", "plan", "regression", "compliance", "release")
RISK_ORDER = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4}

R3_PATHS = (
    "app/data_core.py",
    "app/project_store.py",
    "app/self_repair.py",
    "app/server.py",
    ".github/workflows/",
    "scripts/build_backup_snapshots.py",
    "scripts/agent_gate.py",
    "scripts/validate_",
    "AGENTS.md",
    ".agents/",
)
R1_PREFIXES = ("app/static/",)
R2_PREFIXES = ("app/", "scripts/")
PROTECTED_DELETE_PATHS = (
    "app/", "scripts/", "tests/", ".github/", ".agents/",
    "AGENTS.md", "projekt-manifest.json",
)
AGENT_PATHS = ("AGENTS.md", ".agents/", ".github/workflows/agents.yml", "scripts/agent_gate.py", "scripts/validate_agents.py")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def changed(base: str | None, head: str) -> list[str]:
    if not base or set(base) == {"0"}:
        cmd = ["git", "show", "--pretty=", "--name-only", head]
    else:
        cmd = ["git", "diff", "--name-only", base, head]
    result = _run(cmd)
    if result.returncode:
        result = subprocess.run(["git", "show", "--pretty=", "--name-only", head], text=True, capture_output=True, check=True)
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def deleted(base: str | None, head: str) -> list[str]:
    if not base or set(base) == {"0"}:
        return []
    result = _run(["git", "diff", "--diff-filter=D", "--name-only", base, head])
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()}) if result.returncode == 0 else []


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    return any(path == item or path.startswith(item) for item in patterns)


def risk_level(files: list[str], removed: list[str]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    level = "R0"
    for path in files:
        if _matches(path, R1_PREFIXES):
            if RISK_ORDER[level] < 1:
                level = "R1"
            reasons.append("Darstellung/UI")
        elif _matches(path, R2_PREFIXES):
            if RISK_ORDER[level] < 2:
                level = "R2"
            reasons.append("Fachlogik/API")
        if _matches(path, R3_PATHS):
            level = "R3"
            reasons.append(f"Kern-/Qualitätsgrenze: {path}")
    if any(_matches(path, PROTECTED_DELETE_PATHS) for path in removed):
        level = "R4"
        reasons.append("Produktiv-, Test- oder Qualitätsvertrag gelöscht")
    return level, reasons


def requires_regression(risk: str, code_changed: bool) -> bool:
    """R1–R3-Verhaltensänderungen brauchen explizite Regressionsevidenz."""
    return code_changed and risk in {"R1", "R2", "R3"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args()

    files = changed(args.base, args.head)
    removed = deleted(args.base, args.head)
    risk, reasons = risk_level(files, removed)
    code = [f for f in files if f.startswith(("app/", "scripts/", ".github/workflows/"))]
    tests = [f for f in files if f.startswith("tests/")]
    plan_docs = [f for f in files if f == "TODO.md" or f.startswith("docs/iterationen/")]
    agent_changes = [f for f in files if _matches(f, AGENT_PATHS)]

    print(f"# {args.mode} Gate")
    print(f"Geänderte Dateien: {len(files)}")
    print(f"Risikoklasse: {risk}")
    print("Risikogründe: " + (", ".join(dict.fromkeys(reasons)) if reasons else "keine Laufzeitänderung erkannt"))
    if removed:
        print("Gelöscht: " + ", ".join(removed))

    if args.mode == "analyse":
        print("Ergebnis: read-only Analyse abgeschlossen.")
        return

    if args.mode == "risk":
        if risk == "R4":
            print("BLOCKIERT: R4 ist standardmäßig nicht automatisch freigabefähig.")
            raise SystemExit(1)
        print(f"Ergebnis: {risk} erkannt; erforderliche Prüfintensität festgelegt.")
        return

    if args.mode == "rootcause":
        relevant = risk in {"R3", "R4"} or any("test" in f.lower() for f in files)
        print("Trigger: aktiv – Root-Cause-Prüfung erforderlich." if relevant else "Trigger: nicht erforderlich für diesen Diff.")
        return

    if args.mode == "plan":
        if code and not plan_docs:
            print("BLOCKIERT: Laufzeit-/Workflowänderung ohne aktualisierten Plan/TODO.")
            raise SystemExit(1)
        print("Ergebnis: Planbezug vorhanden oder keine Verhaltensänderung.")
        return

    if args.mode == "regression":
        if requires_regression(risk, bool(code)) and not tests:
            print("BLOCKIERT: R1/R2/R3-Änderung ohne geänderte Regressionstests.")
            raise SystemExit(1)
        print("Ergebnis: Regressionsschutz ist im Diff berücksichtigt.")
        return

    if args.mode == "compliance":
        missing: list[str] = []
        if code and "CHANGELOG.md" not in files:
            missing.append("CHANGELOG.md")
        if code and "PROJEKTSTATUS.md" not in files:
            missing.append("PROJEKTSTATUS.md")
        if risk == "R3" and "projekt-manifest.json" not in files:
            missing.append("projekt-manifest.json")
        if agent_changes and "AGENTS.md" not in files:
            missing.append("AGENTS.md")
        if missing:
            print("BLOCKIERT: Pflichtartefakte fehlen: " + ", ".join(sorted(set(missing))))
            raise SystemExit(1)
        print("Ergebnis: Plan-/Scope-/Dokumentationskonformität bestanden.")
        return

    if args.mode == "release":
        if risk == "R4":
            print("BLOCKIERT: R4 darf nicht automatisch freigegeben werden.")
            raise SystemExit(1)
        diff_check = _run(["git", "diff", "--check", args.base or f"{args.head}^", args.head])
        if diff_check.returncode:
            print("BLOCKIERT: git diff --check meldet Format-/Whitespacefehler.")
            print(diff_check.stdout + diff_check.stderr)
            raise SystemExit(1)
        if requires_regression(risk, bool(code)) and not tests:
            print("BLOCKIERT: verhaltensändernder Release ohne Teständerung.")
            raise SystemExit(1)
        print("Ergebnis: deterministische Release-Vorprüfung bestanden.")
        return


if __name__ == "__main__":
    main()
