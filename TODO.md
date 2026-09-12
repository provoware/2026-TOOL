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
2. [x] Analyse-, Risiko-, Fehlerursachen-, Plan-, Regressions-, Plan-Prüfer- und Release-Prüfer-Rollen sauber trennen.
3. [x] maschinenlesbare Agentenvertragsprüfung statt einfacher Text-Greps.
4. [x] zentrale sichere Self-Repair-Schicht mit Allowlist/Denylist.
5. [x] beschädigte Konfiguration nur aus verifizierter Rückfallkopie restaurieren und Original quarantänisieren.
6. [x] Projektmarker strikt validieren; fremde/ungültige Projektordner niemals automatisch übernehmen.
7. [x] fehlende Standardordner nur in validierten PROVOWARE-Projekten selbst reparieren.
8. [x] SQLite-Recovery über bestehenden verifizierenden Datenkern integrieren.
9. [x] Self-Repair-Status/Run als lokale API und Startprüfung integrieren.
10. [x] Regressionstests für Konfig-Recovery, Kollisionen, Fremdordnerschutz, Quarantäne, API und Agentenverträge.
11. [x] Manifest, Hilfe, Architektur, Qualitätsdoku, Changelog und Projektstatus synchronisieren.
12. [x] vollständigen Branch-Head validiert und über PR #4 nach `main` gemergt.

## 🔵 Iteration 2.2 – UX, Feedback & Transparenz
1. [ ] zentrales wiederverwendbares Feedback-/Prozesssystem.
2. [ ] permanente kompakte Prozessleiste ohne Layoutsprünge.
3. [ ] Warnungs-/Fehlerzähler und wichtige ARIA-Live-Rückmeldungen.
4. [ ] einheitliche Busy-Zustände gegen Doppelklick/Doppelausführung.
5. [ ] Zoom 100–200 % plus `Ctrl++`, `Ctrl+-`, `Ctrl+0` und `Ctrl+Mausrad`.
6. [ ] Skip-Link, Fokusführung und größere Standard-Aktionsziele.
7. [ ] Projekt, Self-Repair, Schnellspeicher und Todo an gemeinsames Feedback anbinden.
8. [ ] Hilfe um Status-/Prozessmodell ergänzen.
9. [ ] `docs/UX_STANDARD.md` und UX-Vertragstests ergänzen.
10. [ ] vollständige Regression und sieben Agenten-Gates bestehen.

## Danach – nächste Fachausbaustufe
- Download-/Dateisortier-Workflow als erster unmittelbar produktiver Laien-Workflow.
- DB-Eingabemaske C als dynamisches Schema-/Formularsystem auf demselben Datenkern.
- globale Suche H über Todo, Notizen, Schnellspeicher und spätere DB-Inhalte.

## Qualitätsregel
Vor Umsetzung zuerst Analyse und dokumentierter Plan. Umsetzung danach automatisch validieren; Plan-Prüfer kontrolliert Abweichungen. Nutzer ist Anwender und nicht reguläre Test- oder Abnahmeinstanz.
