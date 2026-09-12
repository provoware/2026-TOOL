# Projektstatus

## Produktlaufzeit
**v0.2.2 – UX, Feedback & Transparenz** bleibt unverändert.

## Release-Engineering
**Hotfix v0.2.3 – Backup Reliability**

## Status
🟡 Release Candidate – Root Cause des roten v0.2.2-Backupworkflows behoben; vollständige PR-Gates und anschließende reale `main`-Backupprüfung stehen noch aus.

## Ausgangslage
- v0.2.2 auf `main`: Release-Gate 🟢.
- v0.2.2 auf `main`: siebenstufiges Subagent-Gate 🟢.
- v0.2.2 auf `main`: bisheriger Zweig-Rotationsworkflow 🔴.
- vorhandene Legacy-Rückfallstände selbst blieben korrekt auf v0.2.1 und v0.2.0.

## Bestätigte Root Cause
Der alte Workflow versuchte `backup/previous-1` per `git push --force` auf einen historischen Hauptstand zu setzen. GitHub lehnte den Ref-Push ab, weil der historische Commit geänderte `.github/workflows/quality.yml` enthielt und der Actions-GitHub-App-Token keine spezielle Workflow-Schreibberechtigung besitzt. Dies ist ein Berechtigungs-/Strategieproblem der Zweigrotation, kein Datenbank- oder Nutzdatenfehler.

## Hotfix
- neuer technischer Zweig `backup/snapshots`.
- Snapshot-Builder erzeugt zwei vollständige `git archive`-ZIPs der vorherigen `main`-Stände.
- ZIPs enthalten auch Workflow-Dateien.
- jedes ZIP wird vollständig gelesen/getestet und erhält SHA-256.
- Manifest dokumentiert Commit-ID, SHA-256, Datei- und Größenwerte.
- der Backupworkflow ändert auf `backup/snapshots` ausschließlich `version-backups/*`; Workflow-Dateien dieses Zweigs bleiben unverändert.
- alter Zweigmechanismus bleibt nur als Legacy-Rückfallpunkt bestehen.

## Automatische Regression
- temporäres Git-Repo mit drei Ständen,
- Workflow-Datei ändert sich zwischen den Vorgängern,
- previous-1/previous-2 werden auf exakten Inhalt geprüft,
- ZIP-Test und Manifest-SHA werden geprüft,
- bestehende Shell-, UX-, Datenkern-, Crash-/Recovery-, Self-Repair-, API- und Agentenregression bleibt Bestandteil des Gesamt-Gates.

## Agenten / Qualität
AGENTS.md v2.1 klassifiziert Backup-/Release-Engineering als R3. Ein roter Backupworkflow muss künftig bis zum Job-Log analysiert und mit Root-Cause-Schutz behoben werden; kosmetisches Ignorieren ist ausgeschlossen.

## Offene externe Schutzlücke
`main` ist auf Repositoryebene weiterhin nicht durch Branch-Protection/Ruleset geschützt. Dies ist separat in `docs/OFFENE_RISIKEN.md` dokumentiert und kann nicht durch grüne CI allein ersetzt werden.

## Freigaberegel
1. finaler Hotfix-Head durch Release-Gate und alle sieben Subagent-Gates.
2. Merge nach `main`.
3. Release-/Subagent-Gates auf dem gemergten Stand erneut grün.
4. neuer Backupworkflow auf `main` grün.
5. tatsächliche `previous-1.zip`, `previous-2.zip` und `manifest.json` auf `backup/snapshots` nachprüfen.

## Nutzer-Abnahme
Nicht erforderlich. Automatische Evidenz wird nicht durch manuelles Nutzertesten ersetzt.
