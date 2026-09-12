# PROVOWARE HEADQUARTER

**Iteration 1 · Expert Shell · v0.1.0**

Lokale, modulare Arbeitszentrale für Kubuntu mit echter Startprüfung, A–N-Shell, fünf Themes, Laie/Profi/Experte, Projektassistent, Hilfesystem und automatischem Qualitätsfundament.

## Start für Laien
1. Repository herunterladen/klonen.
2. `start.sh` doppelklicken bzw. ausführen.
3. Chromium öffnet die lokale Oberfläche automatisch.
4. Beim ersten Start Projektname und Basisordner festlegen.

Es werden keine externen Python-Pakete benötigt. Der Server bindet ausschließlich an `127.0.0.1` und wählt automatisch einen freien Port.

## Automatische Sicherheit
- echte grafische Startroutine statt Fake-Prozentanzeige
- Vor- und Nachvalidierung
- automatisierte Tests ohne Nutzerabnahme
- zwei rotierende Git-Rückfallstände
- atomare Konfiguration mit zwei lokalen Vorgängerkopien
- getrennte Analyse-, Plan- und Prüfrollen
- Manifest als maschinenlesbare Projektwahrheit

## A–N
A Toolinfo · B Einstellungen · C DB-Eingabe · D Todo · E Kalender · F Organisation · G Module · H Suche · I Projekt · J Notiz · K Logging · L Schnellstart · M Schnellspeicher · N Hauptarbeitsbereich.

## Entwicklung
- `AGENTS.md` – verbindliche Regeln
- `.agents/` – Subagenten-Rollen
- `projekt-manifest.json` – Version, UI, Qualität, Backups
- `docs/` – Architektur, Start, Qualität, Agenten
- `scripts/validate_all.sh` – lokales Release-Gate
- `.github/workflows/` – Quality, Agent-Gates, Backuprotation

## Validierung
```bash
./scripts/validate_all.sh
```

Der Nutzer ist Anwender, nicht regulärer Tester.
