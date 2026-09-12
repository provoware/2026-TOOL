# AGENTS – verbindliche Entwicklungsordnung v2

## 1. Oberste Regel
Der Nutzer ist Anwender, nicht regulärer Tester oder Abnahmeinstanz. Eine Änderung gilt erst als freigabefähig, wenn sie automatisch vorvalidiert, nachvalidiert, regressionsgeprüft und gegen ihren dokumentierten Plan kontrolliert wurde.

**Probleme werden gelöst, nicht verdeckt.** Ein Fehler darf weder durch breites Exception-Schlucken noch durch Umbenennung zur Warnung verschwinden.

## 2. Autorität und Reihenfolge
Bei Konflikten gilt diese Reihenfolge:
1. Schutz von Nutzerdaten und Systemintegrität.
2. explizite Nutzeranforderung.
3. `AGENTS.md` und Sicherheits-/Qualitätsstandards.
4. Iterationsplan und `TODO.md`.
5. Rollenverträge unter `.agents/`.
6. Komfort, Geschwindigkeit und kosmetische Optimierung.

## 3. Rollenfolge – Subagenten implementieren keinen Produktivcode
1. **Analyse-Agent** – Nur analysieren; Abhängigkeiten, Ist-Zustand, Regressionen.
2. **Risiko-Agent** – Read-only Risikoklasse R0–R4 und notwendige Gates bestimmen.
3. **Fehlerursachen-Agent** – Read-only Root Cause, Reproduktion und Fehlerklasse ermitteln.
4. **Plan-Agent** – Keine Implementierung; nur Optimierungsplan/TODO/Abnahmekriterien dokumentieren.
5. **Regressions-Agent** – Read-only prüfen, welche bestehenden und neuen Tests dauerhaft schützen müssen.
6. **Plan-Prüfer** – Read-only Scope, Plan, Tests, Dokumentation und Nebenwirkungen prüfen.
7. **Release-Prüfer** – Read-only finale Freigabekriterien prüfen.
8. **Umsetzung** – erfolgt außerhalb dieser Prüfsubagenten, klein, modular und nur innerhalb des freigegebenen Plans.

Die Rollenverträge unter `.agents/` sind verbindlich. Ein Prüfsubagent darf niemals still zum Umsetzungsagenten werden.

## 4. Trigger-Matrix
- Änderung unter `app/`: Analyse + Risiko + Plan + Regression + Plan-Prüfung + Release-Prüfung.
- Änderung an Persistenz/DB/Projektstruktur/Recovery: zusätzlich Fehlerursachen-Agent und R3-Mindestniveau.
- Änderung unter `.github/workflows/`, `scripts/`, `AGENTS.md`, `.agents/`: Agentenvertragsprüfung zwingend.
- bestätigte Regression/Crash/Datenfehler: Fehlerursachen-Agent zwingend; dauerhafter Regressionstest erforderlich.
- reine Dokumentation ohne Verhaltensänderung: R0; Produktivtests nur soweit betroffen.

## 5. Risikoklassen
### R0 – Dokumentation
Keine Laufzeitwirkung.

### R1 – lokale Darstellung
UI/Text/Styling ohne Persistenz- oder API-Änderung.

### R2 – Fachlogik
normale API-/Modul-/Validierungsänderung ohne Datenmigration.

### R3 – Kernrisiko
Persistenz, Projektstruktur, Datenbank, Recovery, Migration, Backup, Startlogik, CI/Release oder Sicherheitsgrenzen.
Pflicht: isolierter Branch/PR, neue Regressionstests, Fehlerpfade, Restart/Recovery wenn betroffen, Manifest/Status/Changelog synchron.

### R4 – destruktiv/irreversibel
Löschen, Überschreiben nicht reproduzierbarer Nutzerdaten, ungeprüfte Migration, Sicherheitsgrenze aufweichen.
**Standard: blockiert.** Nur mit expliziter Anforderung, Backup/Rollback und speziell dokumentierter Freigabe planbar.

## 6. Pflichtablauf jeder Verhaltensänderung
1. Ziel, Ist-Zustand und betroffene Komponenten bestimmen.
2. Risiko R0–R4 bestimmen.
3. Abhängigkeiten und mögliche Regressionen analysieren.
4. Plan/TODO vor Implementierung dokumentieren.
5. zwei Git-Rückfallstände bzw. geeignete Daten-Backups sicherstellen.
6. Vorvalidierung des Ausgangsstands.
7. kleinstmögliche robuste Änderung implementieren.
8. Nachvalidierung einschließlich Fehlerpfaden.
9. bestätigte Fehlerursache beseitigen; Regressionstest hinzufügen.
10. Manifest, Hilfe, Status, Changelog und Standards synchronisieren, wenn betroffen.
11. Plan-/Scope-Konformität prüfen.
12. finalen Commit erneut als Ganzes validieren.
13. nur grünen Stand freigeben.

