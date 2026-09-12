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

## 🔵 Iteration 2.1 – Reliability & Self-Repair v0.2.1
1. [ ] AGENTS.md v2 mit Risikoklassen, Trigger-Matrix, Self-Repair-Grenzen und Freigaberegeln.
2. [ ] Analyse-, Risiko-, Fehlerursachen-, Plan-, Regressions-, Plan-Prüfer- und Release-Prüfer-Rollen sauber trennen.
3. [ ] maschinenlesbare Agentenvertragsprüfung statt einfacher Text-Greps.
4. [ ] zentrale sichere Self-Repair-Schicht mit Allowlist/Denylist.
5. [ ] beschädigte Konfiguration nur aus verifizierter `.bak1`/`.bak2` restaurieren und Original quarantänisieren.
6. [ ] Projektmarker strikt validieren; fremde/ungültige Projektordner niemals automatisch übernehmen.
7. [ ] fehlende Standardordner nur in validierten PROVOWARE-Projekten selbst reparieren.
8. [ ] SQLite-Recovery über bestehenden verifizierenden Datenkern integrieren.
9. [ ] Self-Repair-Status/Run als lokale API und Startprüfung integrieren.
10. [ ] Regressionstests für Konfig-Recovery, Kollisionen, Fremdordnerschutz, Quarantäne, API und Agentenverträge.
11. [ ] Manifest, Hilfe, Architektur, Qualitätsdoku, Changelog und Projektstatus synchronisieren.
12. [ ] vollständigen finalen Branch-Head und danach `main` automatisch validieren.

## Danach – nächste Fachausbaustufe
- DB-Eingabemaske C als dynamisches Schema-/Formularsystem auf demselben Datenkern.
- globale Suche H über Todo, Notizen, Schnellspeicher und spätere DB-Inhalte.
- Organisationsbereich F weiter ausbauen, ohne Statistikduplikate zu erzeugen.

## Qualitätsregel
Vor Umsetzung zuerst Analyse und dokumentierter Plan. Umsetzung danach automatisch validieren; Plan-Prüfer kontrolliert Abweichungen. Nutzer ist Anwender und nicht reguläre Test- oder Abnahmeinstanz.
