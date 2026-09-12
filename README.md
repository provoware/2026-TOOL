# PROVOWARE HEADQUARTER

**Release-Stand: v0.4.0 · Read-only Sortier-Analyse & Vorschau**

Lokale, modulare Arbeitszentrale für Kubuntu mit A–N-Shell, sicherem Projektmodell, SQLite-WAL-Datenkern, Todo/Kalender, Self-Repair, globalem Prozessfeedback und persistentem Job-/Recovery-Fundament. v0.4.0 ergänzt erstmals einen praktisch nutzbaren Dateien-Workflow und bleibt gegenüber den Quelldateien strikt read-only.

## Start für Laien
1. Repository herunterladen oder das fertige Release-ZIP entpacken.
2. `start.sh` doppelklicken bzw. ausführen.
3. Chromium öffnet die lokale Oberfläche automatisch.
4. Beim ersten Start Projektname und Basisordner festlegen.
5. Im Modul **Dateien** einen Quellordner auswählen und ausschließlich analysieren.

Es werden keine externen Python-Pakete benötigt. Der Server bindet ausschließlich an `127.0.0.1` und wählt automatisch einen freien Port.

## Automatische Sicherheit
- echte grafische Startroutine statt Fake-Prozentanzeige,
- Vor- und Nachvalidierung,
- automatisierte Tests ohne Nutzerabnahme als Releasebedingung,
- SQLite WAL mit Transaktionen, Integritätsprüfung und zwei verifizierten DB-Sicherungen,
- Self-Repair nur über sichere Allowlist und Quarantäne,
- persistenter Jobmanager mit Checkpoint/Resume, Heartbeat und Watchdog,
- Dateiaktionsjournal mit strengem Reversibilitätsvertrag,
- read-only Sortier-Vorschau ohne copy/move/rename/delete,
- Quellwurzel-Symlink-Schutz und keine Symlink-Traversierung,
- sichere Defaults: nicht rekursiv, versteckte/System-/Cachebereiche aus,
- sichtbare Mehrfachtreffer, Konflikte und Überspringgründe statt stiller Entscheidungen,
- zwei vollständige verifizierte Git-Archiv-Snapshots auf `backup/snapshots`,
- sieben risikobasierte read-only Prüfrollen,
- Manifest als maschinenlesbare Projektwahrheit.

## Dateien – v0.4.0
Der Dateien-Assistent arbeitet in vier klaren Schritten:

**Quellordner wählen → Regeln auswählen → nur analysieren → Ergebnis prüfen.**

Vorbereitete Standardgruppen sind Bilder, Video, Audio, Dokumente, Archive und Text/Code. Zusätzlich lassen sich Wortregeln ohne Regelsyntax anlegen, z. B. „Dateiname enthält `suno` → Zielgruppe `Suno`“. Höherer Vorrang gewinnt; gleich starke widersprüchliche Ziele werden als Konflikt angezeigt.

Der Scan läuft als lokaler Hintergrundjob. Pause, Weiter und Abbruch verwenden denselben persistenten Jobmanager wie alle langen Arbeiten. Vorschauergebnisse werden seitenweise aus der Projekt-SQLite gelesen. Ein Resume startet wieder einen echten Worker – ein reiner Statuswechsel ohne Arbeit ist nicht zulässig.

**Wichtig:** v0.4.0 enthält bewusst keinen Ausführen-Button für Dateiänderungen. Ein späterer Executor wird eine getrennte, erneut R3-geprüfte Ausbaustufe.

## Release-ZIP
`scripts/build_release_package.py` erzeugt das Paket reproduzierbar direkt aus einem Git-Commit. Das ZIP wird vor der Ausgabe vollständig gelesen, auf Pflichtdateien und einen eindeutigen Wurzelordner geprüft und erhält SHA-256 sowie maschinenlesbare Paketmetadaten. Das Release-Gate veröffentlicht diese Dateien zusätzlich als GitHub-Actions-Artefakt.

## Daten- und Jobprinzip
Todo, Kalender, Jobs, Jobereignisse, Dateiaktionsjournal und Sortier-Scanindex verwenden dieselbe projektbezogene `provoware.sqlite3`. Es gibt keine zweite Job- oder Sortierdatenbank und keine parallelen Statusdateien.

Aktive Jobs werden nach Neustart oder bei veraltetem Heartbeat als `interrupted` gespeichert und **nicht** still automatisch fortgesetzt. Resume erfolgt explizit aus einem persistierten Checkpoint.

Das Dateiaktionsjournal verändert selbst keine Nutzdateien. Ein späterer Executor darf `applied` oder `undone` erst nach realer Operation und erfolgreicher Nachvalidierung setzen. Endgültiges Löschen gehört nicht zum v0.4.0-Scope.

## A–N
A Toolinfo · B Einstellungen · C DB-Eingabe · D Todo · E Kalender · F Organisation · G Module · H Suche · I Projekt · J Notiz · K Logging · L Schnellstart · M Schnellspeicher · N Hauptarbeitsbereich.

## Entwicklung
- `AGENTS.md` – verbindliche Entwicklungs- und Sicherheitsregeln,
- `.agents/` – sieben Prüfrollen,
- `projekt-manifest.json` – Version, Daten-, Job-, Sortier-, Paket-, UI-, Qualitäts- und Backupverträge,
- `docs/JOB_ACTION_CORE.md` – verbindlicher Job-/Journalvertrag,
- `docs/iterationen/ITERATION_04_SORTER_PREVIEW_PLAN.md` – verbindlicher v0.4.0-Sicherheits-/Funktionsplan,
- `docs/` – Architektur, Start, Qualität, Self-Repair, UX und Iterationspläne,
- `scripts/validate_all.sh` – vollständiges lokales Release-Gate,
- `.github/workflows/` – Release-, Agenten- und Snapshot-Backup-Gates.

## Validierung
```bash
./scripts/validate_all.sh
```

Der Nutzer ist Anwender, nicht regulärer Tester. Rote Gates werden bis zur konkreten Ursache analysiert und durch Fix plus Regression abgesichert. Der Release-Stand wird nur unverändert gemergt und anschließend auf `main` einschließlich Snapshot-Backup und erzeugtem ZIP erneut nachvalidiert.
