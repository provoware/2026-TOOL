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

## 🔵 Iteration 3 – Jobmanager & reversibles Aktionsjournal v0.3.0
1. [x] technischen R3-Plan vor Implementierung erstellt.
2. [ ] SQLite-Schema v1 → v2 sicher migrieren; bestehende Todos unverändert erhalten.
3. [ ] persistenten Jobmanager mit Zustandsmaschine und append-only Ereignissen implementieren.
4. [ ] Pause, Resume, Abbruch, Checkpoint und Heartbeat implementieren.
5. [ ] Neustart-Recovery und stale-Heartbeat-Watchdog implementieren.
6. [ ] transaktionales Datei-Aktionsjournal mit planned/applied/skipped/failed/undone implementieren.
7. [ ] Undo-Vertrag: nur angewendete, ausdrücklich reversible Aktionen rücksetzbar.
8. [ ] lokale Job-/Journal-API ergänzen; keine externe Netzwerkfreigabe.
9. [ ] Migration, Lifecycle, Crash/Resume, Watchdog, Journal und API vollständig regressionsprüfen.
10. [ ] Manifest, Changelog, Status, Qualitätsdoku und Testübersicht synchronisieren.
11. [ ] vollständiges PR Release-Gate + sieben Subagent-Gates bestehen.
12. [ ] nach Merge dieselben Gates auf `main` sowie reale Snapshot-Backuprotation prüfen.

## Danach – Dateisortierung als nutzbarer Workflow
1. [ ] Download-/Quellordner über grafischen Dialog wählen.
2. [ ] vorhandene Dateitypen automatisch analysieren und verständlich gruppieren.
3. [ ] Regeln per Auswahlfeldern/Buttons anbieten; keine Regelsyntax im Laienmodus nötig.
4. [ ] Mehrfachtreffer und Konflikte vor Ausführung sichtbar machen und priorisieren.
5. [ ] Vorschau/Trockenlauf mit Dateien, Anzahl und Datenvolumen.
6. [ ] sicher kopieren/verschieben; kein stilles Überschreiben und kein endgültiges Löschen als Standard.
7. [ ] verschwundene/veränderte Dateien toleriert überspringen und Grund anzeigen statt Gesamtlauf abzubrechen.
8. [ ] globale Prozessanzeige mit bearbeitet/gesamt, Dateien/s, Volumen/s, OK/Hinweis/Fehler/übersprungen.
9. [ ] Abschlusskarte mit Ergebnis, übersprungenen Punkten, Gründen, Undo und nächstem Schritt.
10. [ ] vollständige Regression einschließlich Crash/Resume, Konflikten und paralleler Dateiveränderung.

## Qualitätsregel
Nutzer ist Anwender, nicht reguläre Testinstanz. Jede Verhaltensänderung braucht Plan, Vor-/Nachvalidierung und passende Regression; rote Release-/Backup-Gates werden ursachenbasiert behoben statt ignoriert.
