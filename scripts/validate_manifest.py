#!/usr/bin/env python3
import json
from pathlib import Path

m = json.loads(Path("projekt-manifest.json").read_text(encoding="utf-8"))
errors = []
if m.get("schema_version") != 1: errors.append("Manifest-schema_version muss 1 sein")
app = m.get("app", {})
if app.get("version") != "0.2.0": errors.append("App-Version muss 0.2.0 sein")
iteration = m.get("iteration", {})
if iteration.get("number") != 2: errors.append("Iteration muss 2 sein")
ui = m.get("ui", {})
if ui.get("areas") != list("ABCDEFGHIJKLMN"): errors.append("A-N-Bereiche unvollständig")
if len(ui.get("themes", [])) != 5: errors.append("genau fünf Themes erforderlich")
quality = m.get("quality", {})
if quality.get("manual_user_acceptance_required") is not False: errors.append("manuelle Nutzerabnahme muss false sein")
if quality.get("crash_recovery_tests") is not True: errors.append("Crash-/Recovery-Tests müssen aktiv sein")
backup = m.get("backup", {})
if backup.get("keep_previous") != 2: errors.append("zwei Git-Vorgängerversionen erforderlich")
if backup.get("database_verified_keep") != 2: errors.append("zwei verifizierte DB-Sicherungen erforderlich")
data = m.get("data", {})
if data.get("engine") != "sqlite3": errors.append("Datenkern muss sqlite3 sein")
if data.get("schema_version") != 1: errors.append("DB-Schema muss 1 sein")
if data.get("journal_mode") != "WAL": errors.append("SQLite-WAL erforderlich")
if data.get("calendar_source") != "todos": errors.append("Kalender muss aus Todos gespeist werden")
if data.get("archive_strategy") != "logical-reversible": errors.append("Todo-Archiv muss reversibel sein")
if data.get("backup_keep") != 2: errors.append("DB-Backup-Retention muss 2 sein")
if errors:
    for error in errors: print("FEHLER:", error)
    raise SystemExit(1)
print("OK   Manifest konsistent – v0.2.0 Datenkern")
