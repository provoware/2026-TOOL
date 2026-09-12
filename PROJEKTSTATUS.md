# Projektstatus

## Produktlaufzeit
**v0.3.0 – Jobmanager & reversibles Aktionsjournal**

## Status
🟢 **Freigegeben** – Iteration 3 ist technisch auf `main` vollständig nachvalidiert. Der veröffentlichte Laufzeitstand ist Commit `1b889c2a12b6a640bb6015d72bb3a4c4054cfe9f`.

## Freigegebene Basis
- Expert Shell A–N,
- SQLite-WAL-Datenkern, Todo, Kalender und reversibles Archiv,
- Crash-/Recovery-Schutz,
- Reliability & Self-Repair,
- globale UX-/Prozessanzeige, Warn-/Fehlerzähler, Zoom 100–200 %, Fokus/ARIA,
- sieben read-only Prüfrollen mit R0–R4,
- verifizierte Zwei-Slot-Release-Snapshots auf `backup/snapshots`,
- persistenter Jobmanager mit Checkpoint/Resume und Watchdog,
- reversibles Dateiaktionsjournal als Sicherheitsvertrag für kommende Datei-Workflows.

## Iteration 3 – Jobkern
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
Das Aktionsjournal ist bewusst **kein Datei-Executor**. Es darf keine Dateiänderung vortäuschen. Ein späterer Executor muss Quelle und Ziel unmittelbar vor und nach jeder realen Aktion validieren und darf erst danach `applied` setzen. Für Undo gilt dasselbe: erst reale inverse Operation plus Nachvalidierung, dann `undone`.

## Server / Watchdog
`AppContext` verwendet ein gemeinsames Service-Lock für Datenkern und Jobmanager. Der Watchdog läuft als Daemon, prüft Heartbeats regelmäßig und setzt veraltete aktive Jobs auf `interrupted`; automatische Fortsetzung erfolgt nicht.

## API
Freigegeben sind:
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

## Automatische Release-Evidenz
### Pull Request
- finaler PR-Head `16e4461f004af989484e75606e0e2933fa644630`,
- finales PR Release-Gate: 🟢 alle 16 sichtbaren Stufen erfolgreich,
- finale PR Subagent-Gates: 🟢 alle sieben Rollen erfolgreich,
- automatische Gesamt-Discovery: **57 Tests grün**.

### Nach Squash-Merge auf `main`
- veröffentlichter Stand: `1b889c2a12b6a640bb6015d72bb3a4c4054cfe9f`,
- Release-Gate Run 42 (`34701526931`): 🟢 alle 16 Stufen erfolgreich,
- Subagent-Gates Run 40 (`34701526950`): 🟢 Analyse, Risiko, Fehlerursache, Plan, Regression, Plan-Prüfung und Release-Prüfung erfolgreich,
- Snapshot-Backup Run 15 (`34701526895`): 🟢 Erzeugung, Veröffentlichung und Nachvalidierung erfolgreich.

## Tatsächliche Rückfallstände nach v0.3.0
`backup/snapshots/version-backups/manifest.json` wurde nach dem Merge real geprüft:

- `previous-1.zip` → Commit `5a075481f683cba3d411098cc3d21382283ae719`
  - SHA-256: `744296cb41ab5f190c1d20fc7fe264ab2ecca12f3c0364ba77de211352d7a02f`
- `previous-2.zip` → Commit `597f2337bba4eb961b61a4455db4b00824716b69`
  - SHA-256: `5dbb42abad0bb955302387d9d68ee0b00ebbd0eb644d929cd407545f4b49c9c2`

Beide ZIPs wurden vom Backupworkflow auf Integrität geprüft. Ihre Commit-Zuordnung entspricht der tatsächlichen ersten Elternhistorie von `main` unmittelbar vor v0.3.0.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin **nicht** durch Branch-Protection/Ruleset geschützt. Automatische Gates sind aktiv, können einen ausreichend berechtigten direkten Push aber nicht technisch verhindern. Dieser Punkt bleibt in `docs/OFFENE_RISIKEN.md` dokumentiert.

## Nächster Produktivschritt
Als nächste Ausbaustufe folgt der Dateisortier-Workflow. Aus Sicherheitsgründen wird er in zwei Stufen aufgebaut:

1. **read-only Analyse + Regeln + Konflikterkennung + Vorschau/Trockenlauf**, ohne Nutzdateien zu verändern,
2. erst danach **sicherer Executor für Kopieren/Verschieben + Undo**, auf Basis des jetzt freigegebenen Job-/Journalfundaments.

Damit wird reale Dateiänderung erst eingeführt, wenn die Vorschau- und Konfliktlogik automatisch belastbar geprüft ist.

## Nutzer-Abnahme
Nicht erforderlich. Der Nutzer ist Anwender und keine reguläre Testinstanz; technische Freigabe basiert auf automatischer Evidenz.
