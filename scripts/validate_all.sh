#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
printf '\n[1/5] Struktur\n'; ./scripts/validate_repo.sh
printf '\n[2/5] Manifest\n'; python3 scripts/validate_manifest.py
printf '\n[3/5] Python-Syntax\n'; python3 -m py_compile app/server.py scripts/validate_manifest.py scripts/agent_gate.py tests/test_shell.py
printf '\n[4/5] Automatische Tests\n'; python3 -m unittest discover -s tests -p 'test_*.py' -v
printf '\n[5/5] Rollenverträge\n'; grep -q 'Nur analysieren' .agents/ANALYSE_AGENT.md; grep -q 'Keine Implementierung' .agents/PLAN_AGENT.md; grep -q 'Read-only' .agents/PLAN_PRUEFER.md
printf '\n🟢 RELEASE-GATE BESTANDEN\n'
