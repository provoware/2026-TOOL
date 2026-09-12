# Changelog

## 0.2.2 – 2026-09-12
### Nutzerfreundlichkeit & Transparenz
- zentrale globale Feedback-/Prozessschicht statt verteilter Einzelmeldungen.
- immer sichtbarer Gesamtstatus mit aktueller Aktion und optional realem Fortschritt.
- einheitliche Zähler für OK, Hinweise, Fehler und Übersprungen.
- unbekannte Gesamtmengen zeigen „läuft“ statt erfundener Prozentwerte.
- Toast-Rückmeldung und globale Screenreader-Live-Region.
- Skip-Link direkt zum Hauptarbeitsbereich.
- Laienführung „Nächster sinnvoller Schritt“ abhängig von Projekt-/Sicherheitsstatus.
- Schriftregler bis 200 % und zusätzlicher Kontrast+-Modus unabhängig vom Theme.
- normale Bedienelemente auf mindestens 44 px Zielhöhe gehärtet.
- Navigation setzt `aria-current`; Hauptarbeitsbereich erhält kontrolliertes Fokusmanagement.
- Busy-Zustände verhindern Mehrfachauslösung bei Projektanlage, Self-Repair und Schnellspeicher.
- Diagnosebereich K klarer benannt und Logfläche vergrößert.

### Prozessstandard
- neuer verbindlicher `docs/UX_STANDARD.md`.
- künftige Datei-/Batchfunktionen müssen Phase, Fortschritt, OK/Hinweis/Fehler/Übersprungen und Überspringgrund ausgeben.
- riskante Dateiaktionen folgen Analyse → Regeln → Konfliktprüfung → Vorschau/Trockenlauf → Bestätigung → Ausführung → Ergebnis → Undo/Recovery.
- kein stilles Überschreiben und kein endgültiges Löschen als Standard.

### Qualität
- eigener UX-Vertragstest für Feedback, 200-%-Skalierung, Kontrast+, Prozesslebenszyklus und Datei-Sicherheitsvertrag.
- Release-Workflow zeigt UX-Vertrag als separates Gate.
- bestehende Shell-, Datenkern-, Crash-/Recovery-, Self-Repair-, API- und Agentenregression bleibt vollständig erhalten.

## 0.2.1 – 2026-09-12
### Robustheit & Self-Repair
- getrennte `app/self_repair.py`-Schicht für sichere, reversible Reparaturen.
- verifizierte Config-Recovery mit Quarantäne, strikte Projektmarker-/Strukturprüfung und Symlink-Schutz.
- stabile API-Fehlercodes und grafischer Self-Repair in Bereich K.
- AGENTS.md v2 mit sieben Prüfrollen und Risikomodell R0–R4.
- R4 wird standardmäßig blockiert; Test-/Qualitätsverträge sind gegen stilles Entfernen geschützt.

## 0.2.0 – 2026-09-12
- SQLite-WAL-Datenkern, Todo D, Kalender E, reversibles Archiv und verifizierte Recovery.

## 0.1.0 – 2026-09-12
- Expert Shell A–N, echte Startpipeline, fünf Themes, drei Bedienebenen, Projektassistent und Qualitätsgrundlage.
