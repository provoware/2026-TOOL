# Automatische Tests

Der Nutzer ist keine Testinstanz.

## Testgruppen
- `test_shell.py`: A–N-Shell, Themes, Projektisolation, Markerprüfung, Manifest-/Versionsvertrag, aktive Iteration-4-Entwicklung und Hilfe.
- `test_data_core.py`: WAL/Schema, Persistenz, Archiv/Restore, Kalender, Rollback, Prozesscrash, Backup-Retention und Korruptions-Recovery.
- `test_job_manager.py`: Schema-v1→v2-Migration mit Bestandsschutz, Job-Lifecycle, ungültige Zustandswechsel, Pause/Resume, Abbruch, Checkpoint, Neustart-Recovery, Watchdog, Aktionsjournal, Undo-Vertrag und Transaktionsrollback.
- `test_sorter_preview.py`: read-only Scanner-Feature-Schema mit verifizierter Sicherung, Nicht-Rekursion, Symlink-Schutz, versteckte/System-/Cachebereiche, Dateikategorien, Regelpriorität, Konflikte, verschwundene/unlesbare Einträge, Persistenz/Paging und Nachweis unveränderter Quelldateien.
- `test_api_contract.py`: echter localhost-HTTP-Vertrag von Projekt → Todo/Kalender sowie Joberstellung, Jobsteuerung, Journalansichten, Self-Repair und asynchroner Sortier-Analyse. Prüft zusätzlich Summary/Paging, Root-Symlink-Blockierung und dass Resume wieder einen echten Scanner-Worker startet.
- `test_self_repair.py`: Konfigurationsrestore, Quarantäne, fehlende Standardordner, Fremdordner, Dateikollisionen, Symlink-Schutz und read-only Diagnose.
- `test_agent_gate.py`: R1/R3/R4-Risikoklassifikation, explizite R3-Einstufung des Sortier-Scanners und Schutz vor dem Entfernen von Qualitätsverträgen.
- `test_ux_contract.py`: globale Prozessanzeige, ARIA-Live-Feedback, Warnungs-/Fehlerzähler, Zoom 100–200 %, Tastatursteuerung, Skip-Link, große Aktionsziele, Busy-Schutz sowie read-only Sortier-Assistent mit sicheren Defaults, Wortregel-Feldern, Konflikt-/Skip-Hinweisen und ohne Executor-Endpunkt.
- `test_backup_workflow.py`: verhindert Rückkehr zu den verworfenen historischen Ref-Rotationen.
- `test_backup_snapshots.py`: prüft zwei vollständige Git-Archive inklusive Workflow-Dateien, ZIP-Integrität und SHA-256-Manifest.

## Release-Gate
`scripts/validate_all.sh` prüft Struktur, Manifest, Agentenverträge, Python-/JavaScript-Syntax inklusive `sorter.js`, Jobkern, read-only Sortierkern, UX, Backupverträge, alle Unit-/Integrations-/Crash-/Recoverytests und Diff-Hygiene. GitHub Actions zeigt 17 granulare Schritte; Scanner und HTTP-API besitzen getrennte sichtbare Stufen, damit Fehlerursachen sofort eingegrenzt werden können.

Erst ein vollständig grünes Gate erlaubt die Freigabe. Manuelle Nutzer-Abnahme ersetzt keine fehlende automatische Evidenz.
