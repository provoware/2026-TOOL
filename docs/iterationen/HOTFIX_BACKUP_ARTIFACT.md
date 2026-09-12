# Hotfix 2 – Backup ohne Repository-Schreibrecht

## Root Cause
Auch die Ref-API-Variante scheiterte im GitHub-Actions-Kontext beim Schreibschritt. Damit ist nicht die Git-Syntax, sondern die Schreibberechtigung des Workflow-Tokens die instabile Abhängigkeit.

## Entscheidung
Die automatische Sicherung darf nicht länger Schreibrecht auf das Repository benötigen. Der Workflow erzeugt stattdessen aus den zwei vorherigen `main`-Ständen:
- zwei vollständige `tar.gz`-Quellarchive,
- ein Git-Bundle mit beiden Commitständen,
- ein Manifest mit den exakten Commit-SHAs,
- SHA-256-Prüfsummen.

Danach werden Archive und Git-Bundle lokal im Runner validiert und als GitHub-Actions-Artefakt hochgeladen. Das Workflowrecht wird auf `contents: read` reduziert.

## Wiederherstellung
Das Git-Bundle enthält beide vollständigen Gitstände und kann in ein Repository eingelesen werden. Die tar.gz-Dateien ermöglichen zusätzlich eine einfache Dateiwiederherstellung ohne Gitkenntnisse.

## Rückfallzweige
Die bereits vorhandenen `backup/previous-1` und `backup/previous-2` bleiben als manuell verifizierte Spiegel erhalten, sind aber nicht mehr die automatische Primärsicherung. Primär ist das geprüfte Zwei-Versionen-Artefakt des jeweils letzten erfolgreichen Backup-Laufs.

## Qualitätsregel
Der Workflow gilt nur als erfolgreich, wenn beide Archive lesbar sind, das Git-Bundle `git bundle verify` besteht, Prüfsummen erzeugt wurden und das Artefakt hochgeladen wurde.
