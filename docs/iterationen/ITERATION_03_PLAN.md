# Iteration 3 – Jobmanager & reversibles Aktionsjournal

## Ziel
Iteration 3 legt das sichere Ausführungsfundament für den ersten produktiven Dateisortier-Workflow. Noch keine automatische Datei-Verschiebung und kein endgültiges Löschen.

Produktversion: **v0.3.0**  
Risikoklasse: **R3** – Datenbankmigration, Recovery, Dateipfade, Undo-/Resume-Verträge.

## Architekturentscheidung
- dieselbe projektbezogene SQLite-Datenbank bleibt die einzige Wahrheit,
- Schema-Migration **v1 → v2** erweitert den bestehenden Datenkern,
- Migration erzeugt vor einer bestehenden Datenbank wie bisher eine verifizierte Sicherung,
- `app/job_manager.py` kapselt Zustandsmaschine, Checkpoints, Watchdog und Aktionsjournal,
- `DataCore` bleibt Eigentümer von Verbindung, WAL, Transaktionen, Migration und Recovery,
- Server-API bleibt localhost-only und dependency-frei.

## Job-Zustände
`queued → running → completed`

Kontrollierte Nebenpfade:
- `running → paused → running`,
- `running → cancelling → cancelled`,
- `queued|paused|interrupted → cancelled`,
- `running|cancelling → interrupted` nach Crash/Neustart/Watchdog,
- `interrupted → running` bei Resume,
- `running → failed` bei kontrolliertem Fehler.

Ungültige Übergänge werden blockiert und protokolliert.

## Persistente Jobdaten
Je Job mindestens:
- UUID,
- Typ,
- Status und Phase,
- Nutzlast als JSON,
- Checkpoint als JSON,
- Ergebnis als JSON,
- Fehlercode/-text,
- Fortschritt Einheiten/Bytes,
- Pause-/Abbruchanforderung,
- Heartbeat,
- Start-/Endzeit,
- Resume-Zähler,
- Erstell-/Änderungszeit.

Zusätzlich append-only `job_events` für nachvollziehbare Zustandsänderungen.

## Watchdog / Recovery
- Beim Initialisieren des Jobmanagers werden liegengebliebene `running`/`cancelling`-Jobs nicht fortgesetzt, sondern sicher auf `interrupted` gesetzt.
- Ein Watchdog kann Jobs mit veraltetem Heartbeat ebenfalls auf `interrupted` setzen.
- Resume geschieht nur explizit über die Zustandsmaschine.
- Checkpoints werden transaktional mit Fortschrittsdaten gespeichert.
- Keine Dateioperation wird allein aus einem Jobstatus abgeleitet oder erfunden.

## Reversibles Aktionsjournal
Tabelle `file_actions` ist das spätere Sicherheitsprotokoll für Dateioperationen.

Pro Aktion:
- Job-ID + monotone Sequenz,
- Aktionstyp (`copy`, `move`, `rename`, `mkdir`),
- Quelle/Ziel,
- Zustand (`planned`, `applied`, `skipped`, `failed`, `undone`),
- reversibel ja/nein,
- Vorher-/Nachher-Metadaten JSON,
- Grund/Fehler,
- Zeitpunkte.

Regeln:
- Journalplanung verändert niemals Dateien.
- `applied` darf nur aus `planned` entstehen.
- `undone` darf nur aus `applied` + `reversible=true` entstehen.
- `skipped`/`failed` bleiben erklärbar und werden nicht still verworfen.
- Undo-Dateioperationen selbst kommen erst mit dem späteren sicheren Executor; diese Iteration liefert den verlässlichen Vertrag und die Persistenz.

## API-Scope
Neue lokale Endpunkte für:
- Job erstellen/listen/lesen,
- Pause/Resume/Abbruch anfordern bzw. kontrolliert bestätigen,
- Checkpoint/Heartbeat,
- Job abschließen/fehlschlagen,
- Aktionsjournal lesen.

Keine frei erreichbare Netzwerkbindung; bestehende stabile Fehlercodes bleiben erhalten.

## Regression
Pflichttests:
1. v1→v2-Migration erhält bestehende Todos.
2. Job-Lifecycle und ungültige Übergänge.
3. Checkpoint + Resume.
4. Pause und Abbruch.
5. Neustart-Recovery `running → interrupted`.
6. Watchdog bei stale heartbeat.
7. Aktionsjournal Reihenfolge und Zustandsregeln.
8. Undo nur für angewendete reversible Aktion.
9. Transaktionsrollback bei Fehler.
10. bestehende Shell-, Datenkern-, Self-Repair-, API-, UX-, Agenten- und Backupregression bleibt grün.

## Nicht in dieser Iteration
- keine rekursive Dateisuche,
- keine Dateityp-Regeln,
- keine echte copy/move-Ausführung,
- kein endgültiges Löschen,
- keine automatische Konfliktentscheidung,
- keine neue komplexe UI.

## Done-Kriterien
- Schema v2 mit sicherer Migration und Backup,
- Jobmanager vollständig persistent,
- Crash-/Watchdog-Recovery automatisch getestet,
- Aktionsjournal transaktional und zustandsvalidiert,
- API-Vertrag getestet,
- Manifest/Changelog/Status/Qualitätsdoku synchron,
- vollständiges Release-Gate + sieben Subagent-Gates auf finalem PR-Head,
- nach Merge dieselben Gates auf `main`,
- reale Snapshot-Backuprotation nach Merge erneut grün.
