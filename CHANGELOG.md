# Changelog

## 0.2.2 – 2026-09-12 – UX, Feedback & Transparenz
### Nutzerführung
- permanente kompakte Prozessleiste zeigt aktuelle Aktion, Detail und echten Fortschritt; bei nicht messbaren Vorgängen wird keine Prozentzahl erfunden.
- Sitzungszähler für Hinweise und Fehler bleiben sichtbar.
- wichtige Erfolg-, Hinweis- und Fehlermeldungen erscheinen zusätzlich als kurze ARIA-Live-Rückmeldung mit Symbol und Text.
- Projektanlage, Self-Repair, Schnellspeicher sowie Todo Speichern/Archivieren/Wiederherstellen besitzen einheitliche Busy-Zustände und Doppelausführungsschutz.
- leere Todo-Zustände erklären den nächsten sinnvollen Schritt.

### Barrierefreiheit & Lesbarkeit
- Skip-Link zum Hauptbereich ergänzt.
- Oberflächenzoom auf 100–200 % standardisiert und persistent.
- `Ctrl++`, `Ctrl+-`, `Ctrl+0` und `Ctrl+Mausrad` steuern denselben internen Zoom.
- Standard-Aktionsziele auf etwa 44 px Mindesthöhe vereinheitlicht; kompakte Hilfsaktionen bleiben getrennt.
- Prozessfläche besitzt reservierten Platz gegen Layoutsprünge.
- `prefers-reduced-motion` bleibt berücksichtigt.

### Architektur & Qualität
- `feedback.js` kapselt Prozessstatus, Zähler und wichtige Rückmeldungen wiederverwendbar.
- `feedback.css` trennt Feedbackdarstellung vom allgemeinen Designsystem.
- `docs/UX_STANDARD.md` ist verbindlicher UX-Vertrag; `docs/UX_AUDIT.md` dokumentiert Befunde und Prioritäten.
- `test_ux_contract.py` prüft Prozess-IDs, ARIA, Zoom, Tastatur, Busy-Schutz, große Ziele und Hilfetexte.
- GitHub Release-Gate besitzt eine eigene sichtbare UX-/Feedback-Prüfstufe.
- Startup vergleicht Manifestversion dynamisch mit der laufenden Backendversion statt einer doppelt gepflegten festen Versionszahl.

## 0.2.1 – 2026-09-12
### Robustheit & Self-Repair
- getrennte `app/self_repair.py`-Schicht für ausschließlich sichere, reversible Reparaturen.
- beschädigte `config.json` kann aus verifizierter Rückfallkopie wiederhergestellt werden; das beschädigte Original bleibt in Quarantäne.
- fehlende Standard-Projektordner werden nur nach vollständiger Projektmarker-Prüfung neu angelegt.
- ungültige Projektmarker, Dateikollisionen, Symlink-Ausbrüche und mehrdeutige Zustände werden nicht automatisch verändert.
- konfigurierter Projektpfad und tatsächlich freigegebener Projektpfad sind getrennt.
- Self-Repair-Ereignisse werden append-only als JSONL protokolliert.

### Fehlerbehandlung
- stabile lokale API-Fehlercodes.
- interne Fehlerdetails bleiben im Log und werden nicht an die UI ausgegeben.
- Self-Repair-Status und sicherer Run als lokale API.
- blockierende Datenzustände bleiben rot, während die Diagnoseoberfläche erreichbar bleibt.

### Agenten & Qualität
- `AGENTS.md` v2 mit Risikomodell R0–R4.
- sieben getrennte Prüfrollen: Analyse, Risiko, Fehlerursache, Planung, Regression, Plan-Prüfung und Release-Prüfung.
- Prüfrollen sind read-only gegenüber Produktivcode.
- R4 ist standardmäßig blockiert; Entfernen von Produktiv-, Test- oder Qualitätsverträgen wird als R4 erkannt.
- maschinenlesbare Agentenvertragsprüfung und granulare Release-Gates.

## 0.2.0 – 2026-09-12
### Neu
- zentraler SQLite-Datenkern in eigener Serviceschicht.
- WAL-Modus, Foreign Keys, Busy Timeout, Schema-Versionierung und explizite Transaktionen.
- Todo-Bereich D mit optionalem Datum, Uhrzeit und Priorität.
- reversibles Archiv und Wiederherstellung.
- Monatskalender E liest Termine direkt aus derselben Todo-Tabelle.
- verifizierte Datenbanksicherungen, Quarantäne und Crash-/Recovery-Regression.

## 0.1.0 – 2026-09-12
### Neu
- Expert Shell mit A–N-Dashboard und dominantem Hauptarbeitsbereich N.
- echte gewichtete grafische Startpipeline.
- fünf Themes und drei Bedienebenen.
- lokaler Python-Server ohne externe Runtime-Abhängigkeiten.
- sicherer Projektassistent, Schnellspeicher, Hilfesystem, Status-/Loggingbereich und Fokusmodus.
- triggerbasierte Agentenrollen, deterministische CI-Gates und zwei rotierende Git-Rückfallstände.
