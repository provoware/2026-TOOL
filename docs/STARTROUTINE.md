# Startroutine v0.2.1

Die Startanzeige zeigt ausschließlich echte Prüfschritte. Der Prozentwert ergibt sich aus den Gewichten abgeschlossener Schritte; es gibt keine künstliche Fortschrittsanimation.

## Prüfreihenfolge
1. lokaler Dienst – 8 %
2. Projektmanifest – 7 %
3. Konfiguration/Profil – 8 %
4. Self-Repair und Schutzgrenzen – 12 %
5. Projektstatus/Projektmarker – 7 %
6. SQLite-Datenkern/WAL/Recovery – 15 %
7. A–N-Layout – 9 %
8. fünf Themes – 6 %
9. Browser-Persistenz – 7 %
10. Hilfesystem – 5 %
11. Modulregister – 7 %
12. Sitzungs-/Crashstatus – 9 %

Summe: 100 %.

## Self-Repair beim Start
Vor dem Laden des Projektservices wird eine beschädigte Konfiguration nur dann automatisch repariert, wenn eine verifizierte `.tmp`, `.bak1` oder `.bak2` vorhanden ist. Das defekte Original wird quarantänisiert. Ein konfigurierter Projektpfad wird anschließend nur dann repariert oder für den Datenkern freigegeben, wenn sein PROVOWARE-Projektmarker vollständig valide ist.

Fehlende Standardordner eines validierten Projekts dürfen automatisch neu erzeugt werden. Dateikollisionen, ungültige Marker und nicht verifizierbare Zustände werden nicht verändert.

## Statuslogik
- **Grün:** Prüfung vollständig bestanden.
- **Gelb:** nichtkritischer Hinweis oder bereits sicher reparierter Zustand.
- **Rot/blockierend:** kritische Shell-/Manifestprüfung oder ein Zustand, für den keine eindeutig sichere automatische Lösung existiert.

Ein Self-Repair-Befund mit blockierender Mehrdeutigkeit wird nicht durch einen riskanten Reparaturversuch verdeckt. Fachfunktionen erhalten keinen Projektzugriff, solange die Projektidentität nicht validiert ist.

## Abgesicherter Modus
Bei kritischem UI-/Startfehler bleibt ein abgesicherter Oberflächenmodus erreichbar. Dieser Modus ist kein Ersatz für Datenintegritätsprüfung und darf keine blockierte Datenbank oder einen ungültigen Projektmarker freigeben.
