# PROVOWARE Datenstandard

## Verbindliche Regeln

1. Strukturierte Projektdaten laufen über `app/data_core.py`; Module schreiben nicht direkt in SQLite.
2. SQLite verwendet WAL, Foreign Keys, Busy Timeout und explizite Transaktionen.
3. Schreiboperationen sind vollständig oder werden vollständig zurückgerollt.
4. Das Schema wird über `PRAGMA user_version` versioniert.
5. Vor späteren Schema-Migrationen wird eine verifizierte SQLite-Sicherung erzeugt.
6. Kalenderdaten werden nicht separat gespeichert. Bereich E ist eine Projektion der aktiven terminierten Todos.
7. Erledigte Todos werden logisch und reversibel archiviert; endgültiges Löschen ist nicht Teil des Standardablaufs.
8. Automatische Recovery darf nur aus einer Sicherung erfolgen, die `PRAGMA quick_check` bestanden hat.
9. Eine beschädigte Originaldatenbank wird vor Recovery als Quarantänedatei erhalten.
10. Es werden maximal zwei aktuelle verifizierte Datenbank-Sicherungen gehalten.
11. Cache oder abgeleitete Daten dürfen niemals die einzige Kopie von Nutzerdaten sein.

## Fehlerklassen

- `DataValidationError`: Eingabe ist ungültig; keine Teiländerung zulassen.
- `DataNotFoundError`: Datensatz existiert nicht.
- `DataIntegrityError`: Datenbank ist nicht sicher verwendbar; Normalbetrieb für den betroffenen Datenkern blockieren oder geprüfte Recovery verwenden.

## Qualitätsnachweis

Änderungen am Datenkern müssen mindestens Transaktions-, Restart-/Persistenz-, Crash-, Recovery-, Archiv-/Restore- und Kalenderprojektions-Regressionen bestehen. Eine Nutzerabnahme ersetzt diese Prüfungen nicht und ist nicht vorgesehen.
