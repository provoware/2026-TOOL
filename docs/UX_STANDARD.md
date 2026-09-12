# UX-Standard – PROVOWARE HEADQUARTER

## Leitfrage
Der Nutzer muss ohne technische Vorkenntnisse jederzeit beantworten können:
1. **Was kann ich hier tun?**
2. **Was passiert gerade?**
3. **War es erfolgreich oder gibt es ein Problem?**
4. **Was wurde verändert oder übersprungen?**
5. **Was ist der nächste sichere Schritt?**

## Feedbackmodell
Jede relevante Aktion verwendet dieselben Zustände:
- `BEREIT` – keine Aktion läuft.
- `ARBEITET` – sichtbare Aktivität; auslösende Aktion gegen Doppelausführung sperren.
- `ERFOLG` – Ergebnis in Klartext.
- `HINWEIS` – nutzbar, aber Aufmerksamkeit sinnvoll.
- `FEHLER` – Aktion nicht erfolgreich oder Zustand blockiert.

Farbe ist niemals die einzige Information. Jeder Zustand besitzt Symbol + Klartext + semantischen Status.

## Prozessanzeige
- permanente kompakte Fläche unter dem Header; feste Mindesthöhe gegen Layoutsprünge,
- aktuelle Aktion und Detailtext,
- Fortschritt 0–100 %, wenn messbar,
- ansonsten klarer Aktivitätszustand statt erfundener Prozentwerte,
- letzte Aktion bleibt kurz nachvollziehbar,
- Warnungs- und Fehlerzähler bleiben für die Sitzung sichtbar.

## Laienmodus
- Hauptaktion sprachlich als Ergebnis formulieren: „Projekt sicher anlegen“, „Sicher reparieren“, „Aufgabe speichern“.
- technische Details nicht als Voraussetzung für eine Entscheidung verwenden.
- erweiterte Optionen in `Profi`/`Experte`, Sicherheitsprüfungen bleiben immer aktiv.
- leere Zustände erklären nicht nur, dass nichts vorhanden ist, sondern was als Nächstes möglich ist.

## Fehlertexte
Reihenfolge:
1. Was ist passiert?
2. Welche Auswirkung hat es?
3. Wurde etwas verändert?
4. Was ist die nächste sichere Aktion?

Interne Tracebacks gehören ins Log, nicht in die normale Laienmeldung.

## Barrierefreiheit
- vollständige Tastaturbedienung,
- Skip-Link zum Hauptbereich,
- sichtbarer Fokus,
- ARIA-Live nur für wichtige Statusänderungen,
- Zoom 100–200 % persistent,
- `Ctrl++`, `Ctrl+-`, `Ctrl+0`, `Ctrl+Mausrad`,
- Standard-Aktionsziele mindestens etwa 44 px hoch; kompakte Hilfsaktionen nur bei ausreichendem Abstand,
- `prefers-reduced-motion` respektieren,
- keine Information ausschließlich über Farbe, Position oder Animation.

## Layoutstabilität
- Live-Dateinamen, Pfade, Logs und Statusmeldungen dürfen keine Hauptbereiche verschieben.
- lange Texte umbrechen oder werden in einer begrenzten Fläche dargestellt.
- N behält Priorität als Hauptarbeitsbereich.
- Prozess- und Statusflächen besitzen reservierten Platz.

## Transparenz
K zeigt technische Ereignisse in vereinfachter Form. Die globale Prozessleiste zeigt den aktuellen Nutzerprozess. Beide erfüllen unterschiedliche Aufgaben und dürfen nicht durch unkontrolliertes Textwachstum das Layout verändern.

## Entwicklungsvertrag
Neue Nutzeraktionen müssen vor Freigabe mindestens prüfen:
- verständlicher Ausgangszustand,
- Busy-/Doppelausführungsschutz,
- Erfolgsmeldung,
- Fehlerzustand,
- Tastaturzugang,
- Zoomtauglichkeit,
- keine Layoutverschiebung durch dynamischen Text,
- Regressionstest für die notwendigen UX-Vertragsmerkmale.
