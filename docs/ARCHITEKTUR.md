# Architektur

## Ziel
Die Shell bleibt klein, austauschbar und erweiterbar. Fachmodule dürfen weder Startlogik noch Projektpersistenz, Datenbankzugriffe, Jobzustände oder Reparaturregeln duplizieren.

## Schichten
1. **Bootstrap:** `start.sh`, Serverstart, Sessionmarker.
2. **Projektservice:** `app/project_store.py` – Projektstruktur, atomare Konfiguration, Schnellspeicher und strikte Projektmarker-Prüfung.
3. **Self-Repair:** `app/self_repair.py` – ausschließlich freigegebene, reversible Reparaturregeln, Quarantäne und Diagnose; keine Fachlogik.
4. **Datenkern:** `app/data_core.py` – SQLite, Schema, Transaktionen, Todo, Kalenderprojektion, verifizierte Sicherung und Recovery.
5. **Jobkern:** `app/job_manager.py` – persistente Zustandsmaschine, Checkpoint/Resume, Heartbeat, Watchdog-Recovery, append-only Jobereignisse und reversibles Dateiaktionsjournal.
6. **Sortier-Vorschau:** `app/sorter_preview.py` – read-only Dateisystemanalyse, deterministische Klassifikation, Regelbewertung, persistente Scan-Ergebnisse und Paging. Keine Datei-Mutation.
7. **API:** `app/server.py` – schmale localhost-only HTTP-Schnittstelle, stabile Fehlercodes, Service-Orchestrierung und kontrollierte Hintergrund-Worker für Scan-Jobs.
8. **UI-Shell:** A–N, Designsystem, Hilfe, Einstellungen.
9. **Fach-UI:** `app/static/js/data.js` + `data.css` für Todo/Kalender sowie lazy-loaded `sorter.js` + `sorter.css` für die Sortier-Vorschau; keine Fachlogik in der Shell duplizieren.
10. **Startup Controller:** echte unabhängige Prüfschritte inklusive Self-Repair, SQLite/WAL und Crashstatus.
11. **Qualität:** Manifest, Unit-/API-/Crash-/Recovery-/Self-Repair-/Job-/Journal-/Sortier-Tests, risikobasierte Agent-Gates und Backuprotation.

## Verantwortungsgrenzen
- `project_store.py` kennt Projektpfad und Konfiguration, entscheidet aber keine SQLite-Recovery.
- `self_repair.py` entscheidet nur, ob eine Reparatur auf der Allowlist eindeutig sicher ist; SQLite selbst bleibt beim `DataCore`.
- `data_core.py` besitzt Datenintegrität, zentrale Schema-Migration, WAL, Transaktionen und Datenbank-Recovery.
- `job_manager.py` benutzt denselben `DataCore`; er besitzt Jobzustände, Checkpoints, Heartbeats und Journalregeln.
- `sorter_preview.py` liest ausschließlich Dateisystem-Metadaten der Quelle. Es besitzt Klassifikation, Regelpriorität, Konflikterkennung und den persistenten Scanindex, aber keine copy/move/rename/delete-Operation.
- `server.py` übersetzt Serviceergebnisse in lokale API-Verträge und stabile Fehlercodes. Datenkern, Jobmanager und Sortier-Service werden projektbezogen gecacht; Scans laufen in kontrollierten Daemon-Workern, damit HTTP-Anfragen nicht blockieren.
- `sorter.js` übersetzt die Fachfunktionen in einen Laien-Workflow. Es entscheidet keine Dateisystemänderung und enthält keinen Executor-Endpunkt.
- UI zeigt Status und löst erlaubte Aktionen aus, entscheidet aber weder Reparatur- noch Job-Recovery-Strategie.

## Projektidentität
Ein in der Konfiguration gespeicherter Projektpfad ist noch kein freigegebenes Projekt. Erst ein inhaltlich gültiger `.provoware/project.json`-Marker aktiviert den Pfad für Fachfunktionen. Ein ungültiger Marker bleibt diagnostizierbar, wird aber nie automatisch neu erfunden.

## Datenprinzip
Todos sind die einzige Quelle für Aufgaben und deren Termine. Der Kalender besitzt keinen zweiten Terminbestand, sondern liest eine Monatsprojektion der aktiven terminierten Todos. Archivieren ist ein reversibler Statuswechsel und kein Löschen.

Ab Schema v2 liegen zusätzlich Jobs, Jobereignisse und Dateiaktionsjournal in derselben Projektdatenbank. Es gibt absichtlich keine separaten Job-Statusdateien und keine zweite SQLite-Datenbank.

