# Architektur

## Ziel
Die Shell bleibt klein, austauschbar und erweiterbar. Fachmodule dürfen weder Startlogik noch Projektpersistenz, Datenbankzugriffe oder Reparaturregeln duplizieren.

## Schichten
1. **Bootstrap:** `start.sh`, Serverstart, Sessionmarker.
2. **Projektservice:** `app/project_store.py` – Projektstruktur, atomare Konfiguration, Schnellspeicher und strikte Projektmarker-Prüfung.
3. **Self-Repair:** `app/self_repair.py` – ausschließlich freigegebene, reversible Reparaturregeln, Quarantäne und Diagnose; keine Fachlogik.
4. **Datenkern:** `app/data_core.py` – SQLite, Schema, Transaktionen, Todo, Kalenderprojektion, verifizierte Sicherung und Recovery.
5. **API:** `app/server.py` – schmale localhost-only HTTP-Schnittstelle, stabile Fehlercodes und Service-Orchestrierung.
6. **UI-Shell:** A–N, Designsystem, Hilfe, Einstellungen.
7. **Fach-UI:** `app/static/js/data.js` + `data.css` für Todo/Kalender; keine Fachlogik in der Shell duplizieren.
8. **Startup Controller:** echte unabhängige Prüfschritte inklusive Self-Repair, SQLite/WAL und Crashstatus.
9. **Qualität:** Manifest, Unit-/API-/Crash-/Recovery-/Self-Repair-Tests, risikobasierte Agent-Gates und Backuprotation.

## Verantwortungsgrenzen
- `project_store.py` kennt Projektpfad und Konfiguration, entscheidet aber keine SQLite-Recovery.
- `self_repair.py` entscheidet nur, ob eine Reparatur auf der Allowlist eindeutig sicher ist; SQLite selbst bleibt beim `DataCore`.
- `data_core.py` besitzt die Datenintegritäts- und Datenbank-Recovery-Verträge.
- `server.py` übersetzt Serviceergebnisse in lokale API-Verträge und stabile Fehlercodes.
- UI zeigt Status und löst erlaubte Aktionen aus, entscheidet aber keine Reparaturstrategie.

## Projektidentität
Ein in der Konfiguration gespeicherter Projektpfad ist noch kein freigegebenes Projekt. Erst ein inhaltlich gültiger `.provoware/project.json`-Marker aktiviert den Pfad für Fachfunktionen. Ein ungültiger Marker bleibt diagnostizierbar, wird aber nie automatisch neu erfunden.

## Datenprinzip
Todos sind die einzige Quelle für Aufgaben und deren Termine. Der Kalender besitzt keinen zweiten Terminbestand, sondern liest eine Monatsprojektion der aktiven terminierten Todos. Archivieren ist ein reversibler Statuswechsel und kein Löschen.

## Recovery
SQLite läuft im WAL-Modus. Sicherungen werden über die SQLite-Backup-API erzeugt und vor Freigabe mit `PRAGMA quick_check` geprüft. Bei Korruption wird das Original quarantänisiert; automatische Wiederherstellung erfolgt ausschließlich aus einer geprüften Sicherung. Es werden zwei aktuelle DB-Sicherungen gehalten.

Konfigurations-Recovery folgt demselben Muster: nur validierte `.tmp`/`.bak1`/`.bak2`-Quellen, Quarantäne des defekten Originals, atomarer Ersatz und Nachvalidierung.

## Fehlerstrategie
Erwartbare Fehler bleiben typisiert. Breite Exception-Grenzen existieren nur an API-/Prozessgrenzen und protokollieren intern. Die API exponiert stabile Kategorien statt interne Stacktraces. Mehrdeutige oder nicht sicher reparierbare Zustände bleiben unverändert und werden blockierend gemeldet.

## Komplexitätsregel
Neue Schicht nur, wenn sie Abhängigkeiten reduziert, sicherheitskritische Logik zentralisiert oder Wiederverwendung schafft. UI, HTTP, Projektpersistenz, Self-Repair und Datenzugriff bleiben getrennt, damit einzelne Bereiche unabhängig testbar und austauschbar sind.
