#!/usr/bin/env bash
set -euo pipefail
required=(
  README.md AGENTS.md ENTWICKLUNGSREGELN.md ENTWICKLERDOKU.md PROJEKTSTATUS.md TODO.md CHANGELOG.md
  projekt-manifest.json start.sh
  app/server.py app/static/index.html app/static/css/design.css app/static/js/app.js app/static/js/startup.js app/static/help.json
  .agents/ANALYSE_AGENT.md .agents/PLAN_AGENT.md .agents/PLAN_PRUEFER.md
  docs/ARCHITEKTUR.md docs/QUALITAETSSICHERUNG.md docs/STARTROUTINE.md docs/AGENTEN_WORKFLOW.md docs/HILFE.md
  standards/PROJEKTSTANDARD.md
  scripts/validate_manifest.py scripts/agent_gate.py tests/test_shell.py
)
missing=0
for file in "${required[@]}"; do
  if [[ -f "$file" ]]; then printf 'OK   %s\n' "$file"; else printf 'FEHLT %s\n' "$file"; missing=$((missing+1)); fi
done
(( missing == 0 )) || { printf '\nBLOCKIERT: %d Pflichtdatei(en) fehlen.\n' "$missing"; exit 1; }
printf '\nRepository-Struktur vollständig.\n'
