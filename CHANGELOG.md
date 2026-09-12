# Changelog

## 0.2.0 – 2026-09-12
### Neu
- zentraler SQLite-Datenkern in eigener Serviceschicht.
- WAL-Modus, Foreign Keys, Busy Timeout, Schema-Versionierung und explizite Transaktionen.
- Todo-Bereich D mit optionalem Datum, optionaler Uhrzeit und Priorität.
- Abhaken verschiebt Todos reversibel ins Archiv; Wiederherstellung ist möglich.
- Monatskalender E liest Termine direkt aus derselben Todo-Tabelle, ohne Doppelhaltung.
- Organisationsübersicht zeigt aktive/archivierte Todos und DB-Sicherungen.
- Datenkernprüfung in der grafischen Startroutine.

### Sicherheit & Recovery
- SQLite-Sicherungen werden mit der Backup-API erzeugt und vor Freigabe geprüft.
- maximal zwei aktuelle verifizierte Datenbank-Sicherungen.
- beschädigte Datenbank wird vor Recovery als Quarantäne erhalten.
- automatische Recovery ausschließlich aus verifizierter Sicherung.
- Crash-, Restart-/Persistenz-, Rollback-, Recovery- und API-Vertragstests ergänzt.
- ursprüngliche Expert-Shell-Regression bleibt Bestandteil des Release-Gates.

## 0.1.0 – 2026-09-12
### Neu
- Expert Shell mit A–N-Dashboard und dominantem Hauptarbeitsbereich N.
- echte, gewichtete grafische Startpipeline.
- fünf Themes und drei Bedienebenen.
- lokaler Python-Server ohne externe Runtime-Abhängigkeiten.
- sicherer Projektassistent und projektbezogener Schnellspeicher.
- Hilfesystem, Status-/Loggingbereich und Fokusmodus.
- triggerbasierte Agentenrollen und deterministische CI-Gates.
- rotierende Rückfallzweige für zwei vorherige `main`-Versionen.

### Sicherheit
- localhost-only Server.
- atomare JSON-Speicherung mit zwei Vorgängerkopien.
- fremde nichtleere Zielordner werden nicht automatisch übernommen.
