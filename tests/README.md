# Automatische Tests

Der Nutzer ist nicht die Testinstanz. Jede freizugebende Version muss maschinell geprüft werden.

## Testgruppen

- `test_shell.py` – A–N-Shell, Themes, Manifest, Projektisolation, strikter Projektmarker, Schnellspeicher und Hilfe.
- `test_data_core.py` – SQLite WAL/Schema, Transaktionen, Todo-Archiv/Restore, Kalenderprojektion, Restart/Persistenz, Prozessabsturz, Recovery und Backup-Retention.
- `test_api_contract.py` – realer localhost-HTTP-Vertrag für Projektanlage, Todo, Archiv, Kalender, Restore, Eingabevalidierung sowie read-only Self-Repair-Diagnose und sicheren Reparaturlauf.
- `test_self_repair.py` – verifizierte Konfigurations-Rückfälle, Quarantäne, unterbrochener atomarer Write, Projektstruktur-Reparatur, Fremdordnerschutz, Dateikollisionen, Symlink-Grenzen und read-only Diagnose.
- `test_agent_gate.py` – Risikoklassifikation R1/R3/R4 und Schutz gegen das Entfernen von Tests oder Qualitätsverträgen.

## Vertragsprüfungen

- `scripts/validate_manifest.py` prüft Version, Daten-/Backupverträge, Self-Repair-Allowlist/Denylist, Fehlercodes und Qualitätsmodell.
- `scripts/validate_agents.py` prüft alle sieben Agentenrollen, Read-only-Grenzen, Manifestzuordnung und GitHub-Workflow-Verdrahtung.
- `scripts/agent_gate.py` bewertet den vollständigen Diff risikobasiert und erzwingt Plan-, Regressions-, Dokumentations- und Releasebedingungen.

## Release-Gate

`scripts/validate_all.sh` prüft Struktur, Manifest, Agentenverträge, Python- und JavaScript-Syntax, alle Regressionstests und Diff-Hygiene. Eine Version wird nicht freigegeben, wenn ein Kerncheck fehlschlägt.

Jeder bestätigte Fehler hinterlässt mindestens einen Regressionstest, eine zusätzliche Validierung oder eine Architekturverbesserung, die seine Fehlerklasse künftig verhindert.
