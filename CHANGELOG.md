# Changelog

## 0.2.2 – Kandidat – UX, Feedback & Transparenz
### Nutzerführung
- permanente kompakte Prozessleiste zeigt aktuelle Aktion, Detail und echten Fortschritt; bei nicht messbaren Vorgängen wird keine Prozentzahl erfunden.
- Sitzungszähler für Hinweise und Fehler bleiben sichtbar.
- wichtige Erfolg-, Hinweis- und Fehlermeldungen erscheinen zusätzlich als kurze ARIA-Live-Rückmeldung mit Symbol und Text.
- Projektanlage, Self-Repair, Schnellspeicher sowie Todo Speichern/Archivieren/Wiederherstellen besitzen einheitliche Busy-Zustände und Doppelausführungsschutz.
- leere Todo-Zustände erklären den nächsten möglichen Schritt.

### Barrierefreiheit & Lesbarkeit
- Skip-Link zum Hauptbereich ergänzt.
- Oberflächenzoom auf 100–200 % standardisiert und persistent.
- `Ctrl++`, `Ctrl+-`, `Ctrl+0` und `Ctrl+Mausrad` steuern denselben internen Zoom.
- Standard-Aktionsziele auf etwa 44 px Mindesthöhe vereinheitlicht.
- Prozessfläche besitzt reservierten Platz gegen Layoutsprünge.
- `prefers-reduced-motion` bleibt berücksichtigt.

### Architektur & Qualität
- `feedback.js` kapselt Prozessstatus, Zähler und wichtige Rückmeldungen wiederverwendbar.
- `feedback.css` trennt Feedbackdarstellung vom allgemeinen Designsystem.
- `docs/UX_STANDARD.md` wird verbindlicher UX-Vertrag.
- `test_ux_contract.py` prüft Prozess-IDs, ARIA, Zoom, Tastatur, Busy-Schutz, große Ziele und Hilfetexte.
- GitHub Release-Gate erhält eine eigene sichtbare UX-/Feedback-Prüfstufe.

## 0.2.1 – 2026-09-12
### Robustheit & Self-Repair
- neue getrennte `app/self_repair.py`-Schicht für ausschließlich sichere, reversible Reparaturen.
- beschädigte `config.json` kann aus einer verifizierten `.tmp`, `.bak1` oder `.bak2` wiederhergestellt werden; das beschädigte Original bleibt in Quarantäne.
- fehlende Standard-Projektordner werden nur nach vollständiger Projektmarker-Prüfung neu angelegt.
- ungültige Projektmarker, Dateikollisionen und mehrdeutige Zustände werden nicht automatisch verändert.
- konfigurierter Projektpfad und tatsächlich freigegebener Projektpfad sind getrennt; fehlerhafte Projekte bleiben diagnostizierbar, aber für Fachzugriffe gesperrt.
- Symlinks an Projektmarker oder Standardordnern werden als Projektgrenzen-Verletzung blockiert und nicht verfolgt.
- kritische JSON-Schreibvorgänge synchronisieren nach atomarem Replace auch das Elternverzeichnis, soweit vom Dateisystem unterstützt.
- Self-Repair-Ereignisse werden append-only als JSONL protokolliert.

### Fehlerbehandlung
- stabile lokale API-Fehlercodes für Validierung, Konflikt, Berechtigung, NotFound, Datenintegrität und interne Fehler.
- interne Fehlerdetails/Stacktraces bleiben im Log und werden nicht an die UI ausgegeben.
- `GET /api/self-repair/status` diagnostiziert ohne Änderungen.
- `POST /api/self-repair/run` führt ausschließlich Allowlist-Reparaturen aus; blockierende Zustände bleiben unverändert.
- grafische Startroutine unterscheidet jetzt sicher repariert, Hinweis und blockierend; blockierende Datenzustände bleiben rot, während die Diagnoseoberfläche erreichbar bleibt.
- Bereich K erhält „🛠 Sicher reparieren“ mit verständlicher Statusmeldung.

### Agenten & Qualität
- `AGENTS.md` auf Entwicklungsordnung v2 mit Prioritäten, Triggern, Self-Repair-Allowlist/Denylist und Risikomodell R0–R4 erweitert.
- sieben getrennte Prüfrollen: Analyse, Risiko, Fehlerursache, Planung, Regression, Plan-Prüfung und Release-Prüfung.
- Prüfrollen sind read-only gegenüber Produktivcode; Umsetzung bleibt getrennt.
- risikobasiertes `scripts/agent_gate.py`: R3 erzwingt verstärkte Regression, R4 ist standardmäßig blockiert.
- Entfernen von Produktiv-, Test- oder Qualitätsverträgen wird als R4 erkannt.
- `scripts/validate_agents.py` prüft Rollenverträge, Manifest und Workflow-Verdrahtung maschinenlesbar.
- Release-Gate prüft Struktur, Manifest, Agentenverträge, Python-/JavaScript-Syntax, vollständige Regression und Diff-Hygiene.
- neue Regressionstests für Konfigurations-Recovery, Quarantäne, Fremdordner-/Symlink-Schutz, Projektstruktur-Reparatur, Self-Repair-API und Risikoklassifikation.

## 0.2.0 – 2026-09-12
### Neu
- zentraler SQLite-Datenkern in eigener Serviceschicht.
- WAL-Modus, Foreign Keys, Busy Timeout, Schema-Versionierung und explizite Transaktionen.
- Todo-Bereich D mit optionalem Datum, optionaler Uhrzeit und Priorität.
- Abhaken verschiebt Todos reversibel ins Archiv; Wiederherstellung ist möglich.
- Monatskalender E liest Termine direkt aus derselben Todo-Tabelle, ohne Doppelhaltung.
- Organisationsübersicht zeigt aktive/archivierte Todos und DB-Sicherungen.
- Datenkernprüfung in der grafischen Startroutine.

### Sicherheit & Recovery
- SQLite-Sicherungen werden mit der Backup-API erzeugt und vor Freigabe geprüft.
- maximal zwei aktuelle verifizierte Datenbank-Sicherungen.
- beschädigte Datenbank wird vor Recovery als Quarantäne erhalten.
- automatische Recovery ausschließlich aus verifizierter Sicherung.
- Crash-, Restart-/Persistenz-, Rollback-, Recovery- und API-Vertragstests ergänzt.
- ursprüngliche Expert-Shell-Regression bleibt Bestandteil des Release-Gates.

## 0.1.0 – 2026-09-12
### Neu
- Expert Shell mit A–N-Dashboard und dominantem Hauptarbeitsbereich N.
- echte, gewichtete grafische Startpipeline.
- fünf Themes und drei Bedienebenen.
- lokaler Python-Server ohne externe Runtime-Abhängigkeiten.
- sicherer Projektassistent und projektbezogener Schnellspeicher.
- Hilfesystem, Status-/Loggingbereich und Fokusmodus.
- triggerbasierte Agentenrollen und deterministische CI-Gates.
- rotierende Rückfallzweige für zwei vorherige `main`-Versionen.

### Sicherheit
- localhost-only Server.
- atomare JSON-Speicherung mit zwei Vorgängerkopien.
- fremde nichtleere Zielordner werden nicht automatisch übernommen.
