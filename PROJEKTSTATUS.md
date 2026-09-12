# Projektstatus

## Version
0.2.0 – Iteration 2 „Datenkern“ – Release Candidate

## Status
🟡 RC – Implementierung vollständig; unabhängiges GitHub-Release-Gate auf dem finalen Branchstand steht noch aus.

## Automatisch vorvalidiert
- SQLite WAL/Schema/Integrität
- Transaktions-Rollback
- Restart/Persistenz
- simulierter Prozessabsturz mit uncommitteter Transaktion
- verifizierte Sicherung und Korruptions-Recovery
- Backup-Retention auf zwei DB-Sicherungen
- Todo Archiv/Wiederherstellung
- Kalenderprojektion aus derselben Todo-Datenquelle
- HTTP-API-Vertrag Todo → Kalender → Archiv → Restore
- Expert-Shell A–N, Themes, Projektisolation, Schnellspeicher und Hilfe
- Nutzer-Abnahme: nicht erforderlich

## Enthalten
- getrennte Services für Projektpersistenz und SQLite-Datenkern
- Todo D mit optionaler Terminierung und Priorität
- reversibles Todo-Archiv
- Monatskalender E ohne doppelte Terminspeicherung
- Recovery mit Quarantäne des beschädigten Originals
- Startprüfung für SQLite/WAL und unsauberen Sitzungszustand
- verbindlicher Datenstandard und erweiterte Regression

## Freigaberegel
Status wird erst auf 🟢 Freigegeben gesetzt, wenn das GitHub-Release-Gate, Subagent-Gates und Backuprotation für den finalen `main`-Commit erfolgreich abgeschlossen sind.