## 7. Architekturregeln
- gemeinsame Logik in kleinen Services/Komponenten wiederverwenden.
- UI, API, Projektpersistenz, Datenkern und Self-Repair bleiben getrennte Verantwortungen.
- keine großen Monolithdateien ohne nachweisbaren Vorteil.
- neue Abstraktion nur, wenn sie Abhängigkeiten oder Duplikate reduziert.
- Datenänderungen atomar/transaktional; Dateiersatz über Tempdatei + atomaren Replace.
- auf Linux nach kritischem atomarem Dateiersatz nach Möglichkeit Elternverzeichnis synchronisieren.
- regenerierbare Daten lieber neu erzeugen als riskant reparieren.
- Fachmodule dürfen keine eigene parallele Persistenz erfinden, wenn ein zentraler Service existiert.
- keine versteckten Netzwerkdienste; Runtime bleibt localhost-only, solange nicht explizit anders geplant.

## 8. Self-Repair – Allowlist
Automatisch zulässig sind nur eindeutig sichere und reversible Maßnahmen:
- syntaktisch/strukturell gültige Konfigurations-Backups verifizieren und wiederherstellen,
- beschädigtes Original vorher quarantänisieren,
- fehlende Standardordner **nur nach validiertem PROVOWARE-Projektmarker** neu anlegen,
- bekannte temporäre Artefakte quarantänisieren statt löschen,
- SQLite-Recovery ausschließlich aus verifizierter Sicherung,
- Cache/Index/ableitbare Daten neu erzeugen,
- Reparaturereignisse append-only protokollieren.

## 9. Self-Repair – Denylist
Automatisch verboten:
- Nutzerdateien löschen oder überschreiben,
- fremde nichtleere Ordner übernehmen,
- fehlende/ungültige Projektmarker erfinden,
- Konflikte zwischen mehreren plausiblen Nutzerständen automatisch entscheiden,
- ungeprüfte Backups einspielen,
- R4-Operationen als Self-Repair tarnen.

Wenn eine sichere Reparatur nicht eindeutig möglich ist: Zustand unverändert lassen, Fehler klar melden, Diagnose protokollieren.

## 10. Fehlerbehandlung
Fehler erhalten stabile Kategorien/Codes, soweit sinnvoll: Validierung, NotFound, Conflict, Integrity, IO/Permission, Recovery, Internal.

Breite `except Exception`-Grenzen sind nur an echten Prozess-/API-Grenzen zulässig und müssen intern loggen; Fachlogik soll konkrete Exceptions verwenden.

Jeder bestätigte Fehler hinterlässt mindestens einen dauerhaften Schutz:
- Regressionstest oder
- zusätzliche Validierungsregel oder
- Architekturänderung, die die Fehlerklasse verhindert.

## 11. Regressionsgedächtnis
Für wiederholbare Fehler dokumentieren Tests mindestens:
- Auslöser,
- erwartetes Verhalten,
- Schutz vor Teilzuständen/Datenverlust,
- Neustart-/Recovery-Verhalten, wenn relevant.

Ein bereits behobener Fehler, der erneut unentdeckt auftritt, gilt als Defekt des Regressionsmanagements.

## 12. Backups und Rückfall
`main` hält automatisch zwei direkte Vorgänger unter `backup/previous-1` und `backup/previous-2`.
Lokale Konfigurationen und Datenbanken verwenden zusätzlich eigene verifizierbare Rückfallmechanismen.
Backup ersetzt niemals Validierung; Restore wird selbst geprüft.

## 13. Dokumentations-Synchronität
Bei Verhaltensänderungen müssen mindestens geprüft werden:
- `TODO.md`
- `CHANGELOG.md`
- `PROJEKTSTATUS.md`
- `projekt-manifest.json`
- betroffene Hilfe-/Architektur-/Standarddateien.

Dokumentation beschreibt den tatsächlich geprüften Stand, nicht die Absicht.

## 14. Verboten
- Nutzer routinemäßig zum Testen auffordern.
- Testfehler ignorieren, überspringen oder als Erfolg darstellen.
- Schutzprüfungen entfernen, nur damit ein Gate grün wird.
- Analyse-/Plan-/Prüfsubagenten zur Implementierung verwenden.
- unnötige Nebenumbauten außerhalb des dokumentierten Plans.
- riskante automatische Reparatur ohne klare Allowlist.
