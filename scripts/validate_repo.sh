#!/usr/bin/env bash
set -euo pipefail
required=(
  README.md AGENTS.md ENTWICKLUNGSREGELN.md ENTWICKLERDOKU.md PROJEKTSTATUS.md TODO.md CHANGELOG.md
  projekt-manifest.json start.sh
  .github/workflows/quality.yml .github/workflows/agents.yml .github/workflows/backup.yml
  app/server.py app/project_store.py app/data_core.py app/self_repair.py app/job_manager.py
  app/static/index.html app/static/css/design.css app/static/css/data.css app/static/css/feedback.css
  app/static/js/feedback.js app/static/js/app.js app/static/js/data.js app/static/js/startup.js app/static/help.json
  .agents/ANALYSE_AGENT.md .agents/RISIKO_AGENT.md .agents/FEHLERURSACHE_AGENT.md .agents/PLAN_AGENT.md
  .agents/REGRESSIONS_AGENT.md .agents/PLAN_PRUEFER.md .agents/RELEASE_PRUEFER.md
  docs/ARCHITEKTUR.md docs/QUALITAETSSICHERUNG.md docs/STARTROUTINE.md docs/AGENTEN_WORKFLOW.md docs/HILFE.md docs/SELFREPAIR.md docs/UX_STANDARD.md docs/OFFENE_RISIKEN.md docs/JOB_ACTION_CORE.md
  docs/iterationen/ITERATION_02_PLAN.md docs/iterationen/ITERATION_021_PLAN.md docs/iterationen/ITERATION_022_UX_PLAN.md
  docs/iterationen/HOTFIX_BACKUP_ROTATION.md docs/iterationen/ITERATION_023_BACKUP_HOTFIX.md docs/iterationen/ITERATION_03_PLAN.md
  standards/PROJEKTSTANDARD.md standards/DATENSTANDARD.md
  scripts/build_backup_snapshots.py scripts/validate_manifest.py scripts/validate_agents.py scripts/agent_gate.py scripts/validate_all.sh
  tests/README.md tests/test_shell.py tests/test_data_core.py tests/test_api_contract.py tests/test_self_repair.py tests/test_job_manager.py
  tests/test_agent_gate.py tests/test_ux_contract.py tests/test_backup_workflow.py tests/test_backup_snapshots.py
)
missing=0
for file in "${required[@]}"; do
  if [[ -f "$file" ]]; then printf 'OK   %s\n' "$file"; else printf 'FEHLT %s\n' "$file"; missing=$((missing+1)); fi
done
(( missing == 0 )) || { printf '\nBLOCKIERT: %d Pflichtdatei(en) fehlen.\n' "$missing"; exit 1; }
printf '\nRepository-Struktur vollständig – Iteration 3 Job-/Aktionskern v0.3.0.\n'
