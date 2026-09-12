# Projektstatus

## Produktlaufzeit
**v0.4.0 – Read-only Sortier-Analyse & Vorschau**

## Status
🟢 **Release-Stand – Funktion, Paketierung und vollständiger PR-Prüfpfad sind nachgewiesen.**

Manifest, Serverkennung, HTTP-Header und Versionsregressionen sind auf v0.4.0 synchronisiert. Der Release-Status ist `released`. Vor dem Squash-Merge wird der unveränderte letzte Metadaten-Head nochmals vollständig geprüft; nach dem Merge folgen dieselben Gates auf `main`, Snapshotrotation und Downloadprüfung des dort erzeugten ZIPs.

## Funktionsumfang v0.4.0
- verbindlicher R3-Plan vor Implementierung,
- `app/sorter_preview.py` als getrennte read-only Scanner-/Regelgrenze,
- persistente zeilenweise Scan-Ergebnisse in derselben Projekt-SQLite,
- Feature-Schema v1 mit verifizierter DB-Sicherung vor erstmaliger Tabellenanlage,
- Quellwurzel-Symlink-Schutz und keine Symlink-Traversierung,
- nicht-rekursiver Standard; versteckte/System-/Cache-Inhalte standardmäßig ausgeschlossen,
- deterministische Kategorien Bilder/Video/Audio/Dokumente/Archive/Text-Code/Sonstige,
- Regelpriorität, Mehrfachtreffer und echte Konflikterkennung,
- tolerantes Überspringen verschwundener/unlesbarer Einträge,
- paginierte Vorschau und Scan-Zusammenfassung,
- asynchroner localhost-only Scanstart mit eigenem Worker,
- Resume startet tatsächlich wieder einen Worker und nicht nur einen Datenbankstatus,
- grafische Ordnerwahl über KDialog mit verständlichem Fallback,
- lazy-loaded Dateien-Assistent ohne Regelsyntax-Zwang,
- Standardgruppen sowie optionale Wortregeln mit verständlicher Vorrangstufe,
- Pause, Weiter und Abbruch,
- Summary-Karten, Filter, Paging und globale Prozessanzeige,
- bewusst kein Ausführen-Button für Dateiänderungen.

## Sicherheitsentscheidung
Der Scanner betrachtet Nutzdateien ausschließlich über Dateisystem-Metadaten. Er enthält keine Funktion zum Kopieren, Verschieben, Umbenennen oder Löschen. Schreibzugriffe erfolgen nur auf PROVOWARE-eigene Projektzustände wie SQLite-Scanindex, Jobstatus und Logs. Die spätere Datei-Ausführung bleibt eine getrennte R3-Ausbaustufe.

## Paketierung
- `scripts/build_release_package.py` erzeugt das Nutzer-ZIP direkt aus einem Git-Commit über `git archive`.
- eindeutiger Wurzelordner `PROVOWARE-HEADQUARTER-v0.4.0/`.
- ZIP-Integrität, Pflichtdateien, Dateianzahl und das Fehlen von `.git` werden geprüft.
- SHA-256 und `release-package.json` werden erzeugt.
- das Release-Gate lädt ZIP, Prüfsumme und Metadaten als Actions-Artefakt hoch.
- `tests/test_release_package.py` schützt diesen Vertrag dauerhaft.

## Automatische Evidenz vor letzter Metadatenpromotion
Paket-/RC-Head `3bbc32baf78f8363b63315957d6b4303ee20ec80`:
- Release-Gate Run 80 (`34707482618`): 🟢 alle 17 Qualitätsstufen erfolgreich,
- zusätzliche Paketstufe: 🟢 ZIP erzeugt, verifiziert und als Artefakt veröffentlicht,
- Gesamt-Discovery: **77 Tests grün**,
- Subagent-Gates Run 78 (`34707482625`): 🟢 Analyse, Risiko, Fehlerursache, Plan, Regression, Plan-Prüfung und Release-Prüfung erfolgreich,
- heruntergeladenes Actions-Artefakt zusätzlich lokal geprüft: äußeres und inneres ZIP fehlerfrei, SHA-256 stimmig, einheitlicher v0.4.0-Wurzelordner, keine `.git`-Daten.

Der erste Scanner-Zwischenlauf fand einen Fehler ausschließlich im Test-Doppelgänger für `os.scandir()`. Die Produktlogik wurde nicht geändert; der Test wurde an den echten Iteratorvertrag angepasst und der vollständige Prüfpfad danach erfolgreich wiederholt.

## Letzte Freigabeschritte
1. exakt den letzten `released`-PR-Head erneut über alle 17 Release-Stufen, Paketbau und sieben Subagent-Gates prüfen,
2. Draft-Status entfernen,
3. Squash-Merge nur mit exakt diesem geprüften Head,
4. Release-Gate, Subagent-Gates und Snapshot-Backup auf dem neuen `main` prüfen,
5. finales Nutzer-ZIP aus dem `main`-Workflow herunterladen und erneut auf ZIP-Integrität, Commit und SHA-256 prüfen.

## Vorheriger Hauptstand
Der `main`-Stand vor v0.4.0 ist Commit `76c7d0a28d7a93391de860fc16ced706223dfbd8`.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin **nicht** durch Branch-Protection/Ruleset geschützt. Automatische Gates sind aktiv, können einen ausreichend berechtigten direkten Push aber nicht technisch verhindern. Dieser Punkt bleibt in `docs/OFFENE_RISIKEN.md` dokumentiert.

## Nutzer-Abnahme
Nicht erforderlich. Der Nutzer ist Anwender und keine reguläre Testinstanz; technische Freigabe basiert auf automatischer Evidenz.
