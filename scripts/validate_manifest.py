#!/usr/bin/env python3
import json
from pathlib import Path

m = json.loads(Path("projekt-manifest.json").read_text(encoding="utf-8"))
errors = []
if m.get("schema_version") != 1:
    errors.append("Manifest-schema_version muss 1 sein")
app = m.get("app", {})
if app.get("version") != "0.4.0" or app.get("status") != "iteration-4-sorter-preview":
    errors.append("Produktlaufzeit muss Iteration 4 / v0.4.0 Sortier-Vorschau sein")
development = m.get("development", {})
if development.get("active_iteration") != 4 or development.get("current_version") != "0.4.0":
    errors.append("Aktiver Releasevertrag muss Iteration 4 / v0.4.0 sein")
if development.get("stage") != "sorter-preview" or development.get("risk") != "R3" or development.get("release_status") != "release-candidate":
    errors.append("Iteration 4 muss als R3 sorter-preview release-candidate geführt werden")
iteration = m.get("iteration", {})
if iteration.get("number") != 4 or iteration.get("stage") != "4.0" or iteration.get("release") != "0.4.0":
    errors.append("Iterations-/Releasevertrag muss 4 / 4.0 / 0.4.0 sein")
if iteration.get("scope") != "sorter-preview" or iteration.get("risk") != "R3":
    errors.append("Iteration 4 muss als R3 sorter-preview klassifiziert sein")
ui = m.get("ui", {})
if ui.get("areas") != list("ABCDEFGHIJKLMN") or len(ui.get("themes", [])) != 5:
    errors.append("A-N-/Theme-Vertrag verletzt")
if ui.get("zoom_percent") != {"min":100,"max":200,"step":5}:
    errors.append("Zoomvertrag muss 100–200 % in 5er Schritten sein")
if set(ui.get("zoom_shortcuts", [])) != {"Ctrl++","Ctrl+-","Ctrl+0","Ctrl+Mausrad"}:
    errors.append("Zoom-Tastaturvertrag unvollständig")
for flag in ("global_process_feedback","session_warning_error_counters","skip_link","color_only_status_forbidden"):
    if ui.get(flag) is not True:
        errors.append(f"UI-Vertrag fehlt: {flag}")
quality = m.get("quality", {})
if quality.get("manual_user_acceptance_required") is not False or quality.get("crash_recovery_tests") is not True:
    errors.append("Qualitätsvertrag Nutzer/Crash verletzt")
if quality.get("self_repair_guarded") is not True or quality.get("risk_model") != "R0-R4":
    errors.append("Self-Repair-/Risikovertrag verletzt")
if quality.get("agent_contract_validation") != "scripts/validate_agents.py" or quality.get("ux_contract_test") != "tests/test_ux_contract.py":
    errors.append("Qualitätsprüfer fehlen")
if quality.get("backup_contract_test") != "tests/test_backup_snapshots.py":
    errors.append("Backup-Snapshot-Vertragstest fehlt")
if quality.get("job_contract_test") != "tests/test_job_manager.py":
    errors.append("Jobmanager-Vertragstest fehlt")
if quality.get("sorter_contract_test") != "tests/test_sorter_preview.py":
    errors.append("Sortier-Vorschau-Vertragstest fehlt")
if quality.get("release_package_test") != "tests/test_release_package.py":
    errors.append("Release-Paket-Vertragstest fehlt")
backup = m.get("backup", {})
if backup.get("strategy") != "verified-git-archive-snapshot-branch":
    errors.append("Backupstrategie muss verifizierte Git-Archive verwenden")
if backup.get("snapshot_branch") != "backup/snapshots" or backup.get("snapshot_directory") != "version-backups":
    errors.append("Backup-Snapshotziel unvollständig")
if backup.get("snapshot_slots") != 2 or backup.get("keep_previous") != 2:
    errors.append("genau zwei Versions-Snapshots erforderlich")
if backup.get("sha256") is not True or backup.get("zip_integrity_check") is not True:
    errors.append("Backup-Verifikation unvollständig")
if backup.get("includes_workflow_files_inside_archives") is not True:
    errors.append("vollständige Archive müssen Workflow-Dateien enthalten")
if backup.get("workflow_contract_test") != "tests/test_backup_workflow.py" or backup.get("snapshot_contract_test") != "tests/test_backup_snapshots.py":
    errors.append("Backup-Workflow-/Inhaltstests fehlen")
if backup.get("database_verified_keep") != 2:
    errors.append("zwei verifizierte DB-Sicherungen erforderlich")
package = m.get("release_package", {})
if package.get("format") != "zip" or package.get("source") != "git-archive":
    errors.append("Release-Paket muss als Git-Archiv-ZIP gebaut werden")
if package.get("builder") != "scripts/build_release_package.py" or package.get("contract_test") != "tests/test_release_package.py":
    errors.append("Release-Paket-Builder/Testvertrag fehlt")
if package.get("artifact_name") != "PROVOWARE-HEADQUARTER-v0.4.0" or package.get("filename") != "PROVOWARE-HEADQUARTER-v0.4.0.zip":
    errors.append("Release-Paketname muss v0.4.0 entsprechen")
