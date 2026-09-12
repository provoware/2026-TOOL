# TODO

## 🟢 Iteration 1 – Expert Shell
- [x] Startcontroller und echte grafische Startprüfung
- [x] A–N-Shell mit N als Hauptarbeitsbereich
- [x] fünf professionelle Themes
- [x] Laie / Profi / Experte
- [x] Projekt-Ersteinrichtung und Standardordner
- [x] integrierte Hilfe
- [x] zwei Vorgänger-Backups
- [x] Analyse-, Plan- und Plan-Prüfer-Rollen
- [x] Manifest- und Release-Gate-Grundlage

## 🟢 Iteration 2 – Datenkern v0.2.0
1. [x] SQLite-Service mit WAL, Foreign Keys, Busy Timeout und Schema-Version.
2. [x] transaktionale Schreiblogik und Rollbacktests.
3. [x] Todo D mit optionaler Terminierung, Priorität, Archiv und Wiederherstellung.
4. [x] Kalender E aus derselben Todo-Datenquelle, keine Doppelhaltung.
5. [x] verifizierte DB-Sicherungen, Quarantäne und Recovery.
6. [x] Restart-/Persistenz-, Crash- und Korruptions-Regression.
7. [x] HTTP-API-Vertragstest.
8. [x] Expert-Shell-Regression beibehalten.
9. [x] Datenstandard, Manifest, Hilfe, Architektur und Changelog aktualisieren.
10. [x] vollständigen Iterationsdiff durch unabhängiges GitHub-Release-Gate prüfen.
11. [x] Analyse-, Plan- und Plan-Prüfer-Gates für den vollständigen Diff bestanden.

## 🟢 Iteration 2.1 – Reliability & Self-Repair v0.2.1
1. [x] AGENTS.md v2 mit Risikoklassen, Trigger-Matrix, Self-Repair-Grenzen und Freigaberegeln.
2. [x] sieben getrennte Prüfrollen.
3. [x] maschinenlesbare Agentenvertragsprüfung.
4. [x] sichere Self-Repair-Schicht mit Allowlist/Denylist.
5. [x] Konfigurations-Recovery mit Quarantäne.
6. [x] Projektmarker-/Fremdordner-/Symlink-Schutz.
7. [x] SQLite-Recovery und Regression.
8. [x] PR #4 validiert und nach `main` gemergt.

## 🟢 Iteration 2.2 – UX, Feedback & Transparenz v0.2.2
1. [x] zentrales wiederverwendbares Feedback-/Prozesssystem.
2. [x] permanente kompakte Prozessleiste ohne Layoutsprünge.
3. [x] Warnungs-/Fehlerzähler und wichtige ARIA-Live-Rückmeldungen.
4. [x] einheitliche Busy-Zustände gegen Doppelklick/Doppelausführung.
5. [x] Zoom 100–200 % plus `Ctrl++`, `Ctrl+-`, `Ctrl+0` und `Ctrl+Mausrad`.
6. [x] Skip-Link, Fokusführung und größere Standard-Aktionsziele.
7. [x] Projekt, Self-Repair, Schnellspeicher und Todo an gemeinsames Feedback angebunden.
8. [x] Hilfe um Status-/Prozessmodell ergänzt.
9. [x] `docs/UX_STANDARD.md`, UX-Audit und UX-Vertragstests ergänzt.
10. [x] Kandidaten-Release-Gate und sieben Agenten-Gates bestanden; v0.2.2 promoviert.

## Danach – nächste Fachausbaustufe
- Download-/Dateisortier-Workflow als erster unmittelbar produktiver Laien-Workflow.
- DB-Eingabemaske C als dynamisches Schema-/Formularsystem auf demselben Datenkern.
- globale Suche H über Todo, Notizen, Schnellspeicher und spätere DB-Inhalte.

## Qualitätsregel
Vor Umsetzung zuerst Analyse und dokumentierter Plan. Umsetzung danach automatisch validieren; Plan-Prüfer kontrolliert Abweichungen. Nutzer ist Anwender und nicht reguläre Test- oder Abnahmeinstanz.
