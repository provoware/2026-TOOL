# TODO

## 🟢 Iteration 1 – Expert Shell
- [x] Startcontroller und echte grafische Startprüfung
- [x] A–N-Shell mit N als Hauptarbeitsbereich
- [x] fünf professionelle Themes
- [x] Laie / Profi / Experte
- [x] Projekt-Ersteinrichtung und Standardordner
- [x] integrierte Hilfe
- [x] zwei Vorgänger-Backups
- [x] Agenten- und Release-Gate-Grundlage

## 🟢 Iteration 2 – Datenkern v0.2.0
- [x] SQLite WAL/Transaktionen, Todo, Archiv, Kalender, Recovery und API-Regression

## 🟢 Iteration 2.1 – Reliability & Self-Repair v0.2.1
- [x] AGENTS.md v2 und R0–R4-Risikomodell
- [x] sieben getrennte read-only Prüfrollen
- [x] maschinenlesbare Agentenvertragsprüfung
- [x] konservative Self-Repair-Allowlist/Denylist
- [x] Config-Recovery + Quarantäne
- [x] strikte Projektmarker-/Strukturprüfung
- [x] Symlink-Schutz für Projektgrenzen
- [x] SQLite-Recovery integriert
- [x] Self-Repair-API und grafische Bedienung
- [x] Self-Repair-/API-/Shell-/Agentenregression
- [x] Release- und Subagent-Gates bestanden und nach `main` gemergt

## 🔵 Iteration 2.2 – UX, Feedback & Transparenz v0.2.2
1. [ ] zentrales Feedback-/Prozessmodell statt verteilter Einzelmeldungen.
2. [ ] globale Statusleiste: aktuelle Aktion, realer Fortschritt, Ergebnis.
3. [ ] Standardzähler: OK / Hinweise / Fehler / übersprungen.
4. [ ] Screenreader-Live-Region und unmittelbare Toast-Rückmeldung.
5. [ ] Schriftregler auf 200 % erweitern und Kontrast+-Modus ergänzen.
6. [ ] Busy/Disabled/Success/Warning/Error-Zustände vereinheitlichen.
7. [ ] Laienführung „Nächster sinnvoller Schritt“ ergänzen.
8. [ ] Diagnosebereich K übersichtlicher und transparenter machen.
9. [ ] UX-Standard für Vorschau → Ausführung → Ergebnis → Undo/Recovery definieren.
10. [ ] „übersprungen und warum“ als Pflichtvertrag für künftige Batchprozesse.
11. [ ] UX-Vertragstests ergänzen; komplette bestehende Regression weiterführen.
12. [ ] finalen Branch-Head und danach `main` automatisch validieren.

## Danach – Fachausbaustufe
- Download-/Dateiregeln: Ordner wählen → analysieren → Dateitypen → Regel per Auswahl → Konfliktprüfung → Vorschau → sicher kopieren/verschieben → Ergebnis/Undo.
- DB-Eingabemaske C als dynamisches Schema-/Formularsystem.
- globale Suche H über Todo, Notizen, Schnellspeicher und spätere DB-Inhalte.

## Qualitätsregel
Nutzer ist Anwender, nicht reguläre Testinstanz. Jede Aktion braucht sichtbares Feedback; jede riskante Aktion braucht Vorvalidierung, sichere Rückfallstrategie und automatische Regression.
