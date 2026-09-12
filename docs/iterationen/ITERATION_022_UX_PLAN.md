# Iteration 2.2 – UX, Feedback & Transparenz

## Ziel
PROVOWARE soll für Laien jederzeit beantworten: Was passiert gerade? Ist alles sicher? Was wurde erledigt, übersprungen oder blockiert? Was ist der nächste sinnvolle Schritt?

## Audit-Ergebnis
### Bereits stark
- echte gewichtete Startprüfung statt Fake-Fortschritt
- A–N-Flächenmodell mit dominantem Hauptarbeitsbereich
- fünf Themes, Laie/Profi/Experte, sichtbarer Fokus und Reduced Motion
- Self-Repair mit klarer Sicherheitsgrenze
- Todo/Archiv/Kalender mit reversiblen Aktionen

### Noch zu verbessern
1. Feedback ist auf mehrere kleine Textstellen und Log K verteilt; kein einheitliches globales Feedbackmodell.
2. Außer der Startroutine existiert noch keine wiederverwendbare Prozessanzeige für spätere Datei-/Scan-/Sortierjobs.
3. Kein standardisierter Zähler für OK / Hinweis / Fehler / übersprungen.
4. Kein globales Screenreader-Live-Feedback für alle Aktionen.
5. Schriftregler endet bei 160 %, Ziel ist 200 %.
6. Kein separater Kontrast+-Modus unabhängig vom Theme.
7. Busy/Disabled/Success/Error-Zustände sind nicht für alle Aktionen vereinheitlicht.
8. Kein zentraler „nächster Schritt“ für den Laienmodus.
9. K ist als Diagnosefläche zu klein und zeigt keine klare Trennung zwischen Kurzstatus und Details.
10. Für künftige Dateiaktionen fehlt ein Standard für Vorschau → Ausführung → Ergebnis → Undo sowie „übersprungen und warum“.

## Umsetzung 2.2
1. zentrale Feedback-/Prozessschicht `feedback.js`.
2. immer sichtbare globale Status-/Prozessleiste mit realem Fortschritt.
3. standardisierte Zähler OK / Hinweise / Fehler / übersprungen.
4. Toast + ARIA-Live-Region für unmittelbares Feedback.
5. Schriftgröße bis 200 % und Kontrast+-Schalter.
6. konsistente Busy-/Disabled-/Statusdarstellung.
7. Laienkarte „Nächster sinnvoller Schritt“ im Hauptarbeitsbereich.
8. K als klarer Diagnosebereich mit Self-Repair und sichtbarem Status.
9. `UX_STANDARD.md` als verbindlicher Vertrag für kommende Dateifunktionen.
10. statische UX-Vertragstests und bestehende Regression vollständig weiterführen.

## Definition of Done
- keine Aktion ohne sichtbares Feedback.
- Prozessanzeige kann determinate und indeterminate Jobs darstellen.
- Farbe nie alleinige Statusinformation.
- 100–200 % Schrift/Zoom ohne absichtliches Abschneiden kritischer Bedienung.
- Tastaturfokus sichtbar; globale Meldungen Screenreader-tauglich.
- „übersprungen“ hat immer einen Grund.
- riskante Dateifunktionen müssen später Vorschau und Undo/Recovery besitzen.
- Release erst nach vollständigem Gate.
