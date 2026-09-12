# Projektstatus

## Version
0.2.0 – Iteration 2 „Datenkern“

## Status
🟢 Freigabefähig – vollständiger Iterationsdiff hat GitHub Release-Gate sowie Analyse-, Plan- und Plan-Prüfer-Gates bestanden.

## Automatisch validiert
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
- GitHub Release-Gate: bestanden
- Subagent-Gates Analyse → Plan → Plan-Prüfung: bestanden
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
Dieser Stand darf auf `main` übernommen werden. Nach dem Merge wird derselbe Release-Gate-Zyklus auf `main` erneut ausgeführt und die Zwei-Versionen-Backuprotation kontrolliert.
