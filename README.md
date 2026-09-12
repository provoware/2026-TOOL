# PROVOWARE HEADQUARTER

**Iteration 3 · Jobmanager & reversibles Aktionsjournal · v0.3.0 RC**

Lokale, modulare Arbeitszentrale für Kubuntu mit A–N-Shell, sicherem Projektmodell, SQLite-WAL-Datenkern, Todo/Kalender, Self-Repair, globalem Prozessfeedback und persistentem Job-/Recovery-Fundament für kommende Datei-Workflows.

## Start für Laien
1. Repository herunterladen/klonen.
2. `start.sh` doppelklicken bzw. ausführen.
3. Chromium öffnet die lokale Oberfläche automatisch.
4. Beim ersten Start Projektname und Basisordner festlegen.

Es werden keine externen Python-Pakete benötigt. Der Server bindet ausschließlich an `127.0.0.1` und wählt automatisch einen freien Port.

## Automatische Sicherheit
- echte grafische Startroutine statt Fake-Prozentanzeige,
- Vor- und Nachvalidierung,
- automatisierte Tests ohne Nutzerabnahme als Releasebedingung,
- SQLite WAL mit Transaktionen, Integritätsprüfung und zwei verifizierten DB-Sicherungen,
- Self-Repair nur über sichere Allowlist und Quarantäne,
- persistenter Jobmanager mit Checkpoint/Resume, Heartbeat und Watchdog,
- Dateiaktionsjournal mit strengem Reversibilitätsvertrag; in Iteration 3 noch keine reale Dateiänderung,
- zwei vollständige verifizierte Git-Archiv-Snapshots auf `backup/snapshots`,
- sieben risikobasierte read-only Prüfrollen,
- Manifest als maschinenlesbare Projektwahrheit.

## Daten- und Jobprinzip
Todo, Kalender, Jobs, Jobereignisse und Dateiaktionsjournal verwenden dieselbe projektbezogene `provoware.sqlite3`. Es gibt keine zweite Jobdatenbank und keine parallelen Statusdateien.

Aktive Jobs werden nach Neustart oder bei veraltetem Heartbeat als `interrupted` gespeichert und **nicht** still automatisch fortgesetzt. Resume erfolgt explizit aus einem persistierten Checkpoint.

Das Dateiaktionsjournal verändert selbst keine Nutzdateien. Ein späterer Executor darf `applied` oder `undone` erst nach realer Operation und erfolgreicher Nachvalidierung setzen. Endgültiges Löschen gehört nicht zum v0.3.0-Scope.

## A–N
A Toolinfo · B Einstellungen · C DB-Eingabe · D Todo · E Kalender · F Organisation · G Module · H Suche · I Projekt · J Notiz · K Logging · L Schnellstart · M Schnellspeicher · N Hauptarbeitsbereich.

## Entwicklung
- `AGENTS.md` – verbindliche Entwicklungs- und Sicherheitsregeln,
- `.agents/` – sieben Prüfrollen,
- `projekt-manifest.json` – Version, Daten-, Job-, UI-, Qualitäts- und Backupverträge,
- `docs/JOB_ACTION_CORE.md` – verbindlicher Job-/Journalvertrag,
- `docs/` – Architektur, Start, Qualität, Self-Repair, UX und Iterationspläne,
- `scripts/validate_all.sh` – vollständiges lokales Release-Gate,
- `.github/workflows/` – Release-, Agenten- und Snapshot-Backup-Gates.

## Validierung
```bash
./scripts/validate_all.sh
```

Der Nutzer ist Anwender, nicht regulärer Tester. Rote Gates werden bis zur konkreten Ursache analysiert und durch Fix plus Regression abgesichert.
