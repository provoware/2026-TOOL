# Hotfix – Backup-Ref-Rotation nach v0.2.2

## Zweck dieser Datei
Diese Datei dokumentiert den **ersten und zweiten fehlgeschlagenen Lösungsweg**, damit die Fehlerklasse nicht später versehentlich wieder eingeführt wird. Die aktuelle Lösung steht in `ITERATION_023_BACKUP_HOTFIX.md`.

## Ausgangsbefund
Der v0.2.2-Hauptstand bestand Release- und Subagent-Gates. Der separate Workflow `Zwei Vorgängerversionen halten` scheiterte beim Verschieben historischer Backup-Zweige.

## Versuch 1 – `git push --force`
GitHub verweigerte die Aktualisierung eines Backup-Branches auf einen historischen Commit, weil dieser geänderte `.github/workflows/*` enthielt und der GitHub-App-Token keine spezielle Workflow-Schreibberechtigung besaß.

Ergebnis: **verworfen**.

## Versuch 2 – GitHub Ref API
Daraufhin wurde die Rotation auf `gh api` PATCH/POST für `git/refs` umgestellt und eine SHA-Nachvalidierung ergänzt.

Der reale Post-Merge-Lauf scheiterte ebenfalls:
- HTTP 403,
- `Resource not accessible by integration`.

Ergebnis: **ebenfalls verworfen**.

## Schlussfolgerung
Das Problem ist nicht die konkrete Transportmethode (`git push` versus REST API), sondern die Integrations-/Berechtigungsgrenze bei historischen Refs mit Workflow-Inhalt. Ein weiterer direkter Ref-Rotationsversuch wäre nur Symptombehandlung.

## Nachfolgelösung
Die Primärstrategie wird deshalb auf **verifizierte Git-Archive als ZIP-Snapshots** umgestellt:
- `backup/snapshots` als einmalig angelegter technischer Speicherzweig,
- `version-backups/previous-1.zip`,
- `version-backups/previous-2.zip`,
- Manifest mit Commit-IDs und SHA-256,
- ZIP-Inhaltsprüfung,
- Rotation verändert ausschließlich `version-backups/*`.

Die Archive enthalten die Workflow-Dateien des gesicherten Stands, ohne dass das Actions-Token die Workflow-Dateien des technischen Speicherzweigs ändern muss.

## Regressionsregel
Tests müssen dauerhaft verhindern, dass `gh api`-Ref-Rotation oder `git push --force` wieder als Primärstrategie eingeführt wird, solange keine ausdrücklich geeignete Repositoryberechtigung eingerichtet und separat verifiziert wurde.
