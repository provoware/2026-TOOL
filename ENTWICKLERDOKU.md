# Entwicklerdokumentation – v0.1.0

## Laufzeit
Python-Standardbibliothek + HTML/CSS/JavaScript. Keine externen Runtime-Abhängigkeiten.

`start.sh` startet `app/server.py`. Der Server bindet nur localhost, wählt einen freien Port und öffnet bevorzugt Chromium.

## Persistenz
Globale Konfiguration: `~/.config/provoware-headquarter/config.json`. Atomare Speicherung rotiert `.bak1` und `.bak2`.

Projektstruktur: siehe `standards/PROJEKTSTANDARD.md`.

## Frontend
`index.html` hält nur Struktur. `design.css` enthält Design-Tokens und fünf Themes. `app.js` enthält Shell-Interaktionen. `startup.js` kapselt die Startzustandsprüfung.

## API v0.1
- `GET /api/health`
- `GET /api/bootstrap`
- `GET /api/manifest`
- `GET /api/project/pick-base`
- `POST /api/project/create`
- `POST /api/quick-save`

## Erweiterungsregel
Neue Fachmodule werden hinter stabilen Grenzen ergänzt. N bleibt der zentrale Modulhost. Gemeinsame Dateisystem- und Projektlogik darf nicht in einzelne UI-Module kopiert werden.
