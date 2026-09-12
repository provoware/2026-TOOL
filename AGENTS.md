# AGENTS – verbindliche Entwicklungsregeln

## Auftrag

Entwicklungsagenten arbeiten lösungsorientiert, konservativ bei Datenrisiken und automatisch validierend.

## Pflichtablauf

1. Ziel und betroffene Komponenten bestimmen.
2. Risiken und Abhängigkeiten prüfen.
3. kleinstmögliche robuste Änderung planen.
4. Vorvalidierung ausführen.
5. Änderung implementieren.
6. Nachvalidierung ausführen.
7. betroffene Regressionen ausführen.
8. Fehlerursachen vollständig beheben.
9. Dokumentation, Status und Changelog aktualisieren.
10. nur geprüften Stand freigeben.

## Verboten

- Nutzer als regulären Tester oder Abnahmeinstanz einplanen.
- kritische Fehler als Warnung herunterstufen.
- destruktive Aktionen ohne zwingenden Grund.
- unnötige Komplettumbauten funktionierender Bereiche.
- große unstrukturierte Monolithdateien.
- Fehler nur mit breitem `try/except` verdecken.

## Regressionsregel

Jeder bestätigte Fehler muss mindestens einen dauerhaften Schutz hinterlassen:

- Regressionstest,
- neue Validierungsregel,
- oder Architekturverbesserung, die die Fehlerklasse verhindert.
