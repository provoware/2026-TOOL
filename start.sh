#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'FEHLER: Python 3 wurde nicht gefunden.\n' >&2
  exit 1
fi

exec python3 app/server.py --open-browser
