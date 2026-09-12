# Architektur

## Ziel
Die Shell bleibt klein, austauschbar und erweiterbar. Fachmodule dürfen weder Startlogik noch Projektpersistenz oder Datenbankzugriffe duplizieren.

## Schichten
1. **Bootstrap:** `start.sh`, Serverstart, Sessionmarker.
2. **Projektservice:** `app/project_store.py` – Projektstruktur, atomare Konfiguration, Schnellspeicher.
3. **Datenkern:** `app/data_core.py` – SQLite, Schema, Transaktionen, Todo, Kalenderprojektion, Sicherung und Recovery.
4. **API:** `app/server.py` – schmale localhost-only HTTP-Schnittstelle und Fehlerabbildung.
5. **UI-Shell:** A–N, Designsystem, Hilfe, Einstellungen.
6. **Fach-UI:** `app/static/js/data.js` + `data.css` für Todo/Kalender; keine Fachlogik in der Shell duplizieren.
7. **Startup Controller:** echte unabhängige Prüfschritte inklusive SQLite/WAL und Crashstatus.
8. **Qualität:** Manifest, Unit-/API-/Crash-/Recovery-Tests, Agent-Gates, Backuprotation.

## Datenprinzip
Todos sind die einzige Quelle für Aufgaben und deren Termine. Der Kalender besitzt keinen zweiten Terminbestand, sondern liest eine Monatsprojektion der aktiven terminierten Todos. Archivieren ist ein reversibler Statuswechsel und kein Löschen.

## Recovery
SQLite läuft im WAL-Modus. Sicherungen werden über die SQLite-Backup-API erzeugt und vor Freigabe mit `PRAGMA quick_check` geprüft. Bei Korruption wird das Original quarantänisiert; automatische Wiederherstellung erfolgt ausschließlich aus einer geprüften Sicherung. Es werden zwei aktuelle DB-Sicherungen gehalten.

## Komplexitätsregel
Neue Schicht nur, wenn sie Abhängigkeiten reduziert, sicherheitskritische Logik zentralisiert oder Wiederverwendung schafft. UI, HTTP, Projektpersistenz und Datenzugriff bleiben getrennt, damit einzelne Bereiche unabhängig testbar und austauschbar sind.
