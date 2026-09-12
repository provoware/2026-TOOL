# Architektur

## Ziel
Die Shell bleibt klein, austauschbar und erweiterbar. Fachmodule dürfen weder Startlogik noch Projektpersistenz, Datenbankzugriffe, Jobzustände oder Reparaturregeln duplizieren.

## Schichten
1. **Bootstrap:** `start.sh`, Serverstart, Sessionmarker.
2. **Projektservice:** `app/project_store.py` – Projektstruktur, atomare Konfiguration, Schnellspeicher und strikte Projektmarker-Prüfung.
3. **Self-Repair:** `app/self_repair.py` – ausschließlich freigegebene, reversible Reparaturregeln, Quarantäne und Diagnose; keine Fachlogik.
4. **Datenkern:** `app/data_core.py` – SQLite, Schema, Transaktionen, Todo, Kalenderprojektion, verifizierte Sicherung und Recovery.
5. **Jobkern:** `app/job_manager.py` – persistente Zustandsmaschine, Checkpoint/Resume, Heartbeat, Watchdog-Recovery, append-only Jobereignisse und reversibles Dateiaktionsjournal.
6. **API:** `app/server.py` – schmale localhost-only HTTP-Schnittstelle, stabile Fehlercodes und Service-Orchestrierung.
7. **UI-Shell:** A–N, Designsystem, Hilfe, Einstellungen.
8. **Fach-UI:** `app/static/js/data.js` + `data.css` für Todo/Kalender; keine Fachlogik in der Shell duplizieren.
9. **Startup Controller:** echte unabhängige Prüfschritte inklusive Self-Repair, SQLite/WAL und Crashstatus.
10. **Qualität:** Manifest, Unit-/API-/Crash-/Recovery-/Self-Repair-/Job-/Journal-Tests, risikobasierte Agent-Gates und Backuprotation.

## Verantwortungsgrenzen
- `project_store.py` kennt Projektpfad und Konfiguration, entscheidet aber keine SQLite-Recovery.
- `self_repair.py` entscheidet nur, ob eine Reparatur auf der Allowlist eindeutig sicher ist; SQLite selbst bleibt beim `DataCore`.
- `data_core.py` besitzt Datenintegrität, Schema-Migration, WAL, Transaktionen und Datenbank-Recovery.
- `job_manager.py` benutzt denselben `DataCore`; er besitzt Jobzustände, Checkpoints, Heartbeats und Journalregeln, führt in Iteration 3 aber noch keine Dateioperationen aus.
- `server.py` übersetzt Serviceergebnisse in lokale API-Verträge und stabile Fehlercodes. Datenkern und Jobmanager werden unter einem gemeinsamen Service-Lock verwaltet.
- UI zeigt Status und löst erlaubte Aktionen aus, entscheidet aber weder Reparatur- noch Job-Recovery-Strategie.

## Projektidentität
Ein in der Konfiguration gespeicherter Projektpfad ist noch kein freigegebenes Projekt. Erst ein inhaltlich gültiger `.provoware/project.json`-Marker aktiviert den Pfad für Fachfunktionen. Ein ungültiger Marker bleibt diagnostizierbar, wird aber nie automatisch neu erfunden.

## Datenprinzip
Todos sind die einzige Quelle für Aufgaben und deren Termine. Der Kalender besitzt keinen zweiten Terminbestand, sondern liest eine Monatsprojektion der aktiven terminierten Todos. Archivieren ist ein reversibler Statuswechsel und kein Löschen.

Ab Schema v2 liegen zusätzlich Jobs, Jobereignisse und Dateiaktionsjournal in derselben Projektdatenbank. Es gibt absichtlich keine separaten Job-Statusdateien und keine zweite SQLite-Datenbank.

## Job-/Dateiaktionsprinzip
Ein Jobzustand darf niemals eine nicht nachgewiesene Dateioperation vortäuschen. `file_actions.status='applied'` bedeutet künftig: reale Operation ausgeführt **und nachvalidiert**. `undone` bedeutet: reale Rückoperation ausgeführt und nachvalidiert. Die Journalmethoden selbst verändern keine Nutzdateien.

Lange Arbeiten speichern Checkpoints und Heartbeats transaktional. Bei Neustart oder abgelaufenem Heartbeat wird ein aktiver Job auf `interrupted` gesetzt; er läuft niemals still automatisch weiter. Details: `docs/JOB_ACTION_CORE.md`.

## Recovery
SQLite läuft im WAL-Modus. Sicherungen werden über die SQLite-Backup-API erzeugt und vor Freigabe mit `PRAGMA quick_check` geprüft. Bei Korruption wird das Original quarantänisiert; automatische Wiederherstellung erfolgt ausschließlich aus einer geprüften Sicherung. Es werden zwei aktuelle DB-Sicherungen gehalten.

Vor einer bestehenden Schema-Migration wird ebenfalls eine verifizierte SQLite-Sicherung erzeugt. Die Migration v1 → v2 ergänzt Job-/Journalstrukturen, ohne Todo-/Kalenderdaten umzuschreiben.

Konfigurations-Recovery folgt demselben Muster: nur validierte `.tmp`/`.bak1`/`.bak2`-Quellen, Quarantäne des defekten Originals, atomarer Ersatz und Nachvalidierung.

## Fehlerstrategie
Erwartbare Fehler bleiben typisiert. Breite Exception-Grenzen existieren nur an API-/Prozessgrenzen und protokollieren intern. Die API exponiert stabile Kategorien statt interne Stacktraces. Mehrdeutige oder nicht sicher reparierbare Zustände bleiben unverändert und werden blockierend gemeldet.

Ungültige Jobzustandswechsel werden als Validierungsfehler blockiert; sie werden nicht durch stilles Korrigieren des Status kaschiert.

## Komplexitätsregel
Neue Schicht nur, wenn sie Abhängigkeiten reduziert, sicherheitskritische Logik zentralisiert oder Wiederverwendung schafft. UI, HTTP, Projektpersistenz, Self-Repair, Datenzugriff und Jobsteuerung bleiben getrennt, damit einzelne Bereiche unabhängig testbar und austauschbar sind.
