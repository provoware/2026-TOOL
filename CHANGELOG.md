# Changelog

## 0.3.0 – 2026-09-12 – Jobmanager & reversibles Aktionsjournal
### Datenkern / Migration
- zentrale Projektdatenbank von Schema v1 auf v2 erweitert.
- vor Migration einer bestehenden Datenbank wird weiterhin automatisch eine verifizierte SQLite-Sicherung erzeugt.
- bestehende Todo-/Kalenderdaten bleiben erhalten; keine zweite Job-Datenbank und keine parallelen Statusdateien.

### Persistenter Jobmanager
- neues `app/job_manager.py` mit klarer Zustandsmaschine für `queued`, `running`, `paused`, `cancelling`, `cancelled`, `completed`, `failed` und `interrupted`.
- Checkpoint/Resume mit Phase, Einheiten, Bytes, Resume-Cursor und Resume-Zähler.
- zweistufige Pause und Abbruch für aktive Worker: Anforderung → Bestätigung am sicheren Checkpoint.
- append-only `job_events` für nachvollziehbare Zustandsänderungen.
- aktive Jobs werden bei Neuinitialisierung bzw. sauberem Programmende als `interrupted` konserviert statt still weiterzulaufen.

### Watchdog / Recovery
- automatischer Server-Watchdog prüft Heartbeats im Hintergrund.
- stale `running`/`cancelling`-Jobs werden kontrolliert auf `interrupted` gesetzt.
- keine automatische Fortsetzung nach Crash oder Heartbeatverlust; Resume bleibt explizit.

### Reversibles Dateiaktionsjournal
- neue persistente `file_actions` für `copy`, `move`, `rename`, `mkdir`.
- Zustände `planned`, `applied`, `skipped`, `failed`, `undone`.
- monotone Sequenz pro Job und Vorher-/Nachher-Metadaten als JSON.
- Undo-Kandidaten nur bei `applied` + ausdrücklich `reversible=true`.
- `skipped`/`failed` benötigen Klartextgrund.
- Journalmethoden verändern in Iteration 3 bewusst keine Nutzdateien; endgültiges Löschen ist nicht unterstützt.

### API / Sicherheit
- lokale read-/control-Endpunkte für Jobs, Ereignisse, Aktionen und Undo-Kandidaten.
- Worker-interne Bestätigungen bleiben Python-Servicefunktionen und werden nicht als allgemeine HTTP-Schreibendpunkte veröffentlicht.
- localhost-only und bestehende stabile Fehlercodes bleiben erhalten.

### Regression / Qualität
- neuer Iterationsplan `docs/iterationen/ITERATION_03_PLAN.md` und verbindlicher Vertrag `docs/JOB_ACTION_CORE.md`.
- neue Regression `tests/test_job_manager.py` für v1→v2-Migration, Bestandsschutz, Lifecycle, Pause/Resume, Abbruch, Checkpoint, Startup-Recovery, Watchdog, Journal, Undo und Rollback.
- API-Regression um Job-/Journalvertrag erweitert.
- Release-Gate besitzt eine eigene sichtbare Jobmanager-/Migration-/Resume-/Journal-Stufe.

## 0.2.3 – 2026-09-12 – Backup Reliability Hotfix
### Bestätigte Fehlerursache
- v0.2.2 bestand Release- und Subagent-Gates; der separate Backupworkflow blieb rot.
- Versuch 1 (`git push --force` auf historische Backup-Refs) scheiterte, sobald der Zielstand geänderte `.github/workflows/*` enthielt: GitHub verweigerte der GitHub App die Workflow-Übernahme ohne spezielle Workflow-Berechtigung.
- Versuch 2 (GitHub Ref API per `gh api` PATCH/POST) scheiterte ebenfalls mit HTTP 403 `Resource not accessible by integration`.
- damit ist direkte historische Ref-Rotation mit dem vorhandenen Actions-Token als Architektur verworfen.
- Anwendung, SQLite-Daten und vorhandene Legacy-Rückfallzweige wurden durch beide Fehler nicht beschädigt.

### Neue Primärstrategie
- einmalig angelegter technischer Zweig `backup/snapshots`.
- `scripts/build_backup_snapshots.py` erzeugt zwei vollständige `git archive`-ZIPs der unmittelbar vorherigen `main`-Stände.
- `previous-1.zip` enthält den direkten Vorgänger; `previous-2.zip` dessen ersten Elternstand.
- Archive enthalten auch die jeweiligen `.github/workflows/*` des gesicherten Commits.
- jedes ZIP wird mit `zipfile.testzip()` geprüft und erhält SHA-256.
- `version-backups/manifest.json` dokumentiert Commit, SHA-256, Dateizahl und Größen.
- die Rotation verändert auf `backup/snapshots` ausschließlich `version-backups/*`; dessen eingefrorene Workflow-Dateien bleiben unangetastet.
- `backup/previous-1` und `backup/previous-2` bleiben zusätzliche Legacy-Rückfallpunkte, sind aber nicht mehr Primärmechanismus.

### Qualität / Agenten
- bestehender `test_backup_workflow.py` wurde von der nachweislich nicht funktionierenden Ref-API-Annahme auf den Snapshotvertrag umgestellt.
- zusätzlicher `test_backup_snapshots.py` erzeugt mehrere temporäre Git-Stände mit veränderten Workflow-Dateien und prüft beide ZIP-Inhalte sowie SHA-256.
- Release-Gate prüft Workflowvertrag und Snapshotinhalt getrennt.
- AGENTS.md v2.1 klassifiziert Backup-/Release-Engineering als R3 und verlangt Root-Cause-Analyse bei rotem Backup-Gate.
- Produktlaufzeit bleibt bewusst v0.2.2; v0.2.3 ist ein reiner Release-Engineering-Hotfix.

## 0.2.2 – 2026-09-12 – UX, Feedback & Transparenz
- globale stabile Prozessanzeige mit echtem Fortschritt bzw. klar „läuft“.
- Warnungs-/Fehlerzähler, ARIA-Live-Feedback, Busy-Schutz, Zoom 100–200 %, Fokus/Skip-Link und UX-Vertrag.
- Todo, Projektanlage, Self-Repair und Schnellspeicher verwenden das gemeinsame Feedbackmodell.

## 0.2.1 – 2026-09-12 – Reliability & Self-Repair
- sichere Self-Repair-Allowlist, Quarantäne, Projekt-/Symlink-Schutz, stabile API-Fehlercodes und sieben read-only Prüfrollen mit R0–R4.

## 0.2.0 – 2026-09-12 – Datenkern
- SQLite WAL/Transaktionen, Todo, Kalender, reversibles Archiv, verifizierte Datenbanksicherung und Crash-/Recovery-Regression.

## 0.1.0 – 2026-09-12 – Expert Shell
- A–N-Dashboard, gewichtete Startpipeline, fünf Themes, drei Bedienebenen, Projektassistent und Qualitätsgrundlage.
