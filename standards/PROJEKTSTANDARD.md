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

Vorhandene nichtleere Ordner ohne PROVOWARE-Marker werden nicht übernommen oder verändert. Projektmarker und Konfigurationen werden atomar geschrieben. Ableitbare Cache-Daten gelten nie als einzige Datenkopie.
