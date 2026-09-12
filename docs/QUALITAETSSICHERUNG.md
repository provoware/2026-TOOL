# Qualitätssicherung und lernendes Regressionsmanagement

## Grundsatz

Der Nutzer ist Anwender, nicht Tester.

## Automatische Freigabekette

Anforderung → Risikoanalyse → Implementierung → statische Prüfung → Unit-Test → Integrationstest → UI-Test → Fehlersimulation → Persistenztest → Restarttest → Regression → Accessibility → Performancevergleich → Datenintegrität → Release-Gate.

## Lernendes Regressionsmanagement

Jeder bestätigte Fehler erhält:

- Fehler-ID
- Auslöser
- Ursache
- Lösung
- betroffene Komponenten
- dauerhaften Schutz

Fehlerhistorie beeinflusst spätere Risikobewertung und Testauswahl.

## Risikobasierte Regression

Kleine lokale Änderung: gezielte Tests.

Änderung an zentralem Service: Tests aller abhängigen Module.

Migration, Datenbank oder Dateisystem: vollständige Daten-, Recovery-, Backup- und Restart-Prüfung.

## Release-Gate

Keine Freigabe bei:

- kritischem Fehler
- Datenrisiko
- fehlgeschlagener Kernregression
- beschädigter Persistenz
- fehlgeschlagenem Restart/Recovery bei betroffenen Funktionen
