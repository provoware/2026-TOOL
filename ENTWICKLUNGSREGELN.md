# Entwicklungsregeln

## Architektur

- klare Trennung von UI, Anwendungslogik, Services und Datenhaltung
- gemeinsame Logik zentralisieren
- definierte Schnittstellen zwischen Modulen
- Abhängigkeiten explizit halten
- regenerierbare Daten von Originaldaten trennen

## Sicherheit

- atomare Speicherung für Konfigurationen
- Transaktionen für zusammengehörige Datenbankänderungen
- Vor- und Nachvalidierung bei kritischen Aktionen
- sichere Fallbacks und Recovery statt stiller Datenverluste
- kein endgültiges Löschen als Standardaktion

## Wartbarkeit

- kleine Funktionen mit klarer Verantwortung
- große Dateien als Refactoring-Signal behandeln
- wiederverwendbare Komponenten bevorzugen
- verständliche deutsche Benennung, sofern technisch sinnvoll

## Qualität

- Nutzerabnahme ist kein Testschritt.
- automatische Tests müssen erwartbare Nutzerabläufe abdecken.
- Regressionen werden risikobasiert ausgewählt.
- Kernfunktionen benötigen Restart- und Persistenztests.
