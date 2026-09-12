# Iteration 2.1 – Reliability & Self-Repair

## Ziel
PROVOWARE HEADQUARTER v0.2.1 soll Fehler früher erkennen, sichere reparierbare Zustände automatisch korrigieren und bei nicht eindeutig reparierbaren Zuständen bewusst stoppen, ohne Nutzerdaten zu löschen oder fremde Ordner zu übernehmen.

## Analyse – bestätigte Schwachstellen
1. `ProjectStore.bootstrap()` bewertet einen Projektmarker bisher primär nach Existenz, nicht nach Inhalt und Schema.
2. `load_json()` fällt bei beschädigter Konfiguration still auf Default zurück; dadurch bleibt die Ursache unsichtbar.
3. Self-Repair-Regeln sind dokumentiert, aber noch nicht als zentrale Allowlist/Denylist implementiert.
4. Agent-Gates unterscheiden Risiken nur grob und prüfen Rollenverträge nur über einzelne Texttreffer.
5. Für Änderungen an Persistenz, Recovery und Agentenlogik fehlt ein differenzierter Risikoscore mit zusätzlichen Pflichtprüfungen.

## Architekturentscheidung
Eine neue kleine Schicht `app/self_repair.py` übernimmt ausschließlich sichere Reparaturen. Sie darf keine Fachlogik enthalten und keine Nutzerdaten löschen.

### Automatisch erlaubt
- beschädigte `config.json` aus einer syntaktisch und strukturell gültigen `.bak1`/`.bak2` wiederherstellen,
- beschädigte Konfiguration vorher in Quarantäne verschieben,
- fehlende Standard-Projektordner nur nach validiertem PROVOWARE-Projektmarker neu anlegen,
- bekannte temporäre Dateien nur quarantänisieren, nicht löschen,
- SQLite-Recovery ausschließlich über den bereits verifizierenden `DataCore.ensure_ready()` ausführen,
- Diagnose- und Reparaturereignisse append-only protokollieren.

### Automatisch verboten
- Nutzerdateien löschen oder überschreiben,
- einen fehlenden/ungültigen Projektmarker neu erfinden,
- einen fremden nichtleeren Ordner als Projekt übernehmen,
- Konflikte zwischen zwei plausiblen Nutzerständen automatisch entscheiden,
- Backups ungeprüft zurückspielen.

## Agentenmodell v2
Reihenfolge:
1. Analyse-Agent – read-only Bestands-/Abhängigkeitsanalyse.
2. Risiko-Agent – read-only Risikoklasse und erforderliche Gates.
3. Fehlerursachen-Agent – read-only Root-Cause bei Fehler/Regression.
4. Plan-Agent – nur TODO/Plan-Dokumentation.
5. Regressions-Agent – read-only Prüfmatrix und Schutz gegen Wiederholung.
6. Plan-Prüfer – read-only Plan-/Scope-Konformität.
7. Release-Prüfer – read-only finale Freigabekriterien.

Keiner dieser Subagenten implementiert Produktivcode.

## Risikoklassen
- R0: Dokumentation ohne Verhaltensänderung.
- R1: lokale UI-/Textänderung ohne Persistenz.
- R2: normale Fachlogik/API.
- R3: Persistenz, Projektstruktur, Recovery, Migration, CI/Backup.
- R4: destruktive/irreversible Operation oder Sicherheitsgrenze. R4 ist standardmäßig blockiert, bis explizit anders geplant.

## Umsetzung
1. `AGENTS.md` als verbindliche Entwicklungsordnung v2 ausbauen.
2. Rollenverträge unter `.agents/` vervollständigen.
3. `scripts/agent_gate.py` auf Risikoklassen und präzisere Pflichtartefakte erweitern.
4. `scripts/validate_agents.py` als maschinenlesbare Rollen-/Vertragsprüfung hinzufügen.
5. `app/self_repair.py` implementieren.
6. `project_store.py` um strikte Projektmarkerprüfung und durable atomare Writes ergänzen.
7. `server.py` um Self-Repair-Status und sicheren Reparaturlauf ergänzen.
8. Startcontroller um Self-Repair-Prüfschritt erweitern.
9. Regressionstests für Konfig-Recovery, Fremdordnerschutz, Projektstruktur-Reparatur, API-Vertrag und Agentenregeln ergänzen.
10. Manifest, Hilfe, Architektur, Qualitätsdoku, Changelog und Projektstatus synchronisieren.

## Vorvalidierung
- bestehende v0.2.0-Gates müssen auf `main` grün sein,
- zwei Git-Rückfallstände vorhanden,
- keine bestehende Datenfunktion wird entfernt.

## Nachvalidierung
- Python- und JavaScript-Syntax,
- vollständige Unit-/API-Regression,
- Self-Repair-Fehlersimulationen,
- Agentenvertragsprüfung,
- Manifest-/Strukturprüfung,
- PR-Gates auf finalem Head,
- nach Merge dieselben Gates erneut auf `main`, inklusive Backuprotation.

## Fertig-Kriterium
v0.2.1 wird nur freigegeben, wenn alle automatischen Gates grün sind, sichere Reparaturen reproduzierbar funktionieren und nicht sicher reparierbare Zustände ohne Datenveränderung blockiert bzw. als klarer Fehler gemeldet werden.
