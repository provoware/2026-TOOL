# Jobmanager & reversibles Aktionsjournal

## Zweck
Der Jobkern ist die gemeinsame Ausführungsbasis für lange oder unterbrechbare Arbeiten wie Dateianalyse, Kopieren, Verschieben, Duplikatprüfung und spätere Medienjobs. Er trennt **Auftragszustand** von **Dateioperation**.

## Eine Datenquelle
Jobs, Jobereignisse und Dateiaktionsjournal liegen in derselben projektbezogenen `provoware.sqlite3` wie Todo/Kalender. Dadurch existieren keine konkurrierenden Statusdateien.

SQLite-Vertrag:
- Schema v2,
- WAL,
- Foreign Keys,
- `BEGIN IMMEDIATE` für Schreibtransaktionen,
- Migration v1 → v2 nur nach verifizierter Datenbanksicherung,
- bestehende v1-Todos bleiben unverändert erhalten.

## Job-Zustandsmaschine
Normale Folge:

`queued → running → completed`

Kontrollpfade:
- `running → paused → running`,
- `running → cancelling → cancelled`,
- `queued|paused|interrupted → cancelled`,
- `running|cancelling → interrupted` bei Neustart oder stale Heartbeat,
- `interrupted → running` bei explizitem Resume,
- `running|cancelling → failed` bei kontrolliertem Fehler.

Ungültige Übergänge ergeben `VALIDATION` und verändern den persistierten Zustand nicht.

## Pause und Abbruch
Pause/Abbruch sind zweistufig, sobald ein Worker aktiv ist:
1. Nutzer/API setzt eine Anforderung.
2. Worker erreicht einen sicheren Checkpoint und bestätigt die Anforderung.

Dadurch wird ein Kopier-/Verschiebevorgang später nicht mitten in einem unklaren Teilschritt als „pausiert“ behauptet.

Ein noch nicht gestarteter, pausierter oder unterbrochener Job kann ohne Worker sofort auf `cancelled` gesetzt werden.

## Checkpoint / Resume
Ein Checkpoint speichert transaktional:
- Phase,
- Einheiten bearbeitet/gesamt,
- Bytes bearbeitet/gesamt,
- fachlichen Resume-Cursor als JSON,
- Heartbeat.

Resume erhöht einen persistenten Resume-Zähler. Ein Checkpoint darf nur für `running` oder `cancelling` geschrieben werden.

## Watchdog
`AppContext` besitzt einen automatischen Daemon-Watchdog.
- Prüfintervall: 10 Sekunden.
- Standard-Stale-Grenze: 30 Sekunden.
- `running`/`cancelling` ohne frischen Heartbeat werden auf `interrupted` gesetzt.
- Beim Neuaufbau des Jobmanagers werden noch aktive Zustände ebenfalls auf `interrupted` gesetzt.
- Es wird **nicht** automatisch weitergearbeitet; Fortsetzung ist explizit.

Beim sauberen Programmende werden noch aktive Jobs vor der finalen DB-Sicherung ebenfalls als `interrupted` gespeichert. Damit behauptet der nächste Start keinen weiterlaufenden Prozess.

## Append-only Jobereignisse
`job_events` dokumentiert u. a.:
- created,
- started,
- checkpoint,
- pause-requested / paused,
- resumed,
- cancel-requested / cancelled,
- interrupted / watchdog-interrupted,
- completed / failed,
- action-planned / action-applied / action-skipped / action-failed / action-undone.

Die Ereignisse sind Nachweis/Audit und nicht die primäre Zustandsquelle; aktueller Zustand steht in `jobs` bzw. `file_actions`.

## Dateiaktionsjournal
Iteration 3 unterstützt bewusst nur den **Vertrag**, noch keine echte Dateiänderung.

Aktionstypen:
- `copy`,
- `move`,
- `rename`,
- `mkdir`.

Kein endgültiges Löschen.

Zustände:
- `planned`: nur geplant, keine Dateiänderung behauptet,
- `applied`: Executor hat ausgeführt und muss vorher/nachher validiert haben,
- `skipped`: bewusst übersprungen, Grund ist Pflicht,
- `failed`: Ausführung fehlgeschlagen, Grund ist Pflicht,
- `undone`: eine angewendete reversible Aktion wurde real rückgängig gemacht und danach validiert.

## Strenge Regel für den späteren Executor
Der spätere Datei-Executor darf die Journalmethoden nur in dieser Reihenfolge benutzen:

1. `plan_action()` vor jeder Dateiänderung.
2. Quelle/Ziel unmittelbar vor Ausführung erneut prüfen.
3. Dateioperation ohne stilles Überschreiben ausführen.
4. Quelle/Ziel nach Ausführung prüfen.
5. Erst danach `mark_action_applied()`.

Bei verschwundener/veränderter Quelldatei: `skipped` oder `failed` mit Klartextgrund statt Gesamtabbruch.

Für Undo:
1. nur `undo_candidates()` verwenden,
2. reale inverse Dateioperation ausführen,
3. Ergebnis nachvalidieren,
4. erst danach `mark_action_undone()`.

`mark_action_undone()` ist kein Dateibefehl. Es bestätigt ausschließlich eine bereits erfolgreich ausgeführte Rückoperation.

## Reversibilität
Eine Aktion ist nur Undo-Kandidat, wenn:
- Status `applied`,
- `reversible = true`.

Nichtreversible Aktionen können nicht durch bloße Statusänderung als rückgängig markiert werden.

## HTTP-Schnittstelle
Nutzer-/UI-nahe API:
- `GET /api/jobs`
- `GET /api/jobs/summary`
- `GET /api/jobs/<id>`
- `GET /api/jobs/<id>/events`
- `GET /api/jobs/<id>/actions`
- `GET /api/jobs/<id>/undo-candidates`
- `POST /api/jobs`
- `POST /api/jobs/<id>/pause`
- `POST /api/jobs/<id>/resume`
- `POST /api/jobs/<id>/cancel`

Worker-interne Zustandsbestätigungen bleiben Python-Servicefunktionen und werden nicht als allgemeine HTTP-Schreibendpunkte veröffentlicht.

## Sicherheitsgrenzen dieser Iteration
- keine echte copy/move/rename/mkdir-Ausführung über HTTP,
- kein Delete,
- keine automatische Konfliktentscheidung,
- keine Übernahme fremder Verzeichnisse,
- keine automatische Fortsetzung nach Crash,
- keine zweite Datenbank,
- keine manuellen JSON-/Statusdateien neben SQLite.
