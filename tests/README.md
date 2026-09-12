# Automatische Tests

Der Nutzer ist keine Testinstanz.

## Testgruppen
- `test_shell.py`: A–N-Shell, Themes, Projektisolation, Markerprüfung und Hilfe.
- `test_data_core.py`: WAL/Schema, Persistenz, Archiv/Restore, Kalender, Rollback, Prozesscrash, Backup-Retention und Korruptions-Recovery.
- `test_api_contract.py`: echter localhost-HTTP-Vertrag von Projekt → Todo → Kalender → Archiv → Restore sowie Self-Repair-Status/Run.
- `test_self_repair.py`: Konfigurationsrestore, Quarantäne, fehlende Standardordner, Fremdordner, Dateikollisionen, Symlink-Schutz und read-only Diagnose.
- `test_agent_gate.py`: R1/R3/R4-Risikoklassifikation und Schutz vor dem Entfernen von Qualitätsverträgen.
- `test_ux_contract.py`: globale Prozessanzeige, ARIA-Live-Feedback, Warnungs-/Fehlerzähler, Zoom 100–200 %, Tastatursteuerung, Skip-Link, große Aktionsziele, Busy-Schutz und UX-Hilfe.

## Release-Gate
`scripts/validate_all.sh` prüft Struktur, Manifest, Agentenverträge, Python-/JavaScript-Syntax, UX-Vertrag, alle Unit-/Integrations-/Crash-/Recoverytests und Diff-Hygiene. GitHub Actions zeigt die wichtigsten Testgruppen zusätzlich als getrennte Schritte, damit Fehlerursachen sofort sichtbar sind.

Erst ein vollständig grünes Gate erlaubt die Freigabe. Manuelle Nutzer-Abnahme ersetzt keine fehlende automatische Evidenz.
