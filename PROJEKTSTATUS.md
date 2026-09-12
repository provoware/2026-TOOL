# Projektstatus

## Version
0.2.2 – Iteration 2.2 „UX, Feedback & Transparenz“

## Status
🟢 Release Candidate technisch freigeprüft – vollständiges Release-Gate und alle sieben Subagent-Gates auf dem RC-Head bestanden. Es fehlen nur noch erneute Prüfung des finalen Dokumentations-Heads, Merge auf `main`, `main`-Nachvalidierung und Backupkontrolle.

## Freigeprüfte Basis
- Expert Shell A–N
- SQLite-WAL-Datenkern, Todo, Kalender und reversibles Archiv
- Crash-/Recovery-Schutz
- Reliability & Self-Repair v0.2.1
- AGENTS.md v2.1 mit sieben read-only Prüfrollen und R0–R4

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
- UI-/UX-Änderungen R1 benötigen künftig eigene Regressionsevidenz

## Automatische Evidenz RC-Head
- Release-Gate vollständig erfolgreich.
- Repository-Struktur, Manifest, Agentenverträge, Python- und JavaScript-Syntax erfolgreich.
- Shell-, Datenkern-/Crash-/Recovery-, Self-Repair-, HTTP/API-, Agentenrisiko- und UX-Vertrag erfolgreich.
- gesamte Test-Discovery erfolgreich.
- Analyse, Risiko, Fehlerursache, Plan, Regression, Plan-Prüfung und Release-Prüfung erfolgreich.

## Noch bewusst nicht als bewiesen markiert
Statische HTML/CSS/JS-Vertragstests beweisen keine pixelgenaue Darstellung bei jeder Browser-/DPI-/Zoomkombination. Eine echte Browser-/visuelle Regression bei 100/125/150/175/200 % bleibt als zusätzliche Qualitätsstufe sinnvoll.

## Bekannte offene Schutzlücke
Der GitHub-Branch `main` ist repositoryseitig weiterhin nicht geschützt. Die automatischen Gates prüfen zuverlässig, können einen direkten administrativen Push aber ohne Branch-Protection/Ruleset nicht technisch verhindern. Dies ist transparent in `docs/OFFENE_RISIKEN.md` dokumentiert.

## Freigaberegel
Finalen Dokumentations-Head erneut vollständig prüfen. Erst danach PR #6 mergen. Anschließend denselben gemergten Stand auf `main` erneut validieren und die Zwei-Versionen-Backuprotation bestätigen.

## Nutzer-Abnahme
Nicht erforderlich. Automatische Evidenz darf nicht durch manuelles Nutzertesten ersetzt werden.
