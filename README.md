# PROVOWARE 2026-TOOL

Sauberer Projektgrundstand für die iterative Entwicklung des PROVOWARE HEADQUARTER.

## Ziel

Dieses Repository startet bewusst klein. Neue Funktionen werden modular ergänzt und erst nach automatischer Validierung freigegeben.

## Grundprinzipien

- Nutzer ist Anwender, nicht Tester.
- Vorvalidierung vor jeder relevanten Änderung.
- Nachvalidierung nach jeder relevanten Änderung.
- Keine stillen destruktiven Aktionen.
- Fehlerursache beheben, nicht nur Symptome abfangen.
- Jeder bestätigte Fehler erweitert dauerhaft das Regressionswissen.
- Kleine, klar getrennte Module statt großer Monolithen.
- Dokumentation, Tests und Status bleiben mit dem Code synchron.

## Standardstruktur

- `AGENTS.md` – verbindliche Arbeitsregeln für Entwicklungsagenten
- `ENTWICKLUNGSREGELN.md` – technische Projektregeln
- `ENTWICKLERDOKU.md` – technische Dokumentation
- `PROJEKTSTATUS.md` – aktueller freigegebener Stand
- `TODO.md` – geplante Arbeiten
- `CHANGELOG.md` – Versionsänderungen
- `docs/ARCHITEKTUR.md` – Architekturgrundsätze
- `docs/QUALITAETSSICHERUNG.md` – automatisches Qualitäts- und Regressionsmodell
- `scripts/validate_repo.sh` – Strukturprüfung
- `tests/README.md` – Teststrategie

## Startstatus

Repository zurückgesetzt und als neue professionelle Projektbasis initialisiert.
