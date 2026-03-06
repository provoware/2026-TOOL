#AGENTS.md
Fokus: Planung vor Aktion, minimale Eingriffe, saubere Iterationen, robuste Wartbarkeit
1. Grundprinzip

Planung ist Gold, Handlung ist Silber.

Vor jeder Änderung erst ermitteln, eingrenzen, begründen, planen.

Erst patchen, wenn klar ist:

was geändert wird

wo es geändert wird

warum es geändert wird

was bewusst nicht geändert wird

Keine hektischen Schnellschüsse.

Keine unnötigen Folgeänderungen.

Keine unbegründeten Eingriffe in stabile Bereiche.

Immer kleinster sinnvoller Eingriff.

Immer maximale Wirkung bei minimaler Änderung.

2. Effizienz-Regeln für Entwicklung

Nur betroffene Dateien anfassen.

Nur betroffene Zeilen oder Blöcke ändern.

Keine ganzen Dateien neu schreiben, wenn ein lokaler Patch reicht.

Keine unnötige Umformatierung großer Bereiche.

Keine stilistischen Nebenumbauten ohne echten Nutzen.

Keine doppelte Bearbeitung derselben Stelle in einer Iteration.

Keine Prüfung derselben Logik mehrfach ohne neue Änderung.

Keine Vollprüfung des gesamten Projekts bei lokalen Patches.

Keine unnötigen Neuberechnungen, Neu-Scans oder Wiederholungsanalysen.

Keine unnötigen Doku-Änderungen ohne echtes Verhaltensupdate.

3. Traffic-Sparsamkeit und Prüfsparsamkeit

Arbeite datenarm und prüfarm.

Nutze gezielte Prüfungen statt Vollrundschlag.

Prüfe nur:

direkt geänderte Logik

direkt betroffene Abhängigkeiten

direkt betroffene Ausgabe

Keine Endlos-Prüfschleifen.

Keine identischen Prüfläufe mehrfach.

Kein wiederholtes Öffnen oder Analysieren unveränderter Dateien.

Keine globale Formatierung bei lokalen Fixes.

Keine komplette Test-Suite ohne konkreten Anlass.

Erst planen, dann gesammelt patchen, dann einmal gezielt validieren.

Bei jeder Iteration möglichst wenige Dateioperationen, wenige Prüfdurchläufe, wenige unnötige Dateizugriffe.

4. Pflichtablauf je Iteration
4.1 Voranalyse

Ziel der Iteration klar benennen.

Betroffene Datei oder Dateien exakt bestimmen.

Betroffene Zeilen, Bereiche oder Funktionen eingrenzen.

Patchgrund je Stelle festhalten.

Risiken kurz bewerten.

Folgewirkungen grob abschätzen.

Prüfen, ob Nebeneffekte wirklich relevant sind.

4.2 Patchliste erstellen

Vor jeder Umsetzung eine Schrittliste anlegen mit:

laufender Nummer

Datei

Zeilenbereich oder Blockname

Patchgrund

Art der Änderung

erwartetes Ergebnis

nötige Endvalidierung

Risiko niedrig/mittel/hoch

4.3 Umsetzung

Nur gelistete Stellen ändern.

Nur begründete Anpassungen durchführen.

Keine Zusatzoptimierungen außerhalb des Ziels.

Keine neue Baustelle aufmachen.

Keine ungeplanten Refactorings.

Keine anderen Dateien anfassen, nur weil sie „auch noch verbessert werden könnten“.

4.4 Endvalidierung

Erst nach Abschluss aller Patches.

Nur relevante Prüfungen ausführen:

Syntax

direkt betroffene Funktion

direkt betroffene Ausgabe

relevante Abhängigkeiten

Keine Gesamtprüfung ohne Notwendigkeit.

Keine Wiederholungsprüfung ohne neue Änderung.

5. Exaktes Patchen an Ort und Stelle

Arbeite patchbasiert, nicht flächig.

Nutze wenn möglich:

Zeilennummern

Funktionsnamen

Blockbezeichner

eindeutige Marker

Ersetze nur den kleinsten sinnvollen Bereich.

Keine komplette Datei ersetzen, wenn ein Block reicht.

Keine Verschiebung funktionierenden Codes ohne zwingenden Grund.

Keine Umbenennung funktionierender Strukturen ohne Mehrwert.

6. Regeln für Dateiberührung

Eine Datei darf nur geändert werden bei:

direktem Fehlerbezug

direktem Funktionsbezug

zwingender Abhängigkeit

notwendiger Konfigurationsänderung

echter Doku-Änderung durch neues Verhalten

