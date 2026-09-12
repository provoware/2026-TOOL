# TODO

## 🟢 Iteration 1 – Expert Shell
- [x] A–N-Shell, Startprüfung, Themes, Bedienebenen, Projektbasis, Hilfe und Qualitätsgrundlage.

## 🟢 Iteration 2 – Datenkern v0.2.0
- [x] SQLite WAL/Transaktionen, Todo, Archiv, Kalender, verifizierte Recovery und Crash-/API-Regression.

## 🟢 Iteration 2.1 – Reliability & Self-Repair v0.2.1
- [x] AGENTS.md v2, sieben Prüfrollen, R0–R4, Self-Repair, Quarantäne, Projekt-/Symlink-Schutz und Regression.

## 🟢 Iteration 2.2 – UX, Feedback & Transparenz v0.2.2
- [x] globales Prozessfeedback, Busy-Schutz, Warn-/Fehlerzähler, Zoom 100–200 %, Fokus/ARIA, UX-Standard und UX-Regression.

## 🔵 Iteration 2.3 – Backup Reliability Hotfix v0.2.3
1. [x] roten v0.2.2-Backup-Workflow bis zum konkreten Job-Log analysiert.
2. [x] Root Cause bestimmt: GitHub-App darf historische Workflow-Änderungen nicht per Branch-Ref-Push übernehmen.
3. [x] `backup/snapshots` einmalig als technischer Speicherzweig angelegt.
4. [x] verifizierten `git archive`-Snapshot-Builder ergänzt.
5. [x] zwei Slots `previous-1.zip` / `previous-2.zip` plus Manifest/SHA-256 definiert.
6. [x] ZIP-Integritätsprüfung und vollständige Workflow-Dateien innerhalb der Archive sichergestellt.
7. [x] Backupworkflow so umgebaut, dass auf dem Speicherzweig nur `version-backups/*` verändert wird.
8. [x] Regressionstest mit drei Git-Ständen und veränderten Workflow-Dateien ergänzt.
9. [x] AGENTS.md v2.1 und Qualitätsstandard an neue Backupstrategie angepasst.
10. [ ] vollständiges PR Release-Gate + sieben Subagent-Gates bestehen.
11. [ ] Hotfix nach `main` mergen.
12. [ ] `main` Release-/Subagent-Gates erneut prüfen.
13. [ ] neuen Backupworkflow auf `main` grün prüfen und tatsächliche ZIPs/Manifest auf `backup/snapshots` validieren.

## Danach – erste produktive Fachausbaustufe
- Download-/Dateisortier-Workflow: Ordner wählen → analysieren → Dateitypen → Regeln per Auswahl → Konflikte → Vorschau → sicher kopieren/verschieben → Ergebnis/Undo.
- davor wiederverwendbaren Backend-Jobmanager + Datei-Undo-Journal bereitstellen.

## Qualitätsregel
Nutzer ist Anwender, nicht reguläre Testinstanz. Jede Verhaltensänderung braucht Plan, Vor-/Nachvalidierung und passende Regression; rote Release-/Backup-Gates werden ursachenbasiert behoben statt ignoriert.
