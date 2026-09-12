# Entwicklungsregeln

1. **Kleinste robuste Änderung:** keine Nebenumbauten ohne messbaren Nutzen.
2. **Wiederverwendung:** gemeinsame UI-/Datei-/Persistenzlogik zentralisieren.
3. **Codesparsamkeit:** weniger Code bevorzugen, wenn Lesbarkeit, Sicherheit und Testbarkeit gleich bleiben.
4. **Vorvalidierung:** Voraussetzungen, Pfade, Eingaben, Abhängigkeiten prüfen.
5. **Nachvalidierung:** Ergebnis und Integrität prüfen, erst dann Erfolg melden.
6. **Fehlerprävention:** ungültige Zustände an Systemgrenzen abfangen.
7. **Fallback statt Totalausfall:** lokale Fehler möglichst isolieren.
8. **Transparenz:** Laienmeldung verständlich, technische Details protokollierbar.
9. **Keine Nutzerabnahme:** Tests und Release-Gate sind automatisiert.
10. **Regression lernt:** bestätigte Fehler erweitern das Sicherheitsnetz dauerhaft.
11. **Zwei Vorgänger:** `backup/previous-1` und `backup/previous-2` müssen rückholbar bleiben.
12. **Dokumentationssynchronität:** Verhalten, Hilfe, Manifest, Status und Changelog gemeinsam pflegen.
