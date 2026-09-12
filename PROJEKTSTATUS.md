# Projektstatus

## Produktlaufzeit
**v0.2.2 – UX, Feedback & Transparenz** bleibt unverändert.

## Release-Engineering
**Hotfix v0.2.3 – Backup Reliability**

## Status
🟡 Release Candidate – beide bisherigen historischen Ref-Strategien sind als nicht tragfähig bestätigt; verifizierte Snapshot-Strategie ist implementiert. PR-Gates und reale Post-Merge-Backupprüfung stehen noch aus.

## Freigegebene Produktbasis
- Expert Shell A–N,
- SQLite-WAL-Datenkern, Todo, Kalender und reversibles Archiv,
- Crash-/Recovery-Schutz,
- Reliability & Self-Repair,
- globale UX-/Prozessanzeige, Warn-/Fehlerzähler, Zoom 100–200 %, Fokus/ARIA,
- sieben read-only Prüfrollen mit R0–R4.

## Backup-Befund – zweimal reproduziert
1. Historischer Ref-Push per `git push --force` scheiterte an der GitHub-App-Workflow-Berechtigungsgrenze, sobald der gesicherte Stand geänderte `.github/workflows/*` enthielt.
2. Der anschließende GitHub-Ref-API-Hotfix (`gh api` PATCH/POST) scheiterte ebenfalls mit HTTP 403 `Resource not accessible by integration`.

Damit wird direkte historische Ref-Rotation mit dem vorhandenen Actions-Token nicht weiter verfolgt.

## Sofortschutz
Die Legacy-Rückfallzweige blieben nach dem ersten Fehler korrekt auf v0.2.1 und v0.2.0. Anwendung und Nutzdaten waren von den Backupworkflow-Fehlern nicht betroffen.

## Neue robuste Primärstrategie
- technischer Speicherzweig `backup/snapshots` ist einmalig außerhalb des Actions-Tokens angelegt,
- zwei vollständige Git-Archive: `previous-1.zip` und `previous-2.zip`,
- vollständige Workflow-Dateien bleiben innerhalb der Archive erhalten,
- ZIP-Integritätsprüfung und SHA-256,
- `manifest.json` mit Commit-ID, Hash, Dateizahl und Größe,
- Rotation darf auf dem Speicherzweig ausschließlich `version-backups/*` verändern,
- eingefrorene `.github/workflows/*` des Speicherzweigs bleiben unangetastet.

## Regression
- vorhandener Workflowvertragstest blockiert Rückkehr zu Force-Push und Ref-API,
- neuer Snapshot-Inhaltstest erzeugt mehrere Git-Stände inklusive geänderter Workflow-Dateien,
- existing Shell-, UX-, Datenkern-, Crash-/Recovery-, Self-Repair-, API- und Agentenregression bleibt vollständig im Release-Gate.

## Agenten / Qualität
AGENTS.md v2.1 behandelt Backup-/Release-Engineering als R3. Auch R1-UI-Änderungen benötigen Regressionsevidenz. Ein roter Backupworkflow wird künftig bis zum Job-Log analysiert und nicht als kosmetischer CI-Fehler akzeptiert.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin nicht durch Branch-Protection/Ruleset geschützt. Dies ist in `docs/OFFENE_RISIKEN.md` ausdrücklich dokumentiert.

## Freigaberegel
1. finaler Snapshot-Hotfix-Head: Release-Gate + sieben Subagent-Gates grün.
2. Merge nach `main` nur auf unverändertem geprüften Head.
3. Release-/Subagent-Gates auf dem gemergten `main` erneut grün.
4. neuer Backupworkflow auf `main` grün.
5. `backup/snapshots/version-backups/manifest.json` und beide ZIP-Slots tatsächlich vorhanden und Commit-Zuordnung korrekt.

## Nutzer-Abnahme
Nicht erforderlich. Automatische Evidenz wird nicht durch manuelles Nutzertesten ersetzt.
