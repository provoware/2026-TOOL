# Iteration 2.2 – UX, Feedback & Transparenz

## Ziel
PROVOWARE soll für Laien jederzeit verständlich zeigen: **Was passiert gerade? Ist alles sicher? Was ist passiert? Was muss ich als Nächstes tun?** Die Oberfläche bleibt modular und wird nicht durch modulspezifische Sonderlogik aufgebläht.

## Audit – wichtigste erkannte Lücken
1. Laufzeitaktionen besitzen noch keine einheitliche globale Prozessanzeige.
2. Erfolg/Warnung/Fehler werden an mehreren Stellen unterschiedlich dargestellt.
3. Warnungs-/Fehlerzähler fehlen als dauerhafte Übersicht.
4. Rückmeldungen können in kleinen Paneltexten übersehen werden.
5. Tastatur-Zoom ist nicht vollständig auf 100–200 % standardisiert.
6. Ein Skip-Link zum Hauptbereich fehlt.
7. Busy-Zustände deaktivieren auslösende Aktionen noch nicht einheitlich.
8. Prozessfeedback soll stabilen Platz besitzen und das Layout nicht springen lassen.
9. Die Hilfe erklärt Funktionen, aber noch nicht das einheitliche Status-/Feedbackmodell.
10. UX-Verträge sind noch nicht maschinenlesbar als Regression abgesichert.

## Umsetzung
1. zentrales `feedback.js` als wiederverwendbarer UI-Service.
2. persistente kompakte Prozessleiste mit Statussymbol, Aktion, Detail, Fortschritt und Aktivitätsanzeige.
3. Session-Zähler für Warnungen und Fehler.
4. ARIA-Live-Toastregion für wichtige Ergebnisse, ohne Farbe als einziges Signal.
5. gemeinsame Busy-Hülle für Nutzeraktionen; Doppelklicks werden während laufender Aktion verhindert.
6. Schrift-/UI-Zoom 100–200 %, persistent; `Ctrl++`, `Ctrl+-`, `Ctrl+0`, `Ctrl+Mausrad`.
7. Skip-Link und klarere Fokusführung.
8. große Standardziele und stabile Statusflächen; `prefers-reduced-motion` respektieren.
9. Self-Repair, Projekterstellung, Schnellspeicher und Todo-Aktionen an das gemeinsame Feedback anbinden.
10. `docs/UX_STANDARD.md` als verbindlicher Standard.
11. `tests/test_ux_contract.py` schützt IDs, ARIA, Zoom, Feedbackservice und Statusmodell.
12. Release-/Agenten-Gates auf finalem Diff erneut ausführen.

## Nicht in dieser Iteration
- keine neue Fachlogik für Dateisortierung oder DB-Formulare,
- kein komplettes Redesign der A–N-Struktur,
- keine Animationen, die für Funktion nötig wären,
- keine manuellen Nutzer-Abnahmetests.

## Fertig-Kriterium
Die bestehenden Funktionen bleiben regressionsfrei; jede wichtige Nutzeraktion besitzt einheitliches, barrierearmes und verständliches Feedback; Prozessstatus ist jederzeit sichtbar; Zoom und Tastaturbedienung sind konsistent; automatische UX-Vertragstests und vollständige Release-Gates sind grün.