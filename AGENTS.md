# AGENTS – verbindliche Entwicklungsordnung

## Oberste Regel
Der Nutzer ist Anwender, nicht regulärer Tester oder Abnahmeinstanz. Eine Änderung gilt erst nach automatischer Vorprüfung, Nachprüfung und betroffener Regression als freigabefähig.

## Rollenfolge
1. **Analyse-Subagent**: nur analysieren; keine Codeänderungen.
2. **Plan-Subagent**: nur Optimierungsplan und Todo dokumentieren; kein Code.
3. **Umsetzung**: kleinstmögliche robuste Änderung gemäß freigegebenem Plan.
4. **Plan-Prüfer**: read-only prüfen, ob Plan, Tests, Dokumentation und Standards eingehalten wurden.
5. **Release-Gate**: automatisierte technische Freigabe.

Die Rollenverträge liegen unter `.agents/` und sind verbindlich.

## Pflichtablauf jeder Änderung
1. Ziel und betroffene Komponenten bestimmen.
2. Risiken und Abhängigkeiten analysieren.
3. TODO/Plan aktualisieren, sofern Code oder Verhalten geändert wird.
4. zwei Rückfallstände sicherstellen.
5. Vorvalidierung ausführen.
6. Änderung modular und codesparsam implementieren.
7. Nachvalidierung ausführen.
8. betroffene Regressionen und Fehlerpfade prüfen.
9. Fehlerursache beheben; keinen Fehler nur verdecken.
10. Manifest, Hilfe, Status und Changelog synchron halten, wenn betroffen.
11. Plan-Konformität prüfen.
12. nur bestandenen Stand freigeben.

## Architekturregeln
- gemeinsame Logik in Services/Komponenten wiederverwenden.
- kein Modul greift unkontrolliert in Interna anderer Module ein.
- keine großen Monolithdateien ohne zwingenden Grund.
- regenerierbare Daten lieber neu aufbauen als riskant reparieren.
- Datenänderungen möglichst atomar/transaktional.
- sichere Fallbacks und verständliche Fehlerzustände vorsehen.
- Komplexität aktiv reduzieren; neue Abstraktion nur bei echtem Wiederverwendungsnutzen.

## Fehler- und Regressionsregel
Jeder bestätigte Fehler hinterlässt mindestens einen dauerhaften Schutz: Regressionstest, Validierungsregel oder Architekturverbesserung. Kritische Fehler dürfen nicht zu Warnungen umetikettiert werden.

## Backups
`main` hält automatisch zwei direkte Vorgänger unter `backup/previous-1` und `backup/previous-2`. Zusätzlich sichern atomar gespeicherte lokale Konfigurationen zwei Vorgängerkopien. Backup ist kein Ersatz für Tests, sondern Rückfallebene.

## Verboten
- Nutzer routinemäßig zum Testen auffordern.
- destruktive Aktion ohne zwingenden Grund und Rückfallstrategie.
- breite `try/except`-Blöcke als Ersatz für Ursachenbehebung.
- Testfehler ignorieren oder als erfolgreich darstellen.
- Analyse-, Plan- oder Prüf-Subagenten zur Implementierung verwenden.
