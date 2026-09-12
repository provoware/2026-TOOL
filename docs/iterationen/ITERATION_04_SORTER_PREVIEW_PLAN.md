# Iteration 4 – Read-only Sortier-Analyse & Vorschau v0.4.0

## Ziel
Iteration 4 macht das Dateien-Modul erstmals praktisch nutzbar, ohne Nutzdateien zu verändern.

Ablauf:
**Quellordner wählen → sicher analysieren → Dateitypen/Volumen gruppieren → Regeln auswerten → Mehrfachtreffer/Konflikte sichtbar machen → Trockenlauf-Vorschau.**

Produktversion: **v0.4.0**
Risikoklasse: **R3** – Dateisystemanalyse, persistente Scan-Ergebnisse, Resume/Checkpoint und Sicherheitsgrenzen.

## Sicherheitsgrenze
Diese Iteration ist strikt read-only gegenüber Nutzdateien.

Erlaubt:
- Verzeichnisse und Metadaten lesen,
- Dateinamen, Endungen, Größe und Änderungszeit erfassen,
- Scan-Ergebnisse in der projektbezogenen SQLite-Datenbank speichern,
- Regelentscheidungen und Konflikte berechnen,
- PROVOWARE-eigene Logs/Jobdaten/Scanindizes schreiben.

Nicht erlaubt:
- Nutzdateien kopieren,
- Nutzdateien verschieben,
- Nutzdateien umbenennen,
- Nutzdateien löschen,
- Symlink-Ziele verfolgen,
- Konflikte automatisch durch Dateiänderungen auflösen.

## Architektur
- `app/sorter_preview.py` kapselt ausschließlich Analyse, Regelbewertung, persistente Scan-Einträge und Vorschau.
- Der bestehende `JobManager` bleibt einzige Job-Zustandsmaschine für Start, Pause, Resume, Abbruch, Heartbeat und Checkpoint.
- Scan-Ergebnisse liegen zeilenweise in derselben projektbezogenen SQLite-Datenbank, nicht als großes Job-JSON.
- Die Scanner-Tabellen besitzen einen eigenen Feature-Schema-Vertrag und werden vor ihrer erstmaligen Anlage durch eine verifizierte Datenbanksicherung geschützt.
- Keine zweite Projektdatenbank und keine parallele Joblogik.

## Quellordner-Schutz
Vor Scanstart muss gelten:
- Pfad existiert,
- Pfad ist ein echtes Verzeichnis,
- Quellwurzel ist kein Symlink,
- Nullzeichen und überlange Pfade werden abgewiesen,
- rekursiv ist standardmäßig **aus**,
- versteckte Inhalte sind standardmäßig **aus**,
- bekannte Cache-/Systemordner werden standardmäßig ausgelassen,
- Symlinks werden niemals verfolgt; sie erscheinen als übersprungen mit Grund.

## Dateiklassifikation
Mindestens folgende verständliche Gruppen:
- Bilder,
- Video,
- Audio,
- Dokumente,
- Archive,
- Text / Code,
- Sonstige.

Die Klassifikation basiert zunächst deterministisch auf der normalisierten Dateiendung. Unbekannte Endungen bleiben `Sonstige`; es wird nichts geraten.

## Regelmodell für die Vorschau
Eine Regel besitzt mindestens:
- ID,
- Name,
- Priorität,
- Zielgruppe,
- optionale Dateiendungen,
- optionale Suchwörter im Dateinamen,
- optionale Dateikategorie,
- aktiv ja/nein.

Semantik:
- innerhalb einer Bedingungsliste gilt ODER,
- zwischen gesetzten Bedingungsarten gilt UND,
- höhere Prioritätszahl gewinnt,
- alle Treffer bleiben sichtbar,
- gleich starke Gewinner mit unterschiedlichen Zielgruppen ergeben `conflict`,
- ohne Treffer bleibt die Datei `unmatched`.

Damit kann später z. B. eine Wortregel `suno` höher priorisiert werden als eine allgemeine Audio-Regel.

