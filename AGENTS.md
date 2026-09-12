# AGENTS – verbindliche Entwicklungsordnung v2.1

## Oberste Regel
Der Nutzer ist Anwender, nicht reguläre Test- oder Abnahmeinstanz. Probleme werden gelöst, nicht verdeckt. Freigabe erst nach Vorvalidierung, Nachvalidierung, Regression, Plan-Prüfung und finalem Release-Gate.

## Priorität
1. Nutzerdaten/Systemintegrität.
2. explizite Nutzeranforderung.
3. `AGENTS.md` + Sicherheits-/Qualitäts-/UX-Standards.
4. Iterationsplan + `TODO.md`.
5. Rollenverträge `.agents/`.
6. Komfort/Kosmetik.

## Rollen – Prüfsubagenten implementieren keinen Produktivcode
1. **Analyse-Agent** – Nur analysieren.
2. **Risiko-Agent** – Read-only R0–R4 bestimmen.
3. **Fehlerursachen-Agent** – Read-only Root Cause/Reproduktion.
4. **Plan-Agent** – Keine Implementierung; Plan/TODO/Abnahmekriterien.
5. **Regressions-Agent** – Read-only dauerhaften Testschutz prüfen.
6. **Plan-Prüfer** – Read-only Scope/Plan/Nebenwirkungen; bei Verstoß BLOCKIERT.
7. **Release-Prüfer** – Read-only; Ergebnis RELEASE READY oder BLOCKIERT.
8. Umsetzung erfolgt getrennt und nur innerhalb des Plans.

## Trigger
- `app/static/`: mindestens R1 + UX-Vertrag + Regressionstest.
- normale `app/`-/Fachlogik: R2 + Regression.
- DB/Persistenz/Projekt/Recovery/Start/CI/Agenten/Sicherheitsgrenzen: R3 + isolierter Branch/PR + Fehlerpfade + Manifest/Status/Changelog.
- bestätigter Crash/Fehler: Fehlerursachen-Agent + dauerhafter Regressionstest.
- Löschung von Produktiv-, Test- oder Qualitätsverträgen bzw. irreversible Nutzdatenwirkung: R4, standardmäßig blockiert.

## Risikoklassen
- **R0** Dokumentation ohne Laufzeitwirkung.
- **R1** Darstellung/UI/UX.
- **R2** Fachlogik/API.
- **R3** Daten, Persistenz, Recovery, Start, CI, Agenten, Sicherheitsgrenzen.
- **R4** destruktiv/irreversibel oder Schutzabbau – Standard BLOCKIERT.

## Pflichtablauf
Analyse → Risiko → Plan/TODO → Rückfallstand → Vorvalidierung → kleinste robuste Umsetzung → Nachvalidierung → Regression → Root Cause bei Fehler → Dokumentation/Manifest → Plan-Prüfung → finaler Gesamtstand → Release-Prüfung.

## Architektur
UI, Feedback, API, Projektpersistenz, Datenkern und Self-Repair bleiben getrennte Verantwortungen. Gemeinsame Logik wiederverwenden. Keine parallele Persistenz. Keine Monolithen ohne nachweisbaren Vorteil. Kritische Änderungen atomar/transaktional. Runtime localhost-only, solange nicht explizit anders geplant.

## UX-/Feedback-Vertrag
`docs/UX_STANDARD.md` ist für UI- und Prozessänderungen verbindlich.
- keine Aktion ohne sichtbares bereit/busy/Erfolg/Hinweis/Fehler-Feedback.
- reale Prozentwerte nur bei bekannter Gesamtmenge; sonst „läuft“.
- Batchprozesse führen OK / Hinweise / Fehler / übersprungen; jedes Überspringen braucht einen Grund.
- Farbe nie alleinige Statusinformation.
- Laienmodus zeigt primär den nächsten sinnvollen Schritt.
- Tastatur, sichtbarer Fokus, Screenreader-Live-Status, Kontrast+ und 100–200-%-Skalierung schützen.
- riskante Dateiaktionen brauchen Analyse → Konfliktprüfung → Vorschau/Trockenlauf → Bestätigung → Ergebnis → Undo/Recovery.
- R1-Änderungen benötigen ab v2.1 ebenfalls Regressionsevidenz.

## Self-Repair – Allowlist
Nur eindeutig sichere reversible Maßnahmen: verifizierte Config-Rückfallkopie, Quarantäne vor Restore, fehlende Standardordner nach gültigem Projektmarker, bekannte Temp-Artefakte quarantänisieren, verifizierte SQLite-Recovery, regenerierbare Cache-/Indexdaten neu erzeugen, Ereignisse append-only protokollieren.

## Self-Repair – Denylist
Automatisch verboten: Nutzerdaten löschen/überschreiben, fremde nichtleere Ordner übernehmen, Projektmarker erfinden, mehrdeutige Nutzerstände entscheiden, ungeprüfte Backups einspielen, R4 als Reparatur tarnen. Bei Unsicherheit Zustand unverändert lassen und klar diagnostizieren.

## Fehlerbehandlung
Stabile Kategorien/Codes verwenden, soweit sinnvoll. Breite `except Exception` nur an echten Prozess-/API-Grenzen und dort intern loggen. Jeder bestätigte Fehler hinterlässt Test, Validierung oder Architekturbarriere.

## Backups
`backup/previous-1` und `backup/previous-2` halten zwei direkte Hauptstände. Konfiguration und DB besitzen zusätzliche verifizierbare Rückfallmechanismen. Restore wird selbst geprüft.

## Dokumentations-Synchronität
Bei Verhaltensänderungen mindestens `TODO.md`, `CHANGELOG.md`, `PROJEKTSTATUS.md`, `projekt-manifest.json` sowie betroffene Hilfe-/Architektur-/Standarddateien prüfen. Dokumentiert wird nur tatsächlich geprüfter Stand.

## Verboten
Nutzer routinemäßig testen lassen; Testfehler verstecken; Schutzprüfungen für grüne Gates entfernen; Prüfsubagenten implementieren lassen; unnötige Nebenumbauten; riskante automatische Reparatur ohne Allowlist; unfertige Module als fertig darstellen.
