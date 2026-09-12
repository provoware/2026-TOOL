# Projektstatus

## Freigegebener Produktlaufzeitstand
**v0.3.0 – Jobmanager & reversibles Aktionsjournal**

## Aktive Release-Promotion
**v0.4.0 – Read-only Sortier-Analyse & Vorschau**

## Status
🟡 **Release Candidate – Funktionsumfang vollständig, finale Versionspromotion und Release-Gates stehen noch aus.**

Der integrierte Implementierungshead `693ebbbf0124bb94db20a995877f06fa95f796f2` bestand bereits das vollständige 17-stufige Release-Gate. Die automatische Gesamt-Discovery auf diesem Stand umfasste **76 Tests**, alle grün. Nachfolgende Dokumentations- und Versionspromotionscommits müssen denselben vollständigen Prüfpfad erneut bestehen, bevor ein Merge zulässig ist.

## Funktionsumfang v0.4.0
- verbindlicher R3-Plan vor Implementierung,
- `app/sorter_preview.py` als getrennte read-only Scanner-/Regelgrenze,
- persistente zeilenweise Scan-Ergebnisse in derselben Projekt-SQLite,
- Feature-Schema v1 mit verifizierter DB-Sicherung vor erstmaliger Tabellenanlage,
- Quellwurzel-Symlink-Schutz,
- keine Symlink-Verfolgung innerhalb des Scans,
- nicht-rekursiver Standard,
- versteckte/System-/Cache-Inhalte standardmäßig ausgeschlossen,
- deterministische Kategorien Bilder/Video/Audio/Dokumente/Archive/Text-Code/Sonstige,
- Regelpriorität, Mehrfachtreffer und echte Konflikterkennung,
- tolerantes Überspringen verschwundener/unlesbarer Einträge,
- paginierte Vorschau und Scan-Zusammenfassung,
- Scanner ausdrücklich als R3 klassifiziert,
- asynchroner localhost-only Scanstart statt blockierender HTTP-Anfrage,
- dedizierter Scan-Worker mit sauberem Lifecycle,
- Resume startet tatsächlich wieder einen Worker und nicht nur einen Datenbankstatus,
- grafische Ordnerwahl über KDialog mit verständlichem Fallback,
- lazy-loaded Dateien-Assistent im Hauptarbeitsbereich,
- Standardgruppen per Auswahlfeld statt Regelsyntax,
- optionale Wortregeln mit Zielgruppe und verständlicher Vorrangstufe,
- Pause, Weiter und Abbruch,
- Summary-Karten für Dateien, Volumen, zugeordnet, Konflikte, nicht zugeordnet und übersprungen,
- Filter und Paging für große Ergebnislisten,
- globale Prozessanzeige während des Scans,
- bewusst kein Ausführen-Button für Dateiänderungen.

## Sicherheitsentscheidung
Der Scanner darf Nutzdateien ausschließlich über Dateisystem-Metadaten betrachten. Er enthält keine Funktion zum Kopieren, Verschieben, Umbenennen oder Löschen. Schreibzugriffe erfolgen nur auf PROVOWARE-eigene Projektzustände wie SQLite-Scanindex, Jobstatus und Logs.

Die spätere Datei-Ausführung bleibt eine getrennte R3-Ausbaustufe und darf erst nach erfolgreicher Vorschau-/Konfliktfreigabe entstehen.

## Regelvertrag
Eine aktive Regel kann Dateiendungen, Suchwörter und/oder Kategorie kombinieren. Innerhalb einer Liste gilt ODER, zwischen gesetzten Bedingungsarten UND. Höhere Prioritätszahl gewinnt. Haben die stärksten Treffer dieselbe Priorität, aber unterschiedliche Zielgruppen, wird die Datei als `conflict` markiert. Es wird keine Zielgruppe geraten.

## Robustheitsvertrag
- Einzelne `OSError`-/Permission-/Verschwunden-Fälle brechen den Gesamtscan nicht ab.
- Symlinks werden sichtbar als übersprungen protokolliert und niemals traversiert.
- Scanresultate werden in Batches gespeichert.
- vorhandener Jobmanager bleibt alleiniger Eigentümer von Pause/Resume/Abbruch/Heartbeat/Checkpoint.
- Crash-/Restart-Zustände bleiben über `interrupted` sichtbar; keine stille automatische Fortsetzung.
- Resume eines Sortierjobs startet zusätzlich einen echten Scanner-Worker.
- der HTTP-Server bleibt während eines Scans ansprechbar.

## Reale automatische Evidenz vor Release-Promotion
Auf Implementierungshead `693ebbbf0124bb94db20a995877f06fa95f796f2`:
- Release-Gate Run 56: 🟢 alle 17 sichtbaren Stufen erfolgreich,
- Gesamt-Discovery: **76 Tests grün**,
- Scanner-Regressionsgruppe: **12 Tests grün**,
- HTTP-API-Vertrag: **11 Tests grün**, einschließlich asynchronem Sortierstart, Paging, Root-Symlink-Blockierung und Resume-Worker,
- UX-Vertrag: **9 Tests grün**, einschließlich read-only Wortlaut, sichere Defaults, Lazy-Loading, Konflikt-/Skip-Anzeige und fehlender Executor-Schnittstelle.

Der erste Scanner-Zwischenlauf fand einen Fehler ausschließlich im Test-Doppelgänger für `os.scandir()`: Der Fake-Iterator war nicht iterierbar. Die Produktlogik wurde nicht geändert; der Test wurde an den echten Iteratorvertrag angepasst und der vollständige Prüfpfad danach erfolgreich wiederholt.

## Noch offen vor endgültiger Freigabe
1. Produkt-/Manifest-/Serverversion auf v0.4.0 promovieren,
2. Changelog und Versionsverträge auf den Release Candidate umstellen,
3. finalen PR-Head vollständig über 17 Release-Stufen + sieben Subagent-Gates prüfen,
4. Draft-PR erst danach freigabefähig markieren,
5. Squash-Merge nur auf unverändertem geprüftem Head,
6. dieselben Gates erneut auf `main`,
7. reale Snapshotrotation nach Merge und tatsächliche Commit-Zuordnung im Manifest prüfen.

## Letzter vollständig freigegebener Hauptstand
Der aktuelle `main`-Stand vor v0.4.0 ist Commit `76c7d0a28d7a93391de860fc16ced706223dfbd8`.

Die zugehörige reale Snapshotrotation enthält:
- `previous-1.zip` → `1b889c2a12b6a640bb6015d72bb3a4c4054cfe9f`,
- `previous-2.zip` → `5a075481f683cba3d411098cc3d21382283ae719`.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin **nicht** durch Branch-Protection/Ruleset geschützt. Automatische Gates sind aktiv, können einen ausreichend berechtigten direkten Push aber nicht technisch verhindern. Dieser Punkt bleibt in `docs/OFFENE_RISIKEN.md` dokumentiert.

## Nutzer-Abnahme
Nicht erforderlich. Der Nutzer ist Anwender und keine reguläre Testinstanz; technische Freigabe basiert auf automatischer Evidenz.