notwendigem Todo-/Changelog-Eintrag

Nicht erlaubt:

vorsorgliches Mitanfassen

Schönheitskorrekturen ohne Zweck

Stilangleichung ohne Nutzen

Umstrukturierung aus Gewohnheit

diffuse „wenn wir schon mal hier sind“-Änderungen

7. Konflikte und Folgeprobleme

Wird beim Patchen ein weiteres Problem sichtbar:

nicht sofort unkontrolliert ausweiten

erst prüfen, ob aktueller Patch sicher abgeschlossen werden kann

Wenn nicht sauber in derselben Iteration lösbar:

nicht erzwingen

dokumentieren

als Todo für nächste Iteration anlegen

Keine halbfertigen Nebenlösungen.

Keine instabilen Zwischenzustände erzeugen.

8. Todo-Regel

todo.txt immer aktuell halten bei:

offenem Konflikt

bewusst verschobenem Problem

relevantem Folgepatch

notwendiger Nachvalidierung

bewusst ausgelassener, aber erkannter Baustelle

Format:

[ ] Datum | Bereich | Aufgabe | prüfen: … | fertig wenn: …
[x] Datum | Bereich | erledigt | geprüft: …

Zusätzlich kurz notieren:

wo entdeckt

warum verschoben

was in nächster Iteration zu tun ist

9. Dokumentations-Regeln

Dokumentation nur anpassen, wenn:

Verhalten sich geändert hat

Bedienung sich geändert hat

neue Funktion hinzugekommen ist

Konfiguration erweitert wurde

Fehlerhilfe ergänzt werden muss

Keine unnötigen Umschreibungen.
Keine Textlawinen ohne Mehrwert.
Doku klar, kurz, vollständig und laienverständlich halten.

10. Codesparsamkeit

Weniger Code ist besser, wenn die Funktion stabil bleibt.

Keine doppelte Logik.

Keine verteilten Sonderlösungen, wenn eine zentrale Hilfsfunktion reicht.

Keine unnötig verschachtelten Konstruktionen.

Keine überflüssigen Wrapper.

Keine unnötigen Zwischenvariablen.

Kein unnötiger Boilerplate-Code.

Bestehende, stabile Hilfsfunktionen bevorzugt wiederverwenden.

Neue Funktionen klein und klar halten.

Ziel:

weniger Angriffsfläche

weniger Wartungsaufwand

weniger Testaufwand

weniger Folgefehler

11. Regeln für Wartbarkeit
Dateigrößen

Empfohlene Grenzen:

Hilfsdateien / kleine Module: möglichst bis 150 Zeilen

normale Moduldateien: möglichst bis 300 Zeilen

komplexere Kernmodule: möglichst bis 500 Zeilen

über 500 Zeilen: prüfen, ob sinnvoll teilbar

über 800 Zeilen: grundsätzlich Teilung prüfen und begründen

Funktionsgrößen

kleine Hilfsfunktionen: ideal 5–25 Zeilen

normale Funktionen: möglichst unter 40 Zeilen

über 60 Zeilen: prüfen, ob teilbar

über 100 Zeilen: nur mit klarer Begründung

Strukturregeln

eine Datei = ein klarer Hauptzweck

keine Mischdateien für alles

Konfiguration getrennt von Logik

variable Daten getrennt vom System

Tests getrennt vom Produktivcode

UI getrennt von Geschäftslogik

Hilfsfunktionen zentral bündeln

magische Werte vermeiden, stattdessen zentrale Defaults

12. Barrierefreiheit und Laienfokus

Alle Rückmeldungen in einfacher Sprache.

Fachbegriffe nur bei Bedarf, dann kurz in Klammern erklärt.

Fehlermeldungen mit:

Ursache

Auswirkung

einfacher Lösung

Nutzerführung klar und ruhig.

Keine überladene Technik-Ausgabe im Standardmodus.

Hilfetexte direkt dort, wo sie gebraucht werden.

Buttons, Farben, Kontraste, Fokuszustände immer mitdenken.

Eingaben und Ergebnisse immer validieren.

13. Validierung

Jede Funktion prüft:

vor der Aktion

Eingabe vorhanden?

Format korrekt?

Pfad gültig?

Datei vorhanden?

Werte erlaubt?

nach der Aktion

Aktion erfolgreich?

Ziel wirklich erzeugt oder geändert?

Ausgabe vollständig?

Ergebnis lesbar/verwendbar?

bei Fehlern Rückmeldung vorhanden?

Iterationsende

nur geänderte Bereiche validieren

keine unnötige Gesamtprüfung

