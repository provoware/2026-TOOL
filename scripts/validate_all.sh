#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
printf '\n[1/6] Struktur\n'; ./scripts/validate_repo.sh
printf '\n[2/6] Manifest\n'; python3 scripts/validate_manifest.py
printf '\n[3/6] Python-Syntax\n'; python3 -m py_compile app/server.py app/project_store.py app/data_core.py scripts/validate_manifest.py scripts/agent_gate.py tests/test_shell.py tests/test_data_core.py tests/test_api_contract.py
printf '\n[4/6] JavaScript-Syntax\n'; node --check app/static/js/app.js; node --check app/static/js/data.js; node --check app/static/js/startup.js
printf '\n[5/6] Automatische Regression\n'; python3 -m unittest discover -s tests -p 'test_*.py' -v
printf '\n[6/6] Rollenverträge\n'; grep -q 'Nur analysieren' .agents/ANALYSE_AGENT.md; grep -q 'Keine Implementierung' .agents/PLAN_AGENT.md; grep -q 'Read-only' .agents/PLAN_PRUEFER.md
printf '\n🟢 RELEASE-GATE BESTANDEN – Datenkern v0.2.0\n'
