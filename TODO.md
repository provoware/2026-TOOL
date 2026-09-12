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
- [x] verifizierte Zwei-Slot-Snapshot-Backups statt historischer Ref-Rotation; zwei reale Rotationen erfolgreich nachgewiesen.

## 🟢 Iteration 3 – Jobmanager & reversibles Aktionsjournal v0.3.0
- [x] Jobmanager, Checkpoint/Resume, Watchdog, Aktionsjournal, Undo-Vertrag, 57 Tests, PR-/main-Gates und reale Snapshotrotation vollständig freigegeben.

## 🟡 Iteration 4 – Read-only Sortier-Analyse & Vorschau v0.4.0
1. [x] verbindlichen R3-Plan vor Implementierung angelegt.
2. [x] Scanner-/Regel-Engine als getrennten read-only Service angelegt.
3. [x] persistente, zeilenweise Scan-Ergebnisse in derselben Projekt-SQLite implementiert; erstmalige Feature-Schemaanlage wird vorher verifiziert gesichert.
4. [x] Quellwurzel-Symlinks blockiert; Symlink-Inhalte werden niemals verfolgt.
5. [x] rekursiv standardmäßig aus; versteckte/System-/Cache-Inhalte standardmäßig aus.
6. [x] deterministische Kategorien Bilder/Video/Audio/Dokumente/Archive/Text-Code/Sonstige implementiert.
7. [x] Regelpriorität, Mehrfachtreffer und Konfliktvertrag implementiert; Wortregel kann Dateitypregel überstimmen.
8. [x] tolerantes Verhalten für verschwundene/unlesbare Einträge mit Klartextgrund implementiert.
9. [x] Paging und Scan-Zusammenfassung implementiert.
10. [x] Scanner ausdrücklich als R3 klassifiziert und Agent-Gate-Regression ergänzt.
11. [x] Scanner-Regressionen für Backup/Schema, Nicht-Rekursion, Symlinks, Skip-Gründe, Kategorien, Priorität, Konflikte, Paging und Nicht-Veränderung angelegt.
12. [x] Scanner-/Regeltests im echten GitHub-Gate grün; erster Fehler als unvollständiger `os.scandir()`-Test-Doppelgänger identifiziert, Test repariert, Produktlogik unverändert.
13. [x] localhost-only API für grafische Ordnerauswahl, asynchronen Scanstart, Summary und paginierte Vorschau angebunden.
14. [x] Dateien-Modul lazy-loaded als laienverständlichen Vier-Schritt-Assistenten angebunden.
15. [x] globale Prozessanzeige mit Scanstatus, Dateien, Volumen, Pause/Weiter/Abbruch, Konflikten und Überspringgründen verbunden.
16. [x] Manifest, Changelog, README, Projektstatus, Architektur, Hilfe, Qualitätssicherung und Testübersicht synchronisiert.
17. [ ] finalen v0.4.0-Release-Head mit 76+ Tests, 17 Release-Stufen und allen sieben Subagent-Gates vollständig bestehen.
18. [ ] Squash-Merge auf unverändertem geprüftem Head; danach dieselben Gates auf `main` und reale Snapshotrotation prüfen.

## Danach – sicherer Datei-Executor
1. [ ] Zielordner und Konfliktstrategie ausschließlich nach erfolgreicher Vorschau freigeben.
2. [ ] copy/move mit Vorvalidierung, Nachvalidierung und Aktionsjournal implementieren.
3. [ ] kein stilles Überschreiben und kein endgültiges Löschen als Standard.
4. [ ] parallel veränderte/verschwundene Dateien toleriert überspringen statt Gesamtlauf abzubrechen.
5. [ ] Undo ausschließlich aus nachvalidiertem `applied`-Journalzustand.
6. [ ] Abschlusskarte mit bearbeitet/übersprungen/Fehler/Volumen/Undo/nächster Schritt.
7. [ ] vollständige Crash-/Resume-/Konflikt-/Undo-Regression vor Freigabe.

## Qualitätsregel
Nutzer ist Anwender, nicht reguläre Testinstanz. Jede Verhaltensänderung braucht Plan, Vor-/Nachvalidierung und passende Regression; rote Release-/Backup-Gates werden ursachenbasiert behoben statt ignoriert.