Ergebnis dokumentieren

14. Logging und Debugging
Normalmodus

kurz

klar

laienverständlich

handlungsorientiert

Debugmodus

technische Ursache

betroffene Datei/Funktion

Fehlerstelle

Lösungsvorschlag

nächster Prüfschritt

Logging-Regeln

nur Relevantes loggen

keine Log-Flut

Zeitstempel verwenden

Reparaturen dokumentieren

verschobene Konflikte dokumentieren

15. Verbindliche Iterations-Ausgabe

Jede Iteration endet mit:

A. Änderungsprotokoll

was genau geändert wurde

warum es geändert wurde

welche Dateien bewusst nicht angefasst wurden

welche Endvalidierung ausgeführt wurde

welche Konflikte verschoben wurden

B. Zwei konstruktive Empfehlungen

Immer zwei kurze, hilfreiche Empfehlungen ausgeben, zum Beispiel:

sinnvoller nächster Stabilitätsschritt

Verbesserungsoption für Barrierefreiheit

Empfehlung zur Vereinfachung

Vorschlag zur späteren Modultrennung

Hinweis auf Doku oder Testlücke

Diese zwei Empfehlungen müssen:

konkret

begründet

umsetzbar

unterstützend
sein.

Arbeite strikt planungsbasiert, patchbasiert, codesparsam und traffic-sparsam. Planung ist Gold, Handlung ist Silber. Vor jeder Änderung zuerst Ziel, betroffene Dateien, betroffene Zeilen oder Blöcke, Patchgrund, Risiken und bewusste Nicht-Änderungen ermitteln. Danach eine konkrete Schrittliste erstellen. Nur dann patchen.

Ändere nur begründet betroffene Dateien und nur die exakt betroffenen Stellen. Keine unnötigen Änderungen an stabilen Bereichen, keine kosmetischen Nebenanpassungen, keine globalen Umformatierungen, keine Volltests ohne Anlass, keine Endlos-Prüfschleifen, keine Wiederholungsprüfungen ohne neue Änderung, keine unnötigen Dateioperationen und keine unnötigen Dateizugriffe. Immer kleinster sinnvoller Eingriff.

Validierung erfolgt grundsätzlich erst am Ende aller Patches einer Iteration. Dabei nur relevante Prüfungen ausführen: Syntax, direkt betroffene Logik, direkt betroffene Ausgabe und nur wirklich betroffene Tests. Nicht veränderte Dateien und Bereiche sollen weder unnötig erneut geprüft noch erneut analysiert werden.

Dokumentation nur bei echter Verhaltensänderung anpassen. Offene Konflikte oder Folgeprobleme nicht ungeplant mitbearbeiten, sondern sauber in todo.txt für die nächste Iteration dokumentieren. Jede Iteration endet mit einem kompakten Änderungsprotokoll, klarer Endvalidierung und zwei konstruktiven, unterstützenden Empfehlungen.

Achte auf maximale Wartbarkeit: kleine, klar getrennte Dateien und Funktionen, getrennte Logik-, Config-, Daten-, Test- und Doku-Bereiche. Empfohlene Grenzen: Hilfsdateien bis 150 Zeilen, normale Module bis 300 Zeilen, Kernmodule bis 500 Zeilen; darüber Teilung prüfen. Funktionen möglichst unter 40 Zeilen, über 60 Zeilen Teilbarkeit prüfen. Alle Ausgaben in einfacher Sprache, Fachbegriffe nur kurz erklärt in Klammern.
Kein Patch ohne Patchgrund. Keine Datei ohne Anlass. Keine Prüfung ohne Ziel. Keine Wiederholung ohne neue Änderung. Keine Erweiterung der Iteration bei neu entdeckten Nebenproblemen, wenn diese nicht sauber isoliert lösbar sind. Stattdessen Todo-Eintrag mit Begründung, Prüfschritt und Fertig-Kriterium anlegen.
Bevor Code geschrieben wird, immer prüfen, ob der gewünschte Effekt mit kleinerem Eingriff, Wiederverwendung bestehender Logik oder besserer Planung erreichbar ist. Erst minimaler Plan, dann minimaler Patch, dann minimale zielgerichtete Validierung.
lieber 3 saubere Patches als 12 halbverwandte Änderungen. Das hält Iterationen kontrollierbar.
Pflicht-Abbruch bei Iterationsaufweitung, also: wenn mehr als ein neuer Konflikt auftaucht, aktuellen Patch sauber abschließen und Rest in todo.txt verschieben.
 strenge Patch-Checkliste für jede Iteration
 
