#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
printf '\n[1/11] Repository-Struktur\n'; ./scripts/validate_repo.sh
printf '\n[2/11] Manifest / Verträge\n'; python3 scripts/validate_manifest.py
printf '\n[3/11] Agentenverträge\n'; python3 scripts/validate_agents.py
printf '\n[4/11] Python-Syntax\n'; python3 -m py_compile \
  app/server.py app/project_store.py app/data_core.py app/self_repair.py app/job_manager.py \
  scripts/build_backup_snapshots.py scripts/validate_manifest.py scripts/validate_agents.py scripts/agent_gate.py \
  tests/test_shell.py tests/test_data_core.py tests/test_api_contract.py tests/test_self_repair.py tests/test_job_manager.py \
  tests/test_agent_gate.py tests/test_ux_contract.py tests/test_backup_workflow.py tests/test_backup_snapshots.py
printf '\n[5/11] JavaScript-Syntax\n'; node --check app/static/js/feedback.js; node --check app/static/js/app.js; node --check app/static/js/data.js; node --check app/static/js/startup.js
printf '\n[6/11] Jobmanager / Migration / Resume / Journal\n'; python3 -m unittest -v tests.test_job_manager
printf '\n[7/11] UX-Vertrag\n'; python3 -m unittest -v tests.test_ux_contract
printf '\n[8/11] Backup-Workflow-Vertrag\n'; python3 -m unittest -v tests.test_backup_workflow
printf '\n[9/11] Backup-Snapshot-Inhalt\n'; python3 -m unittest -v tests.test_backup_snapshots
printf '\n[10/11] Automatische Gesamtregression\n'; python3 -m unittest discover -s tests -p 'test_*.py' -v
printf '\n[11/11] Repository-Diff-Hygiene\n'; git diff --check HEAD~1 HEAD || { printf '\nBLOCKIERT: letzter Commit enthält Whitespace-/Patchfehler.\n'; exit 1; }
printf '\n🟢 RELEASE-GATE BESTANDEN – Iteration 3 Job-/Aktionskern v0.3.0\n'
