# Architektur

## Leitidee

Das PROVOWARE HEADQUARTER wird als modulare Desktop-Arbeitszentrale aufgebaut. Der zentrale Arbeitsbereich N hostet Module; Navigation, Status, Todo, Kalender, Suche, Projektinformationen und Diagnose bleiben entkoppelte Bestandteile.

## Schichten

1. UI / Darstellung
2. Anwendungslogik
3. Services
4. Datenhaltung
5. Systemintegration

## Kommunikationsregeln

- Module greifen nicht direkt auf Interna anderer Module zu.
- gemeinsame Aktionen laufen über Services oder Commands.
- Zustandsänderungen werden über definierte Events verteilt.
- lange Vorgänge laufen als Jobs und blockieren die UI nicht.

## Fehlerprinzip

lokaler Fehler → lokale Einschränkung → kontrollierter Fallback → Recovery → erst bei echtem Datenrisiko blockieren.
