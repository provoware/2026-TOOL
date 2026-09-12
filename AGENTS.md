# AGENTS – verbindliche Entwicklungsordnung v2.1

## 1. Oberste Regel
Der Nutzer ist Anwender, nicht regulärer Tester oder Abnahmeinstanz. Freigabe erst nach automatischer Vorvalidierung, Nachvalidierung, Regression, Plan-Prüfung und finalem Release-Gate. **Probleme werden gelöst, nicht verdeckt.**

## 2. Priorität
1. Schutz von Nutzerdaten und Systemintegrität.
2. explizite Nutzeranforderung.
3. `AGENTS.md` sowie Sicherheits-, Qualitäts- und UX-Standards.
4. Iterationsplan und `TODO.md`.
5. Rollenverträge `.agents/`.
6. Komfort/Kosmetik.

## 3. Rollen – Prüfsubagenten implementieren keinen Produktivcode
1. **Analyse-Agent** – Nur analysieren.
2. **Risiko-Agent** – Read-only R0–R4 bestimmen.
3. **Fehlerursachen-Agent** – Read-only Root Cause/Reproduktion.
4. **Plan-Agent** – Keine Implementierung; Plan/TODO/Abnahmekriterien.
5. **Regressions-Agent** – Read-only dauerhaften Testschutz prüfen.
6. **Plan-Prüfer** – Read-only Scope/Plan/Nebenwirkungen; bei Verstoß `BLOCKIERT`.
7. **Release-Prüfer** – Read-only; Ergebnis `RELEASE READY` oder `BLOCKIERT`.
8. Umsetzung erfolgt getrennt, klein und nur innerhalb des Plans.

## 4. Trigger
- `app/static/`: mindestens R1 + UX-Vertrag + Regressionsevidenz.
- normale Fachlogik/API: R2 + Regression.
- DB/Persistenz/Projekt/Recovery/Start/Backup/CI/Agenten/Sicherheitsgrenzen: R3 + isolierter Branch/PR + Fehlerpfade + Manifest/Status/Changelog.
- bestätigter Crash/Fehler: Fehlerursachen-Agent + dauerhafter Regressionstest.
- irreversible Nutzdatenwirkung oder Schutzabbau: R4, standardmäßig blockiert.

## 5. Risikoklassen
- **R0** Dokumentation ohne Laufzeitwirkung.
- **R1** Darstellung/UI/UX.
- **R2** Fachlogik/API.
- **R3** Daten, Persistenz, Recovery, Start, Backup, CI, Agenten, Sicherheitsgrenzen.
- **R4** destruktiv/irreversibel oder Schutzabbau – Standard `BLOCKIERT`.

## 6. Pflichtablauf
Analyse → Risiko → Plan/TODO → Rückfallstand → Vorvalidierung → kleinste robuste Umsetzung → Nachvalidierung → Regression → Root Cause bei Fehler → Dokumentation/Manifest → Plan-Prüfung → finaler Gesamtstand → Release-Prüfung.

## 7. Architektur
UI, Feedback, API, Projektpersistenz, Datenkern, Backup und Self-Repair bleiben getrennte Verantwortungen. Gemeinsame Logik wiederverwenden. Keine parallele Persistenz. Keine Monolithen ohne nachweisbaren Vorteil. Kritische Datenänderungen atomar/transaktional. Runtime localhost-only, solange nicht explizit anders geplant.

## 8. UX-/Feedback-Vertrag
`docs/UX_STANDARD.md` ist verbindlich.
- keine Aktion ohne sichtbar bereit/busy/Erfolg/Hinweis/Fehler.
- reale Prozentwerte nur bei bekannter Gesamtmenge; sonst „läuft“.
- Batchprozesse: OK / Hinweise / Fehler / übersprungen; jedes Überspringen braucht einen Grund.
- Farbe nie alleinige Statusinformation.
- Laienmodus zeigt primär den nächsten sinnvollen Schritt.
- Tastatur, Fokus, Screenreader-Live-Status und 100–200-%-Zoom schützen.
- riskante Dateiaktionen brauchen Analyse → Konfliktprüfung → Vorschau/Trockenlauf → Bestätigung → Ergebnis → Undo/Recovery.

## 9. Self-Repair – Allowlist
Automatisch zulässig nur eindeutig sichere reversible Maßnahmen: verifizierte Config-Rückfallkopie, Quarantäne vor Restore, fehlende Standardordner nach gültigem Projektmarker, bekannte temporäre Artefakte quarantänisieren, verifizierte SQLite-Recovery, regenerierbare Cache-/Indexdaten neu erzeugen, Ereignisse append-only protokollieren.

## 10. Self-Repair – Denylist
Automatisch verboten: Nutzerdaten löschen/überschreiben, fremde nichtleere Ordner übernehmen, Projektmarker erfinden, mehrdeutige Nutzerstände entscheiden, ungeprüfte Backups einspielen, R4 als Reparatur tarnen. Bei Unsicherheit Zustand unverändert lassen und klar diagnostizieren.

## 11. Fehlerbehandlung / Regressionsgedächtnis
Stabile Fehlercodes verwenden, soweit sinnvoll. Breite `except Exception` nur an echten Prozess-/API-Grenzen und dort intern loggen. Jeder bestätigte Fehler hinterlässt mindestens Test, Validierungsregel oder Architekturbarriere. Ein wiederkehrender alter Fehler gilt als Defekt des Regressionsmanagements.

## 12. Backups und Rückfall
Automatische Git-Versionen werden primär als **zwei vollständige, verifizierte `git archive`-ZIPs** auf `backup/snapshots` gehalten:
- `version-backups/previous-1.zip`
- `version-backups/previous-2.zip`
- `version-backups/manifest.json` mit Commit-IDs und SHA-256.

Die ZIPs müssen Workflow-Dateien einschließen und vor Freigabe einen ZIP-Integritätstest bestehen. Der Snapshot-Zweig darf durch die Rotation ausschließlich `version-backups/*` verändern; insbesondere `.github/workflows/*` bleiben dort eingefroren. Die alten `backup/previous-1` und `backup/previous-2` sind Legacy-Rückfallpunkte und nicht mehr Primärmechanismus. Datenbanken/Konfiguration besitzen zusätzliche verifizierbare Rückfallmechanismen. Backup ersetzt niemals Validierung; Restore muss selbst prüfbar sein.

## 13. Release-Engineering-Fehler
Ein fehlgeschlagener Backup-/Release-Workflow darf nicht als kosmetisches Rot ignoriert werden. Pflicht: konkrete Job-Logs lesen → Root Cause benennen → Designfehler statt Symptom beheben → Regressionstest ergänzen → finalen `main`-Stand samt Backupworkflow erneut prüfen.

## 14. Dokumentations-Synchronität
Bei Verhaltensänderungen mindestens `TODO.md`, `CHANGELOG.md`, `PROJEKTSTATUS.md`, `projekt-manifest.json` sowie betroffene Hilfe-/Architektur-/Standarddateien prüfen. Dokumentiert wird nur tatsächlich geprüfter Stand.

## 15. Verboten
Nutzer routinemäßig testen lassen; Testfehler verstecken; Schutzprüfungen für grüne Gates entfernen; Prüfsubagenten implementieren lassen; unnötige Nebenumbauten; riskante Reparatur ohne Allowlist; unfertige Module als fertig darstellen.
