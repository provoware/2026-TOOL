#!/usr/bin/env python3
"""Deterministische CI-Gates passend zu den drei Subagentenrollen."""
from __future__ import annotations
import argparse, subprocess

def changed(base: str|None, head: str) -> list[str]:
    if not base or set(base)=={"0"}: cmd=["git","show","--pretty=","--name-only",head]
    else: cmd=["git","diff","--name-only",base,head]
    p=subprocess.run(cmd,text=True,capture_output=True,check=False)
    if p.returncode:
        p=subprocess.run(["git","show","--pretty=","--name-only",head],text=True,capture_output=True,check=True)
    return sorted({x.strip() for x in p.stdout.splitlines() if x.strip()})

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=["analyse","plan","compliance"],required=True);ap.add_argument("--base");ap.add_argument("--head",default="HEAD");a=ap.parse_args()
    files=changed(a.base,a.head);code=[f for f in files if f.startswith(("app/","scripts/")) or f.startswith(".github/workflows/")];tests=[f for f in files if f.startswith("tests/")];risks=[]
    if any(f.startswith("app/server.py") for f in files): risks.append("Persistenz/API/Startdienst")
    if any(f.startswith(".github/workflows/") for f in files): risks.append("CI/Backup/Release")
    if any(f.startswith("app/static/") for f in files): risks.append("UI/Barrierefreiheit/Layout")
    print(f"# {a.mode.capitalize()}-Gate\n");print(f"Geänderte Dateien: {len(files)}");print("Risiken: "+(", ".join(risks) if risks else "niedrig/keine Kernkomponente erkannt"))
    if a.mode=="analyse": print("Ergebnis: Analyse abgeschlossen; keine Dateien wurden durch dieses Gate verändert.");return
    if a.mode=="plan":
        if code and "TODO.md" not in files: print("BLOCKIERT: Code/Workflow geändert, aber TODO.md nicht mitgeführt.");raise SystemExit(1)
        print("Ergebnis: Planbezug vorhanden.");return
    missing=[]
    if code and not tests: missing.append("Tests")
    if code and "CHANGELOG.md" not in files: missing.append("CHANGELOG.md")
    if code and "PROJEKTSTATUS.md" not in files: missing.append("PROJEKTSTATUS.md")
    if missing: print("BLOCKIERT: Umsetzung ohne "+", ".join(missing));raise SystemExit(1)
    print("Ergebnis: Plan-Konformität der harten Regeln bestanden.")
if __name__=="__main__": main()
