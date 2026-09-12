# UX-Standard – PROVOWARE

## Ziel
So simpel wie möglich, ohne Komfort oder Sicherheit zu verlieren. Laien sehen primär die nächste sinnvolle Entscheidung; Profi/Experte dürfen mehr Details sehen. Sicherheitslogik bleibt in allen Stufen identisch.

## 1. Jede Aktion braucht Feedback
Jede Nutzeraktion muss mindestens einen sichtbaren Zustand besitzen: bereit → aktiv/busy → Erfolg, Hinweis oder Fehler. Busy deaktiviert Mehrfachauslösung. Fehler nennen in einfacher Sprache Wirkung und nächsten sicheren Schritt.

## 2. Prozessvertrag
Längere Prozesse verwenden die zentrale Prozessleiste. Wenn Gesamtmenge bekannt ist, wird realer Fortschritt gezeigt. Wenn sie unbekannt ist, steht „läuft“ statt erfundener Prozentwerte. Reale Aktivität und fachlicher Fortschritt dürfen nicht verwechselt werden.

Pflichtinformationen für Batch-/Scan-/Dateijobs:
- aktuelle Phase,
- bearbeitet / gesamt, wenn bekannt,
- OK,
- Hinweise,
- Fehler,
- übersprungen,
- Grund für jedes Überspringen,
- Abschlussstatus,
- Ergebnisort bzw. Undo/Recovery-Hinweis.

Ein einzelner tolerierbarer Dateifehler beendet keinen Gesamtlauf unnötig.

## 3. Statusfarben
Farbe ist nie die einzige Information.
- 🟢 Erfolg / sicher
- 🔵 aktiv / Information
- 🟡 Hinweis / Entscheidung
- 🟠 automatisch behebbar bzw. Recovery
- 🔴 blockierend / kritisch
- ⚪ übersprungen / nicht geprüft
Immer zusätzlich Symbol und Klartext.

## 4. Laienführung
Im Laienmodus wird ein „Nächster sinnvoller Schritt“ hervorgehoben. Erweiterte Optionen bleiben über progressive Offenlegung erreichbar. Noch nicht implementierte Module dürfen nicht wie fertige Funktionen wirken.

## 5. Riskante Dateiaktionen
Verbindlicher Ablauf:
1. Quelle wählen.
2. automatisch analysieren.
3. Regeln verständlich konfigurieren.
4. Konflikte und Mehrfachtreffer vorab zeigen.
5. Vorschau/Trockenlauf.
6. Nutzer bestätigt die konkrete Wirkung.
7. sicher kopieren/verschieben.
8. veränderte oder verschwundene Quelldateien toleriert überspringen und begründen.
9. Ergebnisbericht.
10. Undo/Recovery anbieten, soweit technisch möglich.

Kein stilles Überschreiben. Kein endgültiges Löschen als Standard.

## 6. Barrierefreiheit
- vollständige Tastaturbedienung und sichtbarer Fokus,
- Screenreader-Live-Status für wichtige Zustandsänderungen,
- Skip-Link zum Hauptarbeitsbereich,
- mindestens 44 px Bedienhöhe für normale Controls,
- Schrift/Zoom 100–200 % ohne absichtliches Abschneiden kritischer Bedienung,
- Kontrast+ unabhängig vom Theme,
- Reduced-Motion respektieren,
- Status nicht nur farblich kommunizieren.

## 7. Layoutstabilität
Live-Texte dürfen das Grundlayout nicht springen lassen. Lange Pfade und Dateinamen umbrechen oder werden in stabilen Scrollflächen dargestellt. Bei kleinem Viewport/großer Schrift wird der Hauptarbeitsbereich priorisiert und Navigation horizontal kompakt erreichbar.

## 8. Fehlerzentrum / Diagnose
Kurzstatus bleibt verständlich. Technische Details gehören in Diagnose/Log. Self-Repair darf ausschließlich freigegebene reversible Fehlerklassen automatisch beheben. Blockierte Fälle bleiben sichtbar und unverändert.

## 9. Qualitätsgate
Neue UI-Funktionen müssen statisch auf Feedbackvertrag, Fokus-/ARIA-Grundlagen, 200-%-Skalierung und Prozesszustände geprüft werden. Für größere UI-Änderungen ist zusätzlich eine echte visuelle/Browser-Regression sinnvoll; statische Tests allein beweisen keine perfekte Darstellung.