Die Sortier-Vorschau ergänzt dieselbe Projektdatenbank um ein **Feature-Schema v1** (`sorter_feature_meta`, `sort_scan_entries`). Dieses Feature-Schema erhöht nicht die zentrale `PRAGMA user_version` des Datenkerns; vor seiner erstmaligen Anlage wird trotzdem eine verifizierte SQLite-Sicherung erzeugt. So bleibt der zentrale Datenkern Eigentümer der Datenbank, während das Fachmodul seine zusätzlichen Tabellen explizit versioniert.

## Read-only Sortierprinzip
Die Quelle ist in Iteration 4 strikt read-only. Erlaubt sind nur Verzeichnis-/Metadatenabfragen wie Name, Endung, Größe und Änderungszeit. Dateiinhalte werden für die Sortier-Vorschau nicht gelesen.

Sicherheitsgrenzen:
- Quellwurzel darf kein Symlink sein,
- Symlinks innerhalb der Quelle werden nie verfolgt,
- Rekursion ist standardmäßig aus,
- versteckte sowie bekannte System-/Cachebereiche sind standardmäßig aus,
- verschwundene oder nicht lesbare Einträge werden als `skipped` mit Grund gespeichert statt den Gesamtlauf zu zerstören,
- Scanergebnisse werden zeilenweise und in Batches gespeichert,
- Vorschau wird paginiert statt als unbeschränkte Gesamtliste ausgeliefert.

Regeln sind deterministisch: gesetzte Bedingungsarten werden mit UND verknüpft, Werte innerhalb derselben Liste mit ODER. Höhere Prioritätszahl gewinnt. Haben gleich starke Gewinner unterschiedliche Zielgruppen, entsteht `conflict`; die Software trifft dann keine automatische Zielentscheidung.

## Job-/Dateiaktionsprinzip
Ein Jobzustand darf niemals eine nicht nachgewiesene Dateioperation vortäuschen. `file_actions.status='applied'` bedeutet künftig: reale Operation ausgeführt **und nachvalidiert**. `undone` bedeutet: reale Rückoperation ausgeführt und nachvalidiert. Die Journalmethoden selbst verändern keine Nutzdateien.

Lange Arbeiten speichern Checkpoints und Heartbeats transaktional. Bei Neustart oder abgelaufenem Heartbeat wird ein aktiver Job auf `interrupted` gesetzt; er läuft niemals still automatisch weiter. Für Sortier-Scans startet ein Resume zusätzlich wieder einen echten Scanner-Worker – ein bloßer Datenbankstatus `running` ohne Arbeit ist unzulässig. Details: `docs/JOB_ACTION_CORE.md`.

## Recovery
SQLite läuft im WAL-Modus. Sicherungen werden über die SQLite-Backup-API erzeugt und vor Freigabe mit `PRAGMA quick_check` geprüft. Bei Korruption wird das Original quarantänisiert; automatische Wiederherstellung erfolgt ausschließlich aus einer geprüften Sicherung. Es werden zwei aktuelle DB-Sicherungen gehalten.

Vor einer bestehenden zentralen Schema-Migration wird ebenfalls eine verifizierte SQLite-Sicherung erzeugt. Die Migration v1 → v2 ergänzt Job-/Journalstrukturen, ohne Todo-/Kalenderdaten umzuschreiben. Die erstmalige Sortier-Feature-Schemaanlage ist ebenfalls durch eine verifizierte Sicherung geschützt.

Konfigurations-Recovery folgt demselben Muster: nur validierte `.tmp`/`.bak1`/`.bak2`-Quellen, Quarantäne des defekten Originals, atomarer Ersatz und Nachvalidierung.

## Fehlerstrategie
Erwartbare Fehler bleiben typisiert. Breite Exception-Grenzen existieren nur an API-/Prozessgrenzen und protokollieren intern. Die API exponiert stabile Kategorien statt interne Stacktraces. Mehrdeutige oder nicht sicher reparierbare Zustände bleiben unverändert und werden blockierend gemeldet.

Ungültige Jobzustandswechsel werden als Validierungsfehler blockiert; sie werden nicht durch stilles Korrigieren des Status kaschiert. Bei Datei-Analysefehlern auf Einzelebene wird dagegen kontrolliert weitergearbeitet und der konkrete Eintrag mit `skipped` plus Klartextgrund dokumentiert.

## Komplexitätsregel
Neue Schicht nur, wenn sie Abhängigkeiten reduziert, sicherheitskritische Logik zentralisiert oder Wiederverwendung schafft. UI, HTTP, Projektpersistenz, Self-Repair, Datenzugriff, Jobsteuerung und Sortier-Analyse bleiben getrennt, damit einzelne Bereiche unabhängig testbar und austauschbar sind.
