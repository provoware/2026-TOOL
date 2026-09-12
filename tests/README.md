# Automatische Tests

Der Nutzer ist nicht die Testinstanz. Jede freizugebende Version muss maschinell geprüft werden.

## Testgruppen

- `test_shell.py` – A–N-Shell, Themes, Manifest, Projektisolation, Schnellspeicher und Hilfe.
- `test_data_core.py` – SQLite WAL/Schema, Transaktionen, Todo-Archiv/Restore, Kalenderprojektion, Restart/Persistenz, Prozessabsturz, Recovery und Backup-Retention.
- `test_api_contract.py` – realer localhost-HTTP-Vertrag für Projektanlage, Todo, Archiv, Kalender, Restore und Eingabevalidierung.

## Release-Gate

`scripts/validate_all.sh` prüft Struktur, Manifest, Python- und JavaScript-Syntax, alle Regressionstests und Agentenrollen. Eine Version wird nicht freigegeben, wenn ein Kerncheck fehlschlägt.

Jeder bestätigte Fehler hinterlässt mindestens einen Regressionstest, eine zusätzliche Validierung oder eine Architekturverbesserung, die seine Fehlerklasse künftig verhindert.
