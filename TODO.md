# TODO

## 🟢 Iteration 1 – Expert Shell
- [x] A–N-Shell, Startprüfung, Themes, Bedienebenen, Projektbasis, Hilfe und Qualitätsgrundlage.

## 🟢 Iteration 2 – Datenkern v0.2.0
- [x] SQLite WAL/Transaktionen, Todo, Archiv, Kalender, verifizierte Recovery und Crash-/API-Regression.

## 🟢 Iteration 2.1 – Reliability & Self-Repair v0.2.1
- [x] AGENTS.md v2, sieben Prüfrollen, R0–R4, Self-Repair, Quarantäne, Projekt-/Symlink-Schutz und Regression.

## 🟢 Iteration 2.2 – UX, Feedback & Transparenz v0.2.2
- [x] globales Prozessfeedback, Busy-Schutz, Warn-/Fehlerzähler, Zoom 100–200 %, Fokus/ARIA, UX-Standard und UX-Regression.

## 🟢 Iteration 2.3 – Backup Reliability Hotfix v0.2.3
1. [x] roten v0.2.2-Backup-Workflow bis zum konkreten Job-Log analysiert.
2. [x] Root Cause bestimmt: historische Ref-Rotation ist mit dem vorhandenen GitHub-App-Token nicht zuverlässig möglich.
3. [x] Force-Push-Variante real reproduziert und verworfen.
4. [x] GitHub-Ref-API-Variante real reproduziert (HTTP 403) und verworfen.
5. [x] `backup/snapshots` einmalig als technischer Speicherzweig angelegt.
6. [x] verifizierten `git archive`-Snapshot-Builder ergänzt.
7. [x] zwei Slots `previous-1.zip` / `previous-2.zip` plus Manifest/SHA-256 definiert.
8. [x] ZIP-Integritätsprüfung und vollständige Workflow-Dateien innerhalb der Archive sichergestellt.
9. [x] Backupworkflow so umgebaut, dass auf dem Speicherzweig nur `version-backups/*` verändert wird.
10. [x] Workflow- und Snapshot-Inhaltsregression ergänzt.
11. [x] AGENTS.md v2.1 und Qualitätsstandard an neue Backupstrategie angepasst.
12. [x] vollständiges PR Release-Gate + sieben Subagent-Gates bestanden.
13. [x] Hotfix als Squash-Commit `597f2337…` nach `main` gemergt.
14. [x] `main` Release-Gate erneut bestanden.
15. [x] `main` siebenstufiges Subagent-Gate erneut bestanden.
16. [x] neuer realer Backupworkflow auf `main` erfolgreich.
17. [x] `backup/snapshots` nachgeprüft: Manifest sowie beide ZIP-Slots vorhanden, Commit-Zuordnung und SHA-256 dokumentiert.

## 🔵 Nächste produktive Fachausbaustufe
### Dateisortierung – erster wirklich nutzbarer Workflow
1. [ ] wiederverwendbaren Backend-Jobmanager mit Pause, Abbruch, Checkpoint/Resume und Watchdog entwickeln.
2. [ ] transaktionales Datei-Aktionsjournal für Vorschau, Ausführung, Fehler und Undo/Recovery entwickeln.
3. [ ] Download-/Quellordner über grafischen Dialog wählen.
4. [ ] vorhandene Dateitypen automatisch analysieren und verständlich gruppieren.
5. [ ] Regeln per Auswahlfeldern/Buttons anbieten; keine Regelsyntax im Laienmodus nötig.
6. [ ] Mehrfachtreffer und Konflikte vor Ausführung sichtbar machen und priorisieren.
7. [ ] Vorschau/Trockenlauf mit Dateien, Anzahl und Datenvolumen.
8. [ ] sicher kopieren/verschieben; kein stilles Überschreiben und kein endgültiges Löschen als Standard.
9. [ ] verschwundene/veränderte Dateien toleriert überspringen und Grund anzeigen statt Gesamtlauf abzubrechen.
10. [ ] globale Prozessanzeige mit bearbeitet/gesamt, Dateien/s, Volumen/s, OK/Hinweis/Fehler/übersprungen.
11. [ ] Abschlusskarte mit Ergebnis, übersprungenen Punkten, Gründen, Undo und nächstem Schritt.
12. [ ] vollständige Regression einschließlich Crash/Resume, Konflikten und paralleler Dateiveränderung.

## Qualitätsregel
Nutzer ist Anwender, nicht reguläre Testinstanz. Jede Verhaltensänderung braucht Plan, Vor-/Nachvalidierung und passende Regression; rote Release-/Backup-Gates werden ursachenbasiert behoben statt ignoriert.
