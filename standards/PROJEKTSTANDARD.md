# PROVOWARE Projektstandard

Ein neues Projekt wird ausschließlich in einem explizit gewählten Basisordner angelegt. Der Zielordner erhält:

- `.provoware/project.json`
- `datenbanken/`
- `archiv/`
- `todo/`
- `notizen/`
- `schnellspeicher/`
- `logs/`
- `export/`
- `sicherungen/`
- `cache/`

## Projektidentität
Ein Ordner gilt nur dann als PROVOWARE-Projekt, wenn `.provoware/project.json` als echtes lokales JSON-Dokument vorhanden und inhaltlich gültig ist. Erwartet werden mindestens:
- `schema_version = 1`,
- `app = "PROVOWARE HEADQUARTER"`,
- ein nichtleerer Projektname.

Ein bloß vorhandener Dateiname reicht nicht. Ein ungültiger Marker wird nicht automatisch ersetzt oder neu erfunden.

## Projektgrenze
Alle Standardordner müssen echte direkte Unterordner des validierten Projektordners sein. Symlinks an `.provoware`, am Projektmarker oder an einem Standardordner werden für automatische Projektfunktionen nicht akzeptiert. Dadurch dürfen `datenbanken`, `logs`, `sicherungen` usw. nicht unbemerkt außerhalb der Projektgrenze zeigen.

Fehlende Standardordner dürfen durch Self-Repair ausschließlich nach erfolgreicher Projektmarker-Prüfung neu angelegt werden. Existiert an ihrer Stelle eine Datei, ein Sonderpfad oder Symlink, bleibt dieser unverändert und der Zustand wird blockierend gemeldet.

## Fremde Ordner
Vorhandene nichtleere Ordner ohne gültigen PROVOWARE-Marker werden nicht übernommen oder verändert. Ein konfigurierter Pfad mit defektem Marker bleibt für Diagnose sichtbar, wird aber nicht für Datenbank-, Todo-, Schnellspeicher- oder andere Fachzugriffe freigegeben.

## Persistenz
Projektmarker und Konfigurationen werden über Tempdatei und atomaren Ersatz geschrieben; kritische Writes werden zusätzlich synchronisiert. Ableitbare Cache-Daten gelten nie als einzige Datenkopie. Self-Repair und Datenbank-Recovery müssen ihre Ergebnisse nachvalidieren und dürfen ungeprüfte Rückfallkopien nicht verwenden.