## Persistente Scan-Einträge
Pro gefundener Datei mindestens:
- Job-ID,
- relativer Pfad,
- Dateiname,
- Endung,
- Kategorie,
- Größe,
- Änderungszeit in Nanosekunden,
- Entscheidung (`matched`, `conflict`, `unmatched`, `skipped`),
- Gewinner-Zielgruppe,
- alle Regel-Treffer,
- Überspringgrund,
- Erfassungszeit.

Diese Metadaten sind zugleich die spätere Grundlage für eine Stale-Prüfung vor realen Dateioperationen.

## Robustheit während des Scans
- Verschwundene Dateien werden übersprungen statt den Gesamtlauf abzubrechen.
- Nicht lesbare Dateien/Ordner werden mit Grund protokolliert.
- Einzelne `OSError`-Fälle dürfen den Restscan nicht zerstören.
- Rekursion folgt keinen Symlinks.
- Checkpoints werden regelmäßig über den vorhandenen Jobmanager geschrieben.
- Pause/Abbruch werden kooperativ zwischen Dateien/Verzeichnissen geprüft.
- Ein Crash lässt den Job als `interrupted` zurück; gespeicherte Scan-Einträge bleiben für Diagnose/Resume erhalten.

## Vorschau / Paging
Die UI darf Scan-Ergebnisse nur seitenweise abrufen. Standardmäßig keine riesige JSON-Gesamtliste.

Vorschau zeigt mindestens:
- Dateien gesamt,
- Datenvolumen,
- Gruppen nach Dateityp,
- matched / conflict / unmatched / skipped,
- Dateiname und relativer Pfad,
- Regel-Treffer,
- vorgeschlagene Zielgruppe,
- Überspringgrund.

## API-Scope dieser Iteration
Geplant:
- Quellordner grafisch wählen,
- read-only Analyse starten,
- Scanstatus/Job lesen,
- Vorschau seitenweise lesen,
- Zusammenfassung lesen,
- Pause/Resume/Abbruch über vorhandenen Jobvertrag.

Keine API für copy/move/delete.

## Regression
Pflichttests:
1. Feature-Schema wird sicher und idempotent angelegt.
2. Vor erstmaliger Schemaanlage entsteht eine verifizierte DB-Sicherung.
3. Nicht-rekursiver Scan bleibt im gewählten Ordner.
4. Rekursiver Scan folgt keinen Symlinks.
5. versteckte/System-/Cache-Inhalte werden standardmäßig ausgelassen.
6. Dateikategorien werden deterministisch erkannt.
7. Wortregel kann durch höhere Priorität eine Dateitypregel überstimmen.
8. gleich priorisierte unterschiedliche Ziele erzeugen Konflikt.
9. Datei verschwindet während Scan → `skipped`, kein Gesamtabbruch.
10. nicht lesbarer Eintrag → `skipped`/Fehlergrund, Restscan läuft weiter.
11. Ergebnisse werden persistent und seitenweise gelesen.
12. Jobfortschritt/Checkpoint wird aktualisiert.
13. Scan verändert Quellinhalte nicht.
14. bestehende 57+ Regressionen bleiben grün.

## Nicht in Iteration 4
- keine echte copy/move-Ausführung,
- kein automatisches Anlegen von Zielordnern,
- kein endgültiges Löschen,
- kein Hashing kompletter Dateien,
- keine Duplikatlöschung,
- keine automatische Konfliktauflösung,
- keine Hintergrundüberwachung des Downloadordners.

## Done-Kriterien
- Plan vor Implementierung vorhanden,
- read-only Scanner und Regel-Engine implementiert,
- persistente, paginierbare Vorschau vorhanden,
- Dateien-Modul laienverständlich angebunden,
- keine Nutzdatei-Mutationsfunktion im Scope,
- neue Regressionen + bestehende Gesamttests grün,
- Manifest/Changelog/Projektstatus/TODO synchron,
- vollständiges Release-Gate und sieben Subagent-Gates auf finalem PR-Head,
- nach Merge dieselben Gates auf `main`,
- reale Snapshot-Backuprotation erneut erfolgreich.
