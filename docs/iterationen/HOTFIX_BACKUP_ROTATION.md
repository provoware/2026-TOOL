# Hotfix – Backup-Ref-Rotation nach v0.2.2

## Befund
Der v0.2.2-Squash-Commit bestand Release- und Subagent-Gates, aber der separate Workflow `Zwei Vorgängerversionen halten` scheiterte beim Schritt, der Backup-Branches per `git push --force` verschiebt.

## Sofortschutz
Die beiden Rückfallzweige wurden manuell auf die korrekten vollständigen Hauptstände gesetzt:
- `backup/previous-1` → v0.2.1-Hauptstand `10ad01a…`
- `backup/previous-2` → v0.2.0-Hauptstand `0748904…`

## Ursachenklasse
Workflow-/Berechtigungsgrenze. Die Backupfunktion soll nicht von einem Force-Push über Git abhängen, wenn GitHub bereits eine Ref-API mit `contents: write` bereitstellt.

## Umsetzung
1. Ref-Rotation über `gh api` PATCH/POST statt `git push --force`.
2. vorhandene Ref aktualisieren, fehlende Ref kontrolliert erzeugen.
3. Ziel-SHAs anschließend mit `git ls-remote` nachvalidieren.
4. zweiter Vorgänger wird aus dem ersten Elterncommit des vorherigen `main`-Heads bestimmt.
5. Workflow-Vertragstest verhindert Rückkehr zu `git push --force`.
6. vollständige Release-/Agenten-Gates vor Merge.

## Sicherheitsregel
Ein Backupfehler verändert keine Nutzdaten und blockiert die Anwendung nicht. Er bleibt jedoch als Qualitätswarnung sichtbar und die Rückfallzweige werden nicht als aktuell behauptet, solange ihre SHAs nicht verifiziert wurden.
