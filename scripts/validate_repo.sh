#!/usr/bin/env bash
set -euo pipefail

required=(
  README.md
  PROJEKTSTATUS.md
  TODO.md
  CHANGELOG.md
  AGENTS.md
  ENTWICKLUNGSREGELN.md
  ENTWICKLERDOKU.md
  docs/ARCHITEKTUR.md
  docs/QUALITAETSSICHERUNG.md
  tests/README.md
)

missing=0
for file in "${required[@]}"; do
  if [[ -f "$file" ]]; then
    printf 'OK   %s\n' "$file"
  else
    printf 'FEHLT %s\n' "$file"
    missing=$((missing + 1))
  fi
done

if (( missing > 0 )); then
  printf '\nRepository-Prüfung fehlgeschlagen: %d Pflichtdatei(en) fehlen.\n' "$missing"
  exit 1
fi

printf '\nRepository-Grundstruktur ist vollständig.\n'
