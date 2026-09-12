# Iteration 2 – Datenkern v0.2.0

## Ziel

Zentralen SQLite-Datenkern mit WAL, Transaktionen, Schema-Versionierung und Recovery einführen. Bereich D erhält echte Todo-Verwaltung mit optionaler Terminierung und reversiblem Archiv. Bereich E liest Termine direkt aus derselben Todo-Datenquelle.

## Sicherheitsprinzipien

- SQLite-Zugriffe ausschließlich über `app/data_core.py`.
- WAL, Foreign Keys, Busy Timeout und Transaktionen zentral erzwingen.
- Keine zweite Kalenderdatenbank: Kalender ist eine Projektion der Todo-Daten.
- Abhaken archiviert logisch und reversibel; kein endgültiges Löschen in Iteration 2.
- Vor Schema-Migration geprüfte SQLite-Sicherung.
- Maximal zwei aktuelle verifizierte Datenbank-Sicherungen halten.
- Bei Datenbankkorruption nur aus einer verifizierten Sicherung automatisch wiederherstellen; beschädigtes Original vorher quarantänisieren.
- Nutzer wird nicht als Tester eingeplant.

## Arbeitspakete

1. `DataCore` und Schema v1 anlegen.
2. Projektanlage initialisiert Datenbank vor Freigabe des Projektes.
3. Todo-API: anlegen, aktiv auflisten, archivieren, wiederherstellen.
4. Kalender-API: Monatsprojektion aus aktiven Todos.
5. UI D und E mit denselben Daten verbinden.
6. Startcontroller um Datenbankprüfung erweitern.
7. Unit-, Restart-, Crash- und Recovery-Tests ergänzen.
8. Manifest, Hilfe, Architektur, Changelog, Status und TODO synchronisieren.
9. Vollständiges Release-Gate ausführen.

## Abnahmekriterien

- WAL aktiv und Schema-Version korrekt.
- Transaktions-Rollback nach Fehler nachgewiesen.
- Uncommittete Transaktion überlebt simulierten Prozessabsturz nicht.
- Todos bleiben nach Neuinstanziierung/Restart erhalten.
- Abgehakte Todos verschwinden aus Aktivliste und erscheinen im Archiv.
- Archivierte Todos können wiederhergestellt werden.
- Kalender zeigt ausschließlich terminierte aktive Todos aus derselben Tabelle.
- Korruptions-Recovery aus geprüftem Backup funktioniert und bewahrt defekte Originaldatei als Quarantäne.
- Expert-Shell-v0.1-Regression bleibt vollständig grün.
