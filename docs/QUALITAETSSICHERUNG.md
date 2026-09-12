# Qualitätssicherung

## Kein manueller Nutzer-Test als Releasebedingung
Freigabe erfolgt über automatische Prüfungen. Nutzerfeedback kann später zusätzliche Anforderungen liefern, ersetzt aber keine Tests.

## Release-Gate
`scripts/validate_all.sh` prüft:
- Pflichtstruktur
- Manifest-Schema und Version
- Python-Syntax
- Server-/Projektservice-Tests
- A–N-Bereiche
- fünf Themes
- Hilfedaten
- Agentenrollen

GitHub Actions führt dasselbe Gate bei Push und Pull Request aus.

## Regression
Bestätigte Fehler erhalten dauerhaft Test, Validierungsregel oder Architekturverbesserung. Künftige Iterationen ergänzen gezielte Fault-Simulationen, Restarttests und Datenbankmigrationstests.

## Rückfall
Zwei Vorgänger von `main` werden als `backup/previous-1` und `backup/previous-2` gehalten. Lokale Konfigurationen besitzen zusätzlich `.bak1` und `.bak2`.
