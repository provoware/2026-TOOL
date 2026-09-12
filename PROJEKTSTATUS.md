# Projektstatus

## Produktlaufzeit
**v0.2.2 – UX, Feedback & Transparenz** bleibt unverändert und freigegeben.

## Release-Engineering
**Hotfix v0.2.3 – Backup Reliability**

## Status
🟢 **Freigegeben** – Snapshot-Backupstrategie ist auf dem echten `main`-Stand erfolgreich gelaufen und vollständig nachgeprüft.

## Freigegebene Produktbasis
- Expert Shell A–N,
- SQLite-WAL-Datenkern, Todo, Kalender und reversibles Archiv,
- Crash-/Recovery-Schutz,
- Reliability & Self-Repair,
- globale UX-/Prozessanzeige, Warn-/Fehlerzähler, Zoom 100–200 %, Fokus/ARIA,
- sieben read-only Prüfrollen mit R0–R4.

## Bestätigte Fehlerursache und Lernschutz
Zwei Varianten direkter historischer Ref-Rotation wurden real getestet und verworfen:
1. `git push --force` scheiterte an der GitHub-App-Workflow-Berechtigungsgrenze.
2. GitHub Ref API (`gh api` PATCH/POST) scheiterte ebenfalls mit HTTP 403 `Resource not accessible by integration`.

Die Fehlerklasse ist dokumentiert und durch Regression davor geschützt, versehentlich wieder als Primärstrategie eingeführt zu werden.

## Freigegebene Backupstrategie
- technischer Speicherzweig `backup/snapshots`,
- `version-backups/previous-1.zip` und `previous-2.zip`,
- vollständige Workflow-Dateien innerhalb der Archive,
- ZIP-Integritätsprüfung,
- SHA-256 pro Snapshot,
- Manifest mit Commit-ID, Hash, Datei- und Größenwerten,
- automatische Rotation verändert auf dem Speicherzweig ausschließlich `version-backups/*`.

## Nachgewiesene Release-Evidenz
### Pull Request #9
- Release-Gate: 🟢 erfolgreich.
- Analyse: 🟢.
- Risiko: 🟢.
- Fehlerursache: 🟢.
- Plan: 🟢.
- Regression: 🟢.
- Plan-Prüfung: 🟢.
- Release-Prüfung: 🟢.

### Gemergter Hauptstand
- Squash-Commit: `597f2337bba4eb961b61a4455db4b00824716b69`.
- Release-Gate Run 35: 🟢 erfolgreich.
- Subagent-Gates Run 33: 🟢 alle sieben Stufen erfolgreich.
- Backupworkflow Run 13: 🟢 erfolgreich.

### Tatsächlich erzeugte Rückfallstände
`backup/snapshots/version-backups/manifest.json` bestätigt:
- `previous-1.zip` → Commit `217fb9f748207f23d474043d78f16e018380bef7`, SHA-256 `35db10f42c1a5c1d75ba3379896c6184b574648091fdd2885ee05f97386015f9`.
- `previous-2.zip` → Commit `b5393392dd62c547a9cce832f35a1101a1509dac`, SHA-256 `9e8b7047313b3b702e57c7b8619a74c321a5e3c779f44b7aeca0c6acc508a4b0`.

Beide ZIP-Dateien und das Manifest wurden repositoryseitig tatsächlich gefunden; die ZIP-Integrität wurde im erfolgreichen Workflow vor Veröffentlichung geprüft.

## Bekannte externe Schutzlücke
`main` ist repositoryseitig weiterhin nicht durch Branch-Protection/Ruleset geschützt. Automatische Gates sind aktiv, können einen ausreichend berechtigten direkten Push aber nicht technisch verhindern. Dieser Punkt bleibt bewusst offen in `docs/OFFENE_RISIKEN.md`.

## Nächste Entwicklungsstufe
Der Infrastrukturkern ist jetzt ausreichend robust, um den ersten unmittelbar nützlichen Dateisortier-Workflow zu bauen. Empfohlene Reihenfolge:
**Jobmanager → Datei-Aktionsjournal/Undo → Ordneranalyse → Dateitypregeln per Auswahl → Konfliktprüfung → Vorschau → sichere Ausführung → Abschluss/Undo.**

## Nutzer-Abnahme
Nicht erforderlich. Automatische Evidenz wurde nicht durch manuelles Nutzertesten ersetzt.