if package.get("prefix") != "PROVOWARE-HEADQUARTER-v0.4.0/":
    errors.append("Release-ZIP benötigt einen eindeutigen v0.4.0-Wurzelordner")
if package.get("sha256") is not True or package.get("zip_integrity_check") is not True:
    errors.append("Release-Paket-Verifikation ist unvollständig")
data = m.get("data", {})
if data.get("engine") != "sqlite3" or data.get("schema_version") != 2 or data.get("journal_mode") != "WAL":
    errors.append("SQLite-Datenvertrag v2 verletzt")
if data.get("migration_backup") is not True:
    errors.append("Schema-Migration muss vorher verifiziert sichern")
if data.get("calendar_source") != "todos" or data.get("archive_strategy") != "logical-reversible" or data.get("backup_keep") != 2:
    errors.append("Daten-/Archivvertrag verletzt")
jobs = m.get("jobs", {})
expected_job_states = {"queued","running","paused","cancelling","cancelled","completed","failed","interrupted"}
if jobs.get("persistent") is not True or jobs.get("same_project_database") is not True:
    errors.append("Jobs müssen persistent in derselben Projektdatenbank liegen")
if set(jobs.get("statuses", [])) != expected_job_states:
    errors.append("Job-Zustandsvertrag unvollständig")
for flag in ("checkpoint_resume","heartbeat","automatic_watchdog","startup_recovery"):
    if jobs.get(flag) is not True:
        errors.append(f"Job-Sicherheitsvertrag fehlt: {flag}")
if jobs.get("event_log") != "append-only" or jobs.get("test") != "tests/test_job_manager.py":
    errors.append("Job-Ereignis-/Testvertrag fehlt")
actions = m.get("file_actions", {})
if set(actions.get("types", [])) != {"copy","move","rename","mkdir"}:
    errors.append("Dateiaktions-Typvertrag verletzt")
if set(actions.get("statuses", [])) != {"planned","applied","skipped","failed","undone"}:
    errors.append("Dateiaktions-Zustandsvertrag verletzt")
if actions.get("planning_changes_files") is not False or actions.get("undo_requires_applied_and_reversible") is not True:
    errors.append("Vorschau-/Undo-Sicherheitsvertrag verletzt")
if actions.get("destructive_delete_supported") is not False:
    errors.append("Endgültiges Löschen darf nicht unterstützt werden")
sorter = m.get("sorter_preview", {})
if sorter.get("source_read_only") is not True or sorter.get("same_project_database") is not True:
    errors.append("Sortier-Vorschau muss read-only auf derselben Projektdatenbank arbeiten")
if sorter.get("feature_schema_version") != 1 or sorter.get("verified_backup_before_first_schema_create") is not True:
    errors.append("Sortier-Feature-Schema-/Backupvertrag verletzt")
if sorter.get("recursive_default") is not False or sorter.get("include_hidden_default") is not False or sorter.get("follow_symlinks") is not False:
    errors.append("Sortier-Defaults müssen nicht-rekursiv, ohne versteckte Inhalte und ohne Symlink-Folgen sein")
if set(sorter.get("categories", [])) != {"Bilder","Video","Audio","Dokumente","Archive","Text / Code","Sonstige"}:
    errors.append("Sortier-Kategorienvertrag unvollständig")
if set(sorter.get("decisions", [])) != {"matched","conflict","unmatched","skipped"}:
    errors.append("Sortier-Entscheidungsvertrag unvollständig")
for flag in ("rule_priority","equal_priority_different_targets_conflict","paging"):
    if sorter.get(flag) is not True:
        errors.append(f"Sortier-Vorschau-Vertrag fehlt: {flag}")
if sorter.get("mutating_operations") != []:
    errors.append("Sortier-Vorschau darf keine mutierenden Dateioperationen enthalten")
if sorter.get("test") != "tests/test_sorter_preview.py":
    errors.append("Sortier-Vorschau-Testvertrag fehlt")
if set(m.get("agents", {})) != {"analysis","risk","root_cause","planning","regression","compliance","release"}:
    errors.append("Manifest muss exakt sieben Prüfrollen enthalten")
self_repair = m.get("self_repair", {})
allowed = self_repair.get("automatic_scope", [])
forbidden = self_repair.get("forbidden_scope", [])
if not isinstance(allowed, list) or len(allowed) < 4 or not isinstance(forbidden, list) or len(forbidden) < 6:
    errors.append("Self-Repair Allow-/Denylist unvollständig")
if "delete-user-data" not in forbidden or "restore-unverified-backup" not in forbidden:
    errors.append("kritische Self-Repair-Verbote fehlen")
error_handling = m.get("error_handling", {})
if error_handling.get("stable_api_codes") is not True or error_handling.get("unknown_internal_details_exposed") is not False:
    errors.append("Fehlerbehandlungsvertrag verletzt")
if errors:
    for error in errors:
        print("FEHLER:", error)
    raise SystemExit(1)
print("OK   Manifest konsistent – Iteration 4 / Read-only Sortier-Analyse & Vorschau v0.4.0 RC")
