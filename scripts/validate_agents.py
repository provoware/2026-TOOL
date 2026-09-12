#!/usr/bin/env python3
"""Maschinenlesbare Prüfung der PROVOWARE-Agentenverträge."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    ".agents/ANALYSE_AGENT.md": ("Nur analysieren",),
    ".agents/RISIKO_AGENT.md": ("Read-only", "R0", "R4"),
    ".agents/FEHLERURSACHE_AGENT.md": ("Read-only", "Root Cause"),
    ".agents/PLAN_AGENT.md": ("Keine Implementierung",),
    ".agents/REGRESSIONS_AGENT.md": ("Read-only", "Regression"),
    ".agents/PLAN_PRUEFER.md": ("Read-only", "BLOCKIERT"),
    ".agents/RELEASE_PRUEFER.md": ("Read-only", "RELEASE READY"),
}


def fail(message: str) -> None:
    print("FEHLER:", message)
    raise SystemExit(1)


def main() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for token in ("R0", "R1", "R2", "R3", "R4", "Self-Repair – Allowlist", "Self-Repair – Denylist", "Release-Prüfer"):
        if token not in agents:
            fail(f"AGENTS.md fehlt Pflichtbegriff: {token}")

    for relative, tokens in EXPECTED.items():
        path = ROOT / relative
        if not path.is_file():
            fail(f"Rollenvertrag fehlt: {relative}")
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                fail(f"{relative} fehlt Vertragsmerkmal: {token}")
        if relative != ".agents/PLAN_AGENT.md" and not any(token in text for token in ("Read-only", "Nur analysieren")):
            fail(f"{relative} ist nicht eindeutig read-only")
        if "Darf Produktivcode ändern" in text or "darf Produktivcode ändern" in text:
            fail(f"{relative} erlaubt unzulässige Implementierung")

    manifest = json.loads((ROOT / "projekt-manifest.json").read_text(encoding="utf-8"))
    declared = manifest.get("agents", {})
    required_keys = {"analysis", "risk", "root_cause", "planning", "regression", "compliance", "release"}
    missing = required_keys - set(declared)
    if missing:
        fail("Manifest fehlen Agentenrollen: " + ", ".join(sorted(missing)))

    workflow = (ROOT / ".github/workflows/agents.yml").read_text(encoding="utf-8")
    for mode in ("analyse", "risk", "rootcause", "plan", "regression", "compliance", "release"):
        if f"--mode {mode}" not in workflow:
            fail(f"Workflow triggert Agent-Gate '{mode}' nicht")

    gate = (ROOT / "scripts/agent_gate.py").read_text(encoding="utf-8")
    for token in ("R3", "R4", "regression", "release"):
        if token not in gate:
            fail(f"agent_gate.py fehlt Vertragslogik: {token}")

    print(f"OK   Agentenverträge konsistent ({len(EXPECTED)} Rollen)")


if __name__ == "__main__":
    main()
