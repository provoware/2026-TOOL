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

## 🟡 Iteration 2 – Datenkern v0.2.0 RC
1. [x] SQLite-Service mit WAL, Foreign Keys, Busy Timeout und Schema-Version.
2. [x] transaktionale Schreiblogik und Rollbacktests.
3. [x] Todo D mit optionaler Terminierung, Priorität, Archiv und Wiederherstellung.
4. [x] Kalender E aus derselben Todo-Datenquelle, keine Doppelhaltung.
5. [x] verifizierte DB-Sicherungen, Quarantäne und Recovery.
6. [x] Restart-/Persistenz-, Crash- und Korruptions-Regression.
7. [x] HTTP-API-Vertragstest.
8. [x] Expert-Shell-Regression beibehalten.
9. [x] Datenstandard, Manifest, Hilfe, Architektur und Changelog aktualisieren.
10. [ ] finalen Branch durch unabhängiges GitHub-Release-Gate prüfen.
11. [ ] nach erfolgreichem Gate auf `main` freigeben und Backuprotation prüfen.

## Nächste sinnvolle Ausbaustufe nach Freigabe
- DB-Eingabemaske C als dynamisches Schema-/Formularsystem auf demselben Datenkern.
- globale Suche H über Todo, Notizen, Schnellspeicher und spätere DB-Inhalte.
- Organisationsbereich F weiter ausbauen, ohne Statistikduplikate zu erzeugen.

## Qualitätsregel
Vor Umsetzung zuerst Analyse und dokumentierter Plan. Umsetzung danach automatisch validieren; Plan-Prüfer kontrolliert Abweichungen. Nutzer ist Anwender und nicht reguläre Test- oder Abnahmeinstanz.
