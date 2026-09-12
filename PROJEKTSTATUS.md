# Projektstatus

## Basis
🟢 v0.2.1 – Reliability & Self-Repair ist über PR #4 nach `main` gemergt.

## Aktuelle Entwicklung
🔵 Iteration 2.2 – UX, Feedback & Transparenz

Geplanter nächster Release: **v0.2.2**. Die Versionsnummer wird erst nach bestandener Kandidatenprüfung in Laufzeit und Manifest promoviert.

## Bereits implementiert im Kandidaten
- zentrale Prozess-/Feedbackschicht,
- permanente Prozessleiste mit stabilem Platz,
- Warnungs-/Fehlerzähler,
- ARIA-Live-Rückmeldungen mit Symbol + Text,
- Busy-/Doppelausführungsschutz für wichtige Nutzeraktionen,
- Zoom 100–200 % inklusive Tastatur und Strg+Mausrad,
- Skip-Link und größere Standard-Aktionsziele,
- verbesserte leere Zustände und verständlichere Fehlermeldungen,
- Self-Repair, Projektanlage, Schnellspeicher und Todo an gemeinsames Feedback angebunden,
- verbindlicher UX-Standard und automatische UX-Vertragstests,
- separates sichtbares UX-Gate in GitHub Actions.

## Sicherheitsstatus
- keine destruktive neue Fachfunktion,
- Self-Repair-Denylist unverändert aktiv,
- Datenkern/Crash/Recovery bleiben Teil der Gesamtregression,
- Nutzer-Abnahme ist nicht als Releasevoraussetzung vorgesehen.

## Freigabestatus
🟡 Kandidat – vollständiges Release-/Agenten-Gate für Iteration 2.2 steht noch aus.
