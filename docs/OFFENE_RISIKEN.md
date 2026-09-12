# Offene Risiken / bewusst noch nicht als gelöst behaupten

## 🔴 `main` noch ohne Repository-Branch-Protection
Die automatische Release- und Subagent-Prüfung ist aktiv, aber `main` ist repositoryseitig weiterhin nicht geschützt. Ein ausreichend berechtigter direkter Push kann die PR-Pflicht technisch umgehen.

**Ziel:** GitHub-Ruleset/Branch-Protection mit Pull-Request-Pflicht und erforderlichen Checks `Release-Gate` und `Subagent-Gates`. Dafür ist Repository-Administration nötig; Dokumentation ersetzt diese Sperre nicht.

## 🟡 Browser-/visuelle Regression
HTML/CSS/JS-, UX- und Accessibility-Verträge sind automatisiert. Noch nicht pixel-/layoutnah automatisiert geprüft sind alle Kombinationen aus Browser, Fenstergröße, Fokusreihenfolge und 100/125/150/175/200-%-Zoom.

**Ziel:** browserbasierte Regression mit DOM-Messungen, Screenshots und Accessibility-Prüfung – ohne Nutzer als Testinstanz.

## 🟡 Backend-Jobmanager für lange Datei-/Scanprozesse
Die zentrale UI-Prozessanzeige existiert. Für lange Dateijobs fehlt noch ein wiederverwendbarer Backend-Jobmanager mit Pause, Abbruch, Resume, Checkpoint, Watchdog, Dateien/s, Volumen/s und kontrolliertem Device-Loss.

**Ziel:** vor dem ersten großen Sortier-/Scanworkflow implementieren.

## 🟡 Undo-Journal für Dateioperationen
Todo-Archiv, Konfiguration, Datenbank und Release-Snapshots besitzen Rückfallmechanismen. Die eigentliche Datei-Sortierengine existiert noch nicht, deshalb gibt es noch kein transaktionales Journal für Verschieben/Kopieren.

**Ziel:** vor der ersten produktiven Verschiebeaktion: Vorzustand protokollieren, Konflikte verhindern, Undo/Recovery ermöglichen.

## 🟢 Bewusst noch nicht implementiert
- DB-Eingabemaske C,
- globale Suche H,
- Download-/Dateiregel-Engine.

Diese Bereiche sind vorbereitete Modulgrenzen und dürfen nicht als fertige Fachfunktionen dargestellt werden.
