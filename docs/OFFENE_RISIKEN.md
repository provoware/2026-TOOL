# Offene Risiken / noch nicht als gelöst behaupten

## 🔴 Main-Branch-Schutz
Der GitHub-Branch `main` ist aktuell repositoryseitig nicht geschützt. Release-/Subagent-Gates existieren, können einen direkten Push aber ohne Branch-Protection nicht technisch verhindern.

**Ziel:** GitHub-Branch-Protection/Ruleset mit Pull-Request-Pflicht und erforderlichen Checks `Release-Gate` und `Subagent-Gates`. Dies benötigt Repository-Administration und darf nicht nur durch Dokumentation ersetzt werden.

## 🟡 Echte Browser-/visuelle Regression
Statische HTML/CSS/JS-Verträge und Syntaxprüfungen sind vorhanden. Noch nicht automatisiert bewiesen sind pixel-/layoutnahe Zustände bei 100/125/150/175/200 %, verschiedenen Fenstergrößen, Fokusreihenfolge und Screenreader-Verhalten.

**Ziel:** später browserbasierte Regression mit Screenshots/DOM-Messungen und Accessibility-Checks ergänzen, ohne den Nutzer als Testinstanz einzusetzen.

## 🟡 Zentraler Backend-Jobmanager
Die neue Feedbackschicht kann Prozesse darstellen. Für lange Datei-/Scanprozesse fehlt noch der Backend-Jobmanager mit Pause, Abbruch, Resume, Watchdog, Checkpoint und realen Dateien/s bzw. Volumen/s.

**Ziel:** vor der ersten großen Dateisortierung als wiederverwendbaren Service ergänzen.

## 🟡 Undo für Dateioperationen
Todo-Archiv und Daten-Recovery sind reversibel. Datei-Kopier-/Verschiebe-Undo existiert noch nicht, weil die eigentliche Dateiregel-Engine noch nicht implementiert ist.

**Ziel:** Transaktionsjournal vor erster produktiver Verschiebeaktion.

## 🟢 Bewusst noch nicht implementiert
DB-Eingabemaske C, globale Suche H und Download-/Dateiregel-Engine sind derzeit vorbereitete Modulgrenzen und dürfen in der UI nicht als fertige Fachfunktionen dargestellt werden.
