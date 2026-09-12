# Iteration 2.3 – Backup-Reliability-Hotfix v0.2.3

## Ausgangsfehler
Der `main`-Release v0.2.2 bestand Release- und Subagent-Gates, aber die Workflow-Rotation der Rückfallzweige schlug fehl. Root Cause: Der `GITHUB_TOKEN` darf einen Branch nicht auf einen Commit verschieben, dessen Diff Workflow-Dateien unter `.github/workflows/` verändert, solange dem GitHub-App-Token die spezielle Workflow-Berechtigung fehlt.

Die beiden vorhandenen Rückfallzweige blieben dabei inhaltlich korrekt auf v0.2.1 und v0.2.0 stehen; es trat kein Datenverlust auf.

## Ziel
Automatisch immer zwei vollständige, verifizierte Quell-Snapshots der beiden vorherigen `main`-Stände halten, ohne Ref-Rotation auf historische Commits und ohne zusätzliche GitHub-Berechtigung.

## Lösung
1. Ein einmalig angelegter Zweig `backup/snapshots` bleibt als technischer Speicherzweig bestehen.
2. Bei jedem Push auf `main` erzeugt die Backup-Automation mit `git archive`:
   - `version-backups/previous-1.zip` aus `github.event.before`,
   - `version-backups/previous-2.zip` aus dessen erstem Eltern-Commit.
3. Jedes ZIP wird mit Python/ZIP-Test vollständig geprüft.
4. Für jedes ZIP wird SHA-256 berechnet.
5. `version-backups/manifest.json` dokumentiert Slot, Commit, SHA-256, Dateiname und Erzeugungszeit.
6. Auf `backup/snapshots` werden ausschließlich `version-backups/*` verändert. Die dort eingefrorenen `.github/workflows/*` bleiben unverändert; dadurch greift die GitHub-App-Workflow-Sperre nicht.
7. Die alten `backup/previous-1` und `backup/previous-2` bleiben als Legacy-Rückfallpunkte bestehen, sind aber nicht mehr die automatische Primärstrategie.

## Sicherheitsregeln
- Kein Backup gilt als erfolgreich, solange ZIP-Test oder SHA-Erzeugung scheitern.
- Das aktuelle `main` wird nie verändert.
- Keine Nutzer-/Projektdateien werden gelöscht.
- Bei fehlendem Vorgänger wird der betreffende Slot ausdrücklich als nicht verfügbar dokumentiert.
- Backup-Commit enthält nur neue Snapshotdateien/Manifest.
- Ein fehlerhafter Backup-Lauf blockiert die Release-Abschlussbewertung, aber nicht die bereits veröffentlichte Quellversion.

## Regression
Automatischer Test erzeugt ein temporäres Git-Repository mit drei Ständen, baut zwei Snapshots und prüft:
- Slot 1 enthält exakt den ersten Vorgänger,
- Slot 2 enthält exakt dessen ersten Vorgänger,
- ZIPs sind fehlerfrei lesbar,
- SHA-256 im Manifest stimmt,
- Workflow-Dateien innerhalb des ZIPs bleiben vollständig enthalten.

## Definition of Done
- Release-/Subagent-Gates im PR grün.
- Hotfix auf `main`.
- neuer Backup-Workflow läuft auf `main` grün.
- `backup/snapshots/version-backups/previous-1.zip` und `previous-2.zip` vorhanden.
- Manifest-SHAs nachvollziehbar.
- Backup-Zweig selbst verändert bei der Rotation keine `.github/workflows/*`.
