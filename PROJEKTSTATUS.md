# Projektstatus

## Freigegebener Produktlaufzeitstand
**v0.3.0 – Jobmanager & reversibles Aktionsjournal**

## Aktive Entwicklung
**v0.4.0 – Read-only Sortier-Analyse & Vorschau**

## Status
🔵 **In Entwicklung – Backend-Fundament angelegt, noch nicht freigegeben.**

Der freigegebene Laufzeitstand bleibt v0.3.0. v0.4.0 wird erst dann als Produktversion geführt, wenn Scanner, localhost-API, Dateien-Assistent, Prozessfeedback, Dokumentation und vollständige PR-/main-Gates bestanden sind.

## Freigegebene Basis aus v0.3.0
- Expert Shell A–N,
- SQLite-WAL-Datenkern, Todo, Kalender und reversibles Archiv,
- Crash-/Recovery-Schutz,
- Reliability & Self-Repair,
- globale UX-/Prozessanzeige, Warn-/Fehlerzähler, Zoom 100–200 %, Fokus/ARIA,
- sieben read-only Prüfrollen mit R0–R4,
- verifizierte Zwei-Slot-Release-Snapshots auf `backup/snapshots`,
- persistenter Jobmanager mit Checkpoint/Resume und Watchdog,
- reversibles Dateiaktionsjournal als Sicherheitsvertrag für kommende Datei-Workflows.

## Iteration 4 – aktueller Backend-Stand
Neu angelegt:
- verbindlicher R3-Plan `docs/iterationen/ITERATION_04_SORTER_PREVIEW_PLAN.md`,
- `app/sorter_preview.py` als getrennte read-only Scanner-/Regelgrenze,
- persistente zeilenweise Scan-Ergebnisse in derselben Projekt-SQLite,
- Feature-Schema v1 mit verifizierter DB-Sicherung vor erstmaliger Tabellenanlage,
- Quellwurzel-Symlink-Schutz,
- keine Symlink-Verfolgung innerhalb des Scans,
- nicht-rekursiver Standard,
- versteckte/System-/Cache-Inhalte standardmäßig ausgeschlossen,
- deterministische Dateikategorien,
- Regelpriorität und Konflikterkennung,
- paginierte Vorschau und Scan-Zusammenfassung im Service,
- tolerantes Überspringen verschwundener/unlesbarer Einträge,
- Scanner als R3 im Agenten-Risikogate,
- eigene Regression `tests/test_sorter_preview.py`,
- eigene sichtbare Sortier-Stufe im Release-Gate.

## Sicherheitsentscheidung für v0.4.0
Der Scanner darf Nutzdateien ausschließlich über Dateisystem-Metadaten betrachten. Er enthält keine Funktion zum Kopieren, Verschieben, Umbenennen oder Löschen. Schreibzugriffe erfolgen nur auf PROVOWARE-eigene Projektzustände wie SQLite-Scanindex, Jobstatus und Logs.

Die spätere Datei-Ausführung bleibt eine getrennte Ausbaustufe und darf erst nach erfolgreicher Vorschau-/Konfliktfreigabe entstehen.

## Regelvertrag
Eine aktive Regel kann Dateiendungen, Suchwörter und/oder Kategorie kombinieren. Innerhalb einer Liste gilt ODER, zwischen gesetzten Bedingungsarten UND. Höhere Prioritätszahl gewinnt. Haben die stärksten Treffer dieselbe Priorität, aber unterschiedliche Zielgruppen, wird die Datei als `conflict` markiert. Es wird keine Zielgruppe geraten.

## Robustheitsvertrag
- Einzelne `OSError`-/Permission-/Verschwunden-Fälle brechen den Gesamtscan nicht ab.
- Symlinks werden sichtbar als übersprungen protokolliert und niemals traversiert.
- Scanresultate werden in Batches gespeichert.
- vorhandener Jobmanager bleibt alleiniger Eigentümer von Pause/Resume/Abbruch/Heartbeat/Checkpoint.
- Crash-/Restart-Zustände bleiben über `interrupted` sichtbar; keine stille automatische Fortsetzung.

## Noch offen vor v0.4.0-Freigabe
1. neue Scanner-/Regeltests im realen GitHub-Gate ausführen und jeden Fehler ursachenbasiert beheben,
2. localhost-only API für Quellordnerwahl, Scanstart, Summary und Paging anbinden,
3. Dateien-Modul als laienverständlichen Vorschau-Assistenten anbinden,
4. globale Prozessanzeige mit Scanfortschritt und Überspringgründen verbinden,
5. Hilfe/Architektur/Qualitätsdoku/Testübersicht synchronisieren,
6. finalen PR-Head vollständig über Release-Gate + sieben Subagent-Gates prüfen,
7. Squash-Merge nur auf unverändertem geprüften Head,
8. dieselben Gates erneut auf `main`,
9. reale Snapshotrotation nach Merge prüfen.

## Letzter vollständig geprüfter Hauptstand
Der aktuelle `main`-Dokumentationsstand ist Commit `76c7d0a28d7a93391de860fc16ced706223dfbd8`. Dessen Release-Gate, sieben Subagent-Gates und Backupworkflow wurden erfolgreich nachvalidiert.

Die reale Snapshotrotation nach diesem Stand enthält:
- `previous-1.zip` → `1b889c2a12b6a640bb6015d72bb3a4c4054cfe9f`,
- `previous-2.zip` → `5a075481f683cba3d411098cc3d21382283ae719`.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin **nicht** durch Branch-Protection/Ruleset geschützt. Automatische Gates sind aktiv, können einen ausreichend berechtigten direkten Push aber nicht technisch verhindern. Dieser Punkt bleibt in `docs/OFFENE_RISIKEN.md` dokumentiert.

## Nutzer-Abnahme
Nicht erforderlich. Der Nutzer ist Anwender und keine reguläre Testinstanz; technische Freigabe basiert auf automatischer Evidenz.
