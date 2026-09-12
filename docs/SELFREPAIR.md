# Self-Repair-Standard v1

## Zweck
Self-Repair soll bekannte, eindeutig sichere Fehlerzustände automatisch korrigieren, ohne Nutzerdaten zu interpretieren, zu löschen oder zu überschreiben. Die Schicht liegt in `app/self_repair.py` und ist bewusst von Fachlogik, Projektpersistenz, SQLite-Datenkern und HTTP-API getrennt.

## Grundsatz
`erkennen → validieren → Rückfall prüfen → Original sichern/quarantänisieren → reparieren → nachvalidieren → protokollieren`

Fehlt an irgendeinem Punkt eine eindeutige Sicherheitsgarantie, wird **nicht repariert**.

## Automatisch erlaubte Reparaturen
1. **Konfiguration:** beschädigte `config.json` nur aus einer syntaktisch und strukturell gültigen `config.json.tmp`, `.bak1` oder `.bak2` wiederherstellen.
2. **Quarantäne:** beschädigtes Original vor Ersatz umbenennen; keine stille Löschung.
3. **Projektstruktur:** fehlende PROVOWARE-Standardordner nur erzeugen, wenn `.provoware/project.json` vollständig und inhaltlich gültig ist.
4. **SQLite:** ausschließlich den vorhandenen `DataCore.ensure_ready()` nutzen. Dieser akzeptiert nur zuvor geprüfte Datenbanksicherungen und hält die defekte Datenbank in Quarantäne.
5. **Ableitbare Zustände:** temporäre, regenerierbare Artefakte dürfen quarantänisiert oder neu aufgebaut werden, sofern keine Nutzerdaten enthalten sind.

## Automatisch verbotene Reparaturen
- Nutzerdaten löschen oder überschreiben.
- einen fehlenden oder ungültigen Projektmarker neu erfinden.
- einen fremden, nichtleeren Ordner automatisch als PROVOWARE-Projekt übernehmen.
- eine Datei an Stelle eines erwarteten Standardordners löschen oder ersetzen.
- ungeprüfte Backups einspielen.
- zwischen mehreren plausiblen Nutzerständen automatisch entscheiden.
- eine irreversible R4-Aktion als Reparatur ausführen.

## Konfiguration
Die Konfiguration besitzt zwei normale Rückfallkopien. Bei defekter Hauptdatei wird die erste tatsächlich valide Quelle in dieser Reihenfolge geprüft:
1. `config.json.tmp` – kann einen unterbrochenen atomaren Schreibvorgang enthalten,
2. `config.json.bak1`,
3. `config.json.bak2`.

Vor einem Restore wird das defekte Original als `config.json.corrupt-<zeitstempel>` quarantänisiert. Nach Restore wird die neue Hauptdatei erneut validiert. Scheitert diese Nachvalidierung, wird der Vorgang zurückgerollt.

## Projektmarker
Ein Projekt ist nur freigegeben, wenn `.provoware/project.json`:
- valides JSON ist,
- `schema_version = 1` enthält,
- `app = "PROVOWARE HEADQUARTER"` enthält,
- einen nichtleeren Projektnamen besitzt.

Ein konfigurierter Pfad mit ungültigem Marker bleibt für Diagnose sichtbar, wird aber nicht als aktives Projekt verwendet.

## Dateisicherheit
Kritische JSON-Schreibvorgänge verwenden Tempdatei, `fsync`, atomaren `os.replace()` und – soweit das Dateisystem dies unterstützt – anschließendes Synchronisieren des Elternverzeichnisses. Das reduziert das Risiko eines halbfertigen Zustands nach Crash oder Stromverlust.

## Diagnose vs. Reparatur
`GET /api/self-repair/status` ist read-only. Es meldet nur Zustände.

`POST /api/self-repair/run` darf ausschließlich die Allowlist ausführen. Bei einer blockierenden Mehrdeutigkeit antwortet der Dienst ohne riskante Änderung mit einem Fehlerstatus.

## Protokollierung
Self-Repair schreibt append-only JSONL-Ereignisse nach `logs/selfrepair.jsonl`. Protokollausfall darf eine ansonsten sichere Reparatur nicht in einen zweiten Datenfehler verwandeln.

## Fertig-Kriterium einer Reparatur
Eine Reparatur gilt nur als erfolgreich, wenn:
1. ursprünglicher Fehler erkannt wurde,
2. Rückfallquelle oder Projektidentität validiert wurde,
3. Änderung innerhalb der Allowlist liegt,
4. Nachvalidierung bestanden ist,
5. kein nicht auflösbarer Konflikt besteht,
6. der Zustand protokolliert wurde, soweit Logging verfügbar ist.
