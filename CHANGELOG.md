# Changelog

## 0.2.2 – Backup-Rotationshotfix
- Post-Merge-Backupfehler nach dem UX-Release als eigener Qualitätsbefund dokumentiert.
- zwei Rückfallzweige sofort auf die korrekten vorherigen Hauptstände verifiziert und zurückgesetzt.
- Backuprotation von `git push --force` auf GitHub Ref API umgestellt.
- vorhandene Ref wird kontrolliert per PATCH aktualisiert; fehlende Ref kann per POST erzeugt werden.
- beide Ziel-SHAs werden nach der Rotation mit `git ls-remote` nachvalidiert.
- drei automatische Workflowvertragstests verhindern Rückkehr zum unvalidierten Force-Push-Verfahren.

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
- stabile lokale API-Fehlercodes und granulare Release-Gates.
- sieben getrennte read-only Prüfrollen mit R0–R4-Risikomodell.

## 0.2.0 – 2026-09-12
- zentraler SQLite-Datenkern mit WAL, Foreign Keys, Busy Timeout, Schema-Versionierung und expliziten Transaktionen.
- Todo D, reversibles Archiv, Kalender E aus derselben Datenquelle.
- verifizierte Datenbanksicherungen, Quarantäne und Crash-/Recovery-Regression.

## 0.1.0 – 2026-09-12
- Expert Shell mit A–N-Dashboard, gewichteter Startpipeline, fünf Themes und drei Bedienebenen.
- lokaler Python-Server, sicherer Projektassistent, Schnellspeicher, Hilfe, Logging, Fokusmodus, Agentengates und zwei Git-Rückfallstände.
