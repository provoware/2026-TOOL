# Automatische Tests

Der Nutzer ist keine Testinstanz.

## Testgruppen
- `test_shell.py`: A–N-Shell, Themes, Projektisolation, Markerprüfung, Manifest-/Versionsvertrag und Hilfe.
- `test_data_core.py`: WAL/Schema, Persistenz, Archiv/Restore, Kalender, Rollback, Prozesscrash, Backup-Retention und Korruptions-Recovery.
- `test_job_manager.py`: Schema-v1→v2-Migration mit Bestandsschutz, Job-Lifecycle, ungültige Zustandswechsel, Pause/Resume, Abbruch, Checkpoint, Neustart-Recovery, Watchdog, Aktionsjournal, Undo-Vertrag und Transaktionsrollback.
- `test_api_contract.py`: echter localhost-HTTP-Vertrag von Projekt → Todo/Kalender sowie Joberstellung, Jobsteuerung, Journalansichten und Self-Repair.
- `test_self_repair.py`: Konfigurationsrestore, Quarantäne, fehlende Standardordner, Fremdordner, Dateikollisionen, Symlink-Schutz und read-only Diagnose.
- `test_agent_gate.py`: R1/R3/R4-Risikoklassifikation und Schutz vor dem Entfernen von Qualitätsverträgen.
- `test_ux_contract.py`: globale Prozessanzeige, ARIA-Live-Feedback, Warnungs-/Fehlerzähler, Zoom 100–200 %, Tastatursteuerung, Skip-Link, große Aktionsziele, Busy-Schutz und UX-Hilfe.
- `test_backup_workflow.py`: verhindert Rückkehr zu den verworfenen historischen Ref-Rotationen.
- `test_backup_snapshots.py`: prüft zwei vollständige Git-Archive inklusive Workflow-Dateien, ZIP-Integrität und SHA-256-Manifest.

## Release-Gate
`scripts/validate_all.sh` prüft Struktur, Manifest, Agentenverträge, Python-/JavaScript-Syntax, Jobkern, UX, Backupverträge, alle Unit-/Integrations-/Crash-/Recoverytests und Diff-Hygiene. GitHub Actions zeigt die wichtigsten Testgruppen zusätzlich als getrennte Schritte, damit Fehlerursachen sofort sichtbar sind.

Erst ein vollständig grünes Gate erlaubt die Freigabe. Manuelle Nutzer-Abnahme ersetzt keine fehlende automatische Evidenz.
