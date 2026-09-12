# Qualitätssicherung

## Kein manueller Nutzer-Test als Releasebedingung
Freigabe erfolgt über automatische Prüfungen. Nutzerfeedback kann zusätzliche Anforderungen liefern, ersetzt aber keine technische Abnahme.

## Risikomodell R0–R4
- **R0:** Dokumentation ohne Laufzeitwirkung.
- **R1:** Darstellung/UX.
- **R2:** Fachlogik/API/Validierung.
- **R3:** Persistenz, Projektstruktur, DB, Recovery, Backup, Migration, Startlogik, Jobsteuerung, Dateisystemanalyse, CI/Release oder Sicherheitsgrenzen.
- **R4:** destruktiv/irreversibel; standardmäßig blockiert.

R1–R3 benötigen passende Regressionsevidenz. R3 verlangt zusätzlich – soweit betroffen – Restart-, Crash-, Recovery-, Teilzustands- und Rückfallprüfungen.

## Release-Gate
`scripts/validate_all.sh` prüft:
1. Pflichtstruktur,
2. Manifest/Verträge,
3. sieben Agentenrollen,
4. Python-Syntax,
5. JavaScript-Syntax inklusive lazy-loaded Sortier-UI,
6. Jobmanager/Migration/Resume/Journal,
7. read-only Sortier-Analyse/Regeln/Vorschau,
8. UX-Vertrag,
9. Backup-Workflow-Vertrag,
10. Backup-Snapshot-Inhalt,
11. vollständige Regression,
12. Diff-/Patch-Hygiene.

GitHub Actions führt die Verträge granular auf Pull Requests und nach Merge auf `main` erneut aus. Der sichtbare Release-Workflow besitzt derzeit 17 Schritte; Sortier-Analyse und HTTP-API werden separat geprüft, damit Fehlerursachen nicht in einer Gesamtprüfung verborgen bleiben.

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

## Sortier-Vorschau-Qualität
Iteration 4 ist R3, obwohl die Quelle read-only bleibt. Grund: Sie liest reale Dateisystemstrukturen, schreibt einen persistenten Scanindex und hängt an Job-/Recovery-Verträgen.

Pflichtevidenz:
- Quellwurzel-Symlink wird blockiert,
- rekursiv ist standardmäßig aus,
- versteckte sowie bekannte System-/Cachebereiche sind standardmäßig aus,
- Symlinks im Baum werden sichtbar übersprungen und nie verfolgt,
- Dateikategorien sind deterministisch,
- Wortregeln mit höherer Priorität können allgemeine Dateitypregeln überstimmen,
- gleich starke unterschiedliche Ziele ergeben `conflict`,
- verschwundene oder nicht lesbare Einträge werden `skipped`, der Restscan läuft weiter,
- Scanresultate bleiben persistent und paginierbar,
- Quelldateien bleiben in Inhalt, Namen und Zeitstempeln unverändert,
- API-Start ist asynchron und blockiert den HTTP-Server nicht,
- Resume eines Scannerjobs startet wieder einen echten Worker statt nur den Jobstatus umzuschalten,
- UI enthält keinen Executor-Endpunkt und kennzeichnet den Ablauf ausdrücklich als „Nur analysieren – nichts verändern“.

Ein bestätigter Testfehler beim ersten Scanner-Gate wurde als Test-Doppelgängerfehler identifiziert: Der simulierte `os.scandir()`-Iterator war nicht iterierbar. Die Produktlogik wurde nicht verändert; der Test-Doppelgänger wurde an den realen `ScandirIterator`-Vertrag angepasst und derselbe vollständige Gate-Satz anschließend erfolgreich wiederholt.

## Self-Repair-Qualität
Self-Repair ist eine Allowlist eindeutig sicherer Reparaturen. Jeder automatische Eingriff muss reversibel bzw. durch Quarantäne abgesichert und nachvalidiert sein. Verboten sind insbesondere Nutzerdatenlöschung, Fremdordnerübernahme, erfundene Projektmarker, ungeprüfte Backups und automatische Entscheidungen bei mehrdeutigen Nutzerständen.

## Regression / Regressionsgedächtnis
Bestätigte Fehler erhalten dauerhaft Test, Validierungsregel oder Architekturverbesserung. Der Schutz umfasst je nach Fehlerklasse Crash, Neustart, Recovery, Quarantäne, API, Jobzustand, Watchdog, Journal, Scanner, UX und Release-Engineering. Ein wiederkehrender bereits behobener Fehler gilt zusätzlich als Defekt des Regressionsmanagements.

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
