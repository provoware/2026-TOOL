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
1. [x] technischen R3-Plan vor Implementierung erstellt.
2. [x] SQLite-Schema v1 → v2 sicher migriert; bestehende Todos bleiben erhalten und bestehende DB wird vorher verifiziert gesichert.
3. [x] persistenten Jobmanager mit Zustandsmaschine und append-only Ereignissen implementiert.
4. [x] Pause, Resume, Abbruch, Checkpoint und Heartbeat implementiert.
5. [x] Neustart-Recovery und stale-Heartbeat-Watchdog implementiert.
6. [x] transaktionales Datei-Aktionsjournal mit planned/applied/skipped/failed/undone implementiert.
7. [x] Undo-Vertrag umgesetzt: nur angewendete, ausdrücklich reversible Aktionen sind Undo-Kandidaten.
8. [x] lokale Job-/Journal-API ergänzt; Worker-Bestätigungen bleiben service-intern, keine externe Netzwerkfreigabe.
9. [x] Migration-, Lifecycle-, Crash/Resume-, Watchdog-, Journal- und API-Regression bestanden; Gesamt-Discovery: 57 Tests grün.
10. [x] Manifest, Changelog, Projektstatus, Architektur, Qualitätssicherung und Testübersicht synchronisiert.
11. [x] finales PR Release-Gate mit 16 sichtbaren Stufen + alle sieben Subagent-Gates bestanden.
12. [x] nach Squash-Merge `main` erneut vollständig geprüft: Release-Gate Run 42 grün, Subagent-Gates Run 40 alle sieben grün, Snapshot-Backup Run 15 grün; Manifest/Slots gegen die reale Haupt-Historie validiert.

## 🔵 Nächste Ausbaustufe – Dateisortierung als nutzbarer Workflow
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
