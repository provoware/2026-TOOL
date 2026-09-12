# Projektstatus

## Produktlaufzeit
**v0.3.0 – Jobmanager & reversibles Aktionsjournal**

## Status
🟡 **Release Candidate** – Implementierung und Regressionen sind angelegt; vollständige PR-Gates und `main`-Nachvalidierung stehen noch aus.

## Freigegebene Basis aus v0.2.x
- Expert Shell A–N,
- SQLite-WAL-Datenkern, Todo, Kalender und reversibles Archiv,
- Crash-/Recovery-Schutz,
- Reliability & Self-Repair,
- globale UX-/Prozessanzeige, Warn-/Fehlerzähler, Zoom 100–200 %, Fokus/ARIA,
- sieben read-only Prüfrollen mit R0–R4,
- verifizierte Zwei-Slot-Release-Snapshots auf `backup/snapshots`.

## Iteration 3 – neuer Jobkern
- SQLite-Schema v2 in derselben Projektdatenbank,
- verifizierte Sicherung vor bestehender Schema-Migration,
- persistente Job-Zustandsmaschine,
- Checkpoint/Resume, Heartbeat und Resume-Zähler,
- zweistufige Pause/Abbruchsteuerung für aktive Worker,
- automatischer Watchdog für stale Jobs,
- Startup-/Shutdown-Recovery auf `interrupted`,
- append-only Jobereignisse,
- persistentes Dateiaktionsjournal mit `planned/applied/skipped/failed/undone`,
- Undo-Kandidaten nur bei `applied` + `reversible=true`,
- kein endgültiges Löschen und noch keine reale Dateioperation in diesem Iterationsschritt.

## Sicherheitsentscheidung
Das Aktionsjournal ist bewusst **kein Datei-Executor**. Es darf keine Dateiänderung vortäuschen. Ein späterer Executor muss Quelle/Ziel vor und nach jeder realen Aktion validieren und darf erst danach `applied` setzen. Für Undo gilt dasselbe: erst reale inverse Operation + Nachvalidierung, dann `undone`.

## Server / Watchdog
`AppContext` verwendet ein gemeinsames Service-Lock für Datenkern und Jobmanager, damit kein Lock-Reihenfolge-Deadlock entsteht. Der Watchdog läuft als Daemon, prüft Heartbeats regelmäßig und setzt veraltete aktive Jobs auf `interrupted`; automatische Fortsetzung erfolgt nicht.

## API
Neu vorhanden:
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

Worker-interne Bestätigungen bleiben Python-intern. Der Server bleibt localhost-only.

## Neue automatische Evidenz
`tests/test_job_manager.py` deckt ab:
- v1→v2-Migration mit Bestandsschutz,
- Lifecycle und ungültige Übergänge,
- Checkpoint,
- Pause/Resume,
- Abbruch,
- Startup-Recovery,
- Watchdog,
- Aktionsjournal,
- Undo-Regeln,
- Transaktionsrollback.

`tests/test_api_contract.py` deckt zusätzlich den lokalen Job-/Journal-HTTP-Vertrag ab.

## Noch offen vor Freigabe
1. vollständiges Release-Gate auf finalem PR-Head,
2. alle sieben Subagent-Gates,
3. Squash-Merge auf unverändertem geprüften Head,
4. dieselben Gates erneut auf `main`,
5. reale Snapshot-Backuprotation nach Merge und Prüfung der zwei erzeugten Vorgängerslots.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin nicht durch Branch-Protection/Ruleset geschützt. Automatische Gates sind aktiv, können einen ausreichend berechtigten direkten Push aber nicht technisch verhindern. Dieser Punkt bleibt in `docs/OFFENE_RISIKEN.md` dokumentiert.

## Nächster Produktivschritt nach Freigabe
Auf diesem Job-/Journalfundament kann anschließend der echte Dateisortier-Workflow entstehen:
**Ordner wählen → analysieren → Regeln → Konflikte → Vorschau/Trockenlauf → sichere copy/move-Ausführung → Ergebnis/Übersprungen/Undo.**

## Nutzer-Abnahme
Nicht erforderlich. Automatische Evidenz ersetzt keine Nutzermeinung, aber der Nutzer wird nicht als reguläre Testinstanz eingesetzt.
