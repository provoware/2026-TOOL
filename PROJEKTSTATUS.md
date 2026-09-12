# Projektstatus

## Produktlaufzeit
**v0.3.0 – Jobmanager & reversibles Aktionsjournal**

## Status
🟢 **PR-freigabefähige Implementierung** – der fachliche Implementierungshead `eb7881d7…` bestand das vollständige Release-Gate und alle sieben Subagent-Gates. Nachfolgende reine Evidenz-/Dokumentationscommits müssen vor Merge dieselben Gates erneut bestehen. `main`-Nachvalidierung und reale Snapshotrotation bleiben nach dem Merge zwingend.

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

Worker-interne Start-, Checkpoint-/Heartbeat-, Bestätigungs-, Abschluss- und Fehlerfunktionen bleiben Python-intern. Der Server bleibt localhost-only.

## Automatische PR-Evidenz
Auf Implementierungshead `eb7881d7d0cf15d5b8f1f6e4ff86fd543a68d74d`:
- Release-Gate Run 39: 🟢 alle 16 sichtbaren Stufen erfolgreich.
- Subagent-Gates Run 37: 🟢 Analyse, Risiko, Fehlerursache, Plan, Regression, Plan-Prüfung und Release-Prüfung erfolgreich.
- automatische Gesamt-Discovery: **57 Tests grün**.
- eigener Jobmanager-Gate: 🟢 10 Migration-/Lifecycle-/Resume-/Watchdog-/Journaltests erfolgreich.
- HTTP-API-Vertrag: 🟢 einschließlich Job-/Journal-Endpunkte.
- vorheriger Run 38 fand ausschließlich einen Markdown-Whitespacefehler; alle Fachtests waren bereits grün. Der Whitespacefehler wurde korrigiert und der komplette Gate-Satz anschließend erfolgreich wiederholt.

## Noch offen vor endgültiger Freigabe
1. reine Evidenz-/Dokumentationscommits erneut vollständig über PR-Gates prüfen,
2. Squash-Merge nur auf unverändertem geprüftem Head,
3. Release- und sieben Subagent-Gates erneut auf dem gemergten `main`,
4. reale Snapshot-Backuprotation nach Merge,
5. `backup/snapshots/version-backups/manifest.json` und beide erzeugten Slots gegen die tatsächliche `main`-Historie prüfen.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin nicht durch Branch-Protection/Ruleset geschützt. Automatische Gates sind aktiv, können einen ausreichend berechtigten direkten Push aber nicht technisch verhindern. Dieser Punkt bleibt in `docs/OFFENE_RISIKEN.md` dokumentiert.

## Nächster Produktivschritt nach Freigabe
Auf diesem Job-/Journalfundament kann anschließend der echte Dateisortier-Workflow entstehen:
**Ordner wählen → analysieren → Regeln → Konflikte → Vorschau/Trockenlauf → sichere copy/move-Ausführung → Ergebnis/Übersprungen/Undo.**

## Nutzer-Abnahme
Nicht erforderlich. Automatische Evidenz ersetzt keine Nutzermeinung, aber der Nutzer wird nicht als reguläre Testinstanz eingesetzt.
