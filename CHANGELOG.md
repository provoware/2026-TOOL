# Changelog

## 0.2.3 – 2026-09-12 – Backup Reliability Hotfix
### Root Cause
- der v0.2.2-Release bestand Release- und Subagent-Gates, der anschließende Backupworkflow schlug jedoch fehl.
- konkrete Ursache aus dem GitHub-Job-Log: Der Actions-GitHub-App-Token darf einen Backup-Branch nicht auf einen historischen Commit verschieben, wenn dadurch geänderte `.github/workflows/*` übernommen würden und die spezielle Workflow-Berechtigung fehlt.
- die vorhandenen Legacy-Rückfallzweige blieben unverändert und korrekt; kein Versions- oder Nutzdatenverlust.

### Neue Backupstrategie
- einmaliger technischer Zweig `backup/snapshots`.
- zwei vollständige Quellarchive `version-backups/previous-1.zip` und `previous-2.zip` aus `git archive`.
- Archive enthalten auch die jeweiligen `.github/workflows/*` des gesicherten Stands.
- ZIP-Integritätsprüfung vor Veröffentlichung.
- `manifest.json` mit Commit-ID, SHA-256, Dateizahl und Größenangaben.
- die automatische Rotation verändert auf `backup/snapshots` ausschließlich `version-backups/*`; eingefrorene Workflow-Dateien des Speicherzweigs bleiben unangetastet.
- alte `backup/previous-1` / `backup/previous-2` bleiben als zusätzliche Legacy-Punkte erhalten.

### Qualität / Agenten
- eigener `build_backup_snapshots.py` statt komplexer Inline-Backup-Logik.
- Regression erzeugt mehrere temporäre Git-Stände inklusive geänderter Workflow-Dateien und prüft Snapshotinhalt + SHA-256.
- Release-Gate erhält eine eigene Backup-Snapshot-Prüfung.
- AGENTS.md v2.1 behandelt Backup/Release-Engineering ausdrücklich als R3 und verlangt Root-Cause-Analyse bei rotem Backup-Gate.
- Produktlaufzeit bleibt bewusst v0.2.2; v0.2.3 ist ein reiner Release-Engineering-Hotfix.

## 0.2.2 – 2026-09-12 – UX, Feedback & Transparenz
- globale wiederverwendbare Prozessanzeige, Warn-/Fehlerzähler, Busy-Schutz, Zoom 100–200 %, Skip-Link/Fokus, UX-Standard und UX-Regression.

## 0.2.1 – 2026-09-12 – Reliability & Self-Repair
- sichere Self-Repair-Allowlist, Quarantäne, Projekt-/Symlink-Schutz, stabile API-Fehlercodes und sieben read-only Prüfrollen mit R0–R4.

## 0.2.0 – 2026-09-12 – Datenkern
- SQLite WAL/Transaktionen, Todo, Kalender, reversibles Archiv, verifizierte Datenbanksicherung und Crash-/Recovery-Regression.

## 0.1.0 – 2026-09-12 – Expert Shell
- A–N-Dashboard, gewichtete Startpipeline, fünf Themes, drei Bedienebenen, Projektassistent und Qualitätsgrundlage.
