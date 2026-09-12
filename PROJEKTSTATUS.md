# Projektstatus

## Version
0.2.1 – Iteration 2.1 „Reliability & Self-Repair“

## Status
🟡 Release Candidate – Implementierung und Regressionserweiterung abgeschlossen; finale GitHub-PR-Gates und anschließende `main`-Nachvalidierung stehen noch aus.

## Neue Schutzebenen
- konservative Self-Repair-Schicht mit expliziter Allowlist/Denylist
- verifizierte Konfigurations-Recovery mit Quarantäne
- strikte Projektmarker- und Projektstrukturprüfung
- Symlink-Schutz für Projektmarker und Standardordner
- stabilere atomare JSON-Persistenz mit `fsync`
- stabile lokale API-Fehlercodes ohne Offenlegung interner Stacktraces
- Diagnose-Endpunkt ohne Änderungen und separater freigegebener Reparaturlauf
- grafische rote Kennzeichnung blockierender, nicht sicher reparierbarer Zustände

## Agentenmodell v2
- Analyse-Agent
- Risiko-Agent R0–R4
- Fehlerursachen-Agent
- Plan-Agent
- Regressions-Agent
- Plan-Prüfer
- Release-Prüfer

Alle Prüfrollen bleiben read-only gegenüber Produktivcode. R4 ist standardmäßig blockiert.

## Automatische Prüfbasis
- bestehende SQLite-WAL-/Transaktions-/Crash-/Recovery-Regression bleibt erhalten
- Self-Repair-Regression für Konfigurationsrestore, Quarantäne, Fremdordner, fehlende Standardordner, Kollisionen und Symlinks ergänzt
- API-Vertrag um Self-Repair-Status und sicheren Reparaturlauf erweitert
- Shell-Regression um Projektmarker-/Self-Repair-Verträge ergänzt
- Agent-Gate-Risikoklassifikation erhält eigene Regressionstests
- `validate_agents.py` prüft Rollenverträge maschinenlesbar
- vollständiges `validate_all.sh` bleibt zwingendes Release-Gate

## Freigaberegel
Dieser RC darf erst nach erfolgreichem Pull-Request-Release-Gate sowie allen sieben Subagent-Gates auf `main` übernommen werden. Danach müssen dieselben Gates auf dem gemergten `main`-Commit erneut erfolgreich sein und die Zwei-Versionen-Backuprotation muss bestätigt werden.

## Nutzer-Abnahme
Nicht erforderlich. Fehlende automatische Evidenz darf nicht durch manuelles Nutzertesten ersetzt werden.
