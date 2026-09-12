# Projektstatus

## Version
0.2.2 – Iteration 2.2 „UX, Feedback & Transparenz“

## Status
🟡 Release Candidate – UX-Gesamtaudit umgesetzt; automatische PR-Gates stehen noch aus.

## Bereits freigegebene Basis
- Expert Shell A–N
- SQLite-WAL-Datenkern, Todo, Kalender und reversibles Archiv
- Crash-/Recovery-Schutz
- Reliability & Self-Repair v0.2.1
- AGENTS.md v2 mit sieben read-only Prüfrollen und R0–R4

## UX-Ausbau 0.2.2
- globale Status-/Prozessleiste
- realer deterministischer Fortschritt oder ausdrücklich „läuft“ bei unbekannter Gesamtmenge
- Zähler OK / Hinweise / Fehler / übersprungen
- Screenreader-Live-Status und Toast-Feedback
- Skip-Link zum Hauptarbeitsbereich
- Laienführung „Nächster sinnvoller Schritt“
- Schrift bis 200 %
- Kontrast+ unabhängig vom Theme
- mindestens 44 px normale Bedienelemente
- Busy-/Disabled-Schutz gegen Mehrfachauslösung
- klarerer Diagnosebereich K
- verbindlicher UX-Standard für spätere Datei-/Batchprozesse

## Noch bewusst nicht als bewiesen markiert
Statische HTML/CSS/JS-Vertragstests beweisen keine pixelgenaue Darstellung bei jeder Browser-/DPI-/Zoomkombination. Eine spätere echte Browser-/visuelle Regression bei 100/125/150/175/200 % bleibt als zusätzliche Qualitätsstufe sinnvoll.

## Freigaberegel
Erst vollständiges Release-Gate und alle Subagent-Gates auf dem finalen Branch-Head. Danach Merge und dieselben Gates erneut auf `main` plus Backuprotation.

## Nutzer-Abnahme
Nicht erforderlich. Automatische Evidenz darf nicht durch manuelles Nutzertesten ersetzt werden.
