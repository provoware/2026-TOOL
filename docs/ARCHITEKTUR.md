# Architektur

## Ziel
Die Shell bleibt klein, austauschbar und erweiterbar. Fachmodule dürfen weder Startlogik noch Projektpersistenz duplizieren.

## Schichten
1. **Bootstrap:** `start.sh`, Serverstart, Sessionmarker.
2. **Service:** `ProjectStore`, atomare Persistenz, Projektstruktur, Schnellspeicher.
3. **API:** schmale lokale HTTP-Schnittstelle.
4. **UI-Shell:** A–N, Designsystem, Hilfe, Einstellungen.
5. **Startup Controller:** echte unabhängige Prüfschritte.
6. **Qualität:** Manifest, Tests, Agent-Gates, Backuprotation.

## Komplexitätsregel
Neue Schicht nur, wenn sie Abhängigkeiten reduziert oder Logik mehrfach wiederverwendet. Kleine Fachlogik bleibt lokal; gemeinsame oder sicherheitskritische Logik wird zentralisiert.
