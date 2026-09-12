# Qualitätssicherung

## Kein manueller Nutzer-Test als Releasebedingung
Freigabe erfolgt über automatische Prüfungen. Nutzerfeedback kann zusätzliche Anforderungen liefern, ersetzt aber keine technische Abnahme.

## Risikomodell R0–R4
- **R0:** Dokumentation ohne Laufzeitwirkung.
- **R1:** Darstellung/UX.
- **R2:** Fachlogik/API/Validierung.
- **R3:** Persistenz, Projektstruktur, DB, Recovery, Backup, Migration, Startlogik, Jobsteuerung, CI/Release oder Sicherheitsgrenzen.
- **R4:** destruktiv/irreversibel; standardmäßig blockiert.

R1–R3 benötigen passende Regressionsevidenz. R3 verlangt zusätzlich – soweit betroffen – Restart-, Crash-, Recovery-, Teilzustands- und Rückfallprüfungen.

## Release-Gate
`scripts/validate_all.sh` prüft:
1. Pflichtstruktur,
2. Manifest/Verträge,
3. sieben Agentenrollen,
4. Python-Syntax,
5. JavaScript-Syntax,
6. Jobmanager/Migration/Resume/Journal,
7. UX-Vertrag,
8. Backup-Workflow-Vertrag,
9. Backup-Snapshot-Inhalt,
10. vollständige Regression,
11. Diff-/Patch-Hygiene.

GitHub Actions führt dieselben Verträge granular auf Pull Requests und nach Merge auf `main` erneut aus. Die Jobmanager-Regression besitzt zusätzlich eine eigene sichtbare CI-Stufe.

## Subagent-Gates
`Analyse → Risiko → Fehlerursache → Plan → Regression → Plan-Prüfung → Release-Prüfung`.

Die Rollen schreiben keinen Produktivcode. `scripts/validate_agents.py` prüft Rollenverträge, Manifestzuordnung und Workflow-Verdrahtung maschinenlesbar.

## Jobmanager-/Journal-Qualität
Iteration 3 ist R3. Pflichtevidenz:
- bestehende Schema-v1-Datenbank migriert auf v2 und behält bestehende Todos,
- vor bestehender Migration wird eine verifizierte SQLite-Sicherung erzeugt,
- ungültige Jobzustandswechsel verändern keinen Zustand,
- Pause/Resume/Abbruch folgen der definierten Zustandsmaschine,
- Checkpoint und Fortschritt werden transaktional gespeichert,
- Neustart markiert aktive Jobs als `interrupted`, statt Arbeit zu erfinden,
- stale Heartbeats werden vom Watchdog als `interrupted` markiert,
- Dateiaktionsjournal hält monotone Sequenz und strenge Zustandswechsel,
- Undo ist nur für `applied` + `reversible=true` möglich,
- ein Fehler nach Aktionsplanung rollt die gesamte Transaktion zurück,
- HTTP-API veröffentlicht nur Nutzer-/UI-nahe Jobsteuerung; Worker-Bestätigungen bleiben Service-intern.

Das Journal ist kein Datei-Executor. `applied`/`undone` darf ein späterer Executor erst **nach** realer Dateioperation und Nachvalidierung setzen. Diese Trennung ist ein Architekturvertrag, kein Hinweistext.

## Self-Repair-Qualität
Self-Repair ist eine Allowlist eindeutig sicherer Reparaturen. Jeder automatische Eingriff muss reversibel bzw. durch Quarantäne abgesichert und nachvalidiert sein. Verboten sind insbesondere Nutzerdatenlöschung, Fremdordnerübernahme, erfundene Projektmarker, ungeprüfte Backups und automatische Entscheidungen bei mehrdeutigen Nutzerständen.

## Regression / Regressionsgedächtnis
Bestätigte Fehler erhalten dauerhaft Test, Validierungsregel oder Architekturverbesserung. Der Schutz umfasst je nach Fehlerklasse Crash, Neustart, Recovery, Quarantäne, API, Jobzustand, Watchdog, Journal und Release-Engineering. Ein wiederkehrender bereits behobener Fehler gilt zusätzlich als Defekt des Regressionsmanagements.

## Release-Backup – zwei vollständige Vorgängerversionen
Die frühere Rotation von `backup/previous-1` und `backup/previous-2` ist als Primärmechanismus abgelöst. Ursache: GitHub verweigert einem Actions-App-Token das Verschieben eines Branches auf einen Commit, wenn dadurch geänderte `.github/workflows/*` übernommen würden und die spezielle Workflow-Berechtigung fehlt.

Die robuste Primärstrategie ist:
- technischer Zweig `backup/snapshots`,
- `version-backups/previous-1.zip`,
- `version-backups/previous-2.zip`,
- `version-backups/manifest.json`.

Die ZIPs entstehen direkt mit `git archive` aus den beiden vorherigen `main`-Ständen und enthalten daher auch deren Workflow-Dateien. Vor Veröffentlichung werden ZIP-Struktur und Lesbarkeit geprüft; das Manifest enthält Commit-ID und SHA-256. Die Rotation auf `backup/snapshots` darf ausschließlich `version-backups/*` ändern. Damit werden auf dem technischen Zweig keine Workflow-Dateien durch das Actions-Token verändert.

Die alten Backup-Zweige bleiben als zusätzliche Legacy-Rückfallpunkte bestehen. Lokale Konfigurationen besitzen `.bak1`/`.bak2`; SQLite hält zwei verifizierte Sicherungen. Backup ersetzt keine Validierung – auch Restore muss prüfbar sein.

## Backup-Fehler sind Release-Fehler
Ein roter Backup-Workflow wird nicht als kosmetischer CI-Fehler akzeptiert. Vorgehen: Job-Log lesen → konkrete Root Cause → Architekturfix → Regressionstest → PR-Gates → `main`-Nachprüfung → tatsächlichen Snapshotzweig und Manifest prüfen.

## Fehlercodes
Die lokale API nutzt stabile Kategorien wie `VALIDATION`, `NOT-FOUND`, `CONFLICT`, `PERMISSION`, `DATA-INTEGRITY` und `INTERNAL`. Interne Stacktraces werden nicht an die UI ausgegeben; Details bleiben im Log.
