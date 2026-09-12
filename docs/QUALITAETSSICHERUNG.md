# Qualitätssicherung

## Kein manueller Nutzer-Test als Releasebedingung
Freigabe erfolgt über automatische Prüfungen. Nutzerfeedback kann später zusätzliche Anforderungen liefern, ersetzt aber keine Tests oder technische Abnahme.

## Risikomodell R0–R4
- **R0:** Dokumentation ohne Laufzeitwirkung.
- **R1:** Darstellung/UX ohne Persistenz/API.
- **R2:** Fachlogik/API/Validierung.
- **R3:** Persistenz, Projektstruktur, DB, Recovery, Backup, Migration, Startlogik, CI/Release oder Sicherheitsgrenzen.
- **R4:** destruktiv/irreversibel; standardmäßig blockiert.

Die Risikoklasse bestimmt die notwendige Prüftiefe. R3 verlangt geänderte Regressionstests und – soweit betroffen – Restart-, Crash-, Recovery- und Teilzustandsprüfungen.

## Release-Gate
`scripts/validate_all.sh` prüft:
1. Pflichtstruktur,
2. Manifest/Version/Qualitätsverträge,
3. sieben Agentenrollen und deren Read-only-Verträge,
4. Python-Syntax,
5. JavaScript-Syntax,
6. vollständige automatische Regression,
7. Diff-/Patch-Hygiene.

GitHub Actions führt das Gate auf Pull Requests und nach Merge auf `main` erneut aus.

## Subagent-Gates
Die deterministische Pipeline bildet folgende Prüfkette ab:
`Analyse → Risiko → Fehlerursachen-Trigger → Plan → Regression → Plan-Prüfung → Release-Prüfung`.

Die Rollen schreiben keinen Produktivcode. `scripts/validate_agents.py` prüft Rollenverträge, Manifestzuordnung und Workflow-Verdrahtung maschinenlesbar.

## Self-Repair-Qualität
Self-Repair ist kein allgemeines „Fehler wegmachen“, sondern eine Allowlist eindeutig sicherer Reparaturen. Jeder automatische Eingriff muss reversibel bzw. durch Quarantäne abgesichert und nachvalidiert sein. Die Denylist verbietet insbesondere Nutzerdatenlöschung, Fremdordnerübernahme, erfundene Projektmarker, ungeprüfte Backups und automatische Entscheidungen bei mehrdeutigen Nutzerständen.

`GET /api/self-repair/status` ist read-only. `POST /api/self-repair/run` führt nur Allowlist-Reparaturen aus. Nicht sicher reparierbare Zustände bleiben unverändert und werden blockierend gemeldet.

## Regression
Bestätigte Fehler erhalten dauerhaft Test, Validierungsregel oder Architekturverbesserung. Der Schutz umfasst je nach Fehlerklasse auch Crash, Neustart, Recovery, Quarantäne und API-Verträge. Ein wiederkehrender bereits behobener Fehler gilt zusätzlich als Defekt des Regressionsmanagements.

## Fehlercodes
Die lokale API nutzt stabile Kategorien wie `VALIDATION`, `NOT-FOUND`, `CONFLICT`, `PERMISSION`, `DATA-INTEGRITY` und `INTERNAL`. Interne Stacktraces werden nicht an die UI ausgegeben; Details bleiben im Log.

## Rückfall
Zwei Vorgänger von `main` werden als `backup/previous-1` und `backup/previous-2` gehalten. Lokale Konfigurationen besitzen `.bak1` und `.bak2`; SQLite hält zwei verifizierte Sicherungen. Backup ersetzt keine Validierung – auch Restore wird geprüft.
