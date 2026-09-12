#!/usr/bin/env python3
"""Deterministische, risikobasierte Gates für die PROVOWARE-Subagenten."""
from __future__ import annotations
import argparse, subprocess
MODES=("analyse","risk","rootcause","plan","regression","compliance","release")
RISK_ORDER={"R0":0,"R1":1,"R2":2,"R3":3,"R4":4}
R3_PATHS=("app/data_core.py","app/project_store.py","app/self_repair.py","app/server.py",".github/workflows/","scripts/agent_gate.py","scripts/validate_","AGENTS.md",".agents/")
R1_PREFIXES=("app/static/",); R2_PREFIXES=("app/","scripts/")
PROTECTED_DELETE_PATHS=("app/","scripts/","tests/",".github/",".agents/","AGENTS.md","projekt-manifest.json")
AGENT_PATHS=("AGENTS.md",".agents/",".github/workflows/agents.yml","scripts/agent_gate.py","scripts/validate_agents.py")
def _run(cmd): return subprocess.run(cmd,text=True,capture_output=True,check=False)
def changed(base,head):
    cmd=["git","show","--pretty=","--name-only",head] if not base or set(base)=={"0"} else ["git","diff","--name-only",base,head]; r=_run(cmd)
    if r.returncode: r=subprocess.run(["git","show","--pretty=","--name-only",head],text=True,capture_output=True,check=True)
    return sorted({x.strip() for x in r.stdout.splitlines() if x.strip()})
def deleted(base,head):
    if not base or set(base)=={"0"}: return []
    r=_run(["git","diff","--diff-filter=D","--name-only",base,head]); return sorted({x.strip() for x in r.stdout.splitlines() if x.strip()}) if r.returncode==0 else []
def _matches(path,patterns): return any(path==item or path.startswith(item) for item in patterns)
def risk_level(files,removed):
    reasons=[]; level="R0"
    for path in files:
        if _matches(path,R1_PREFIXES):
            if RISK_ORDER[level]<1: level="R1"
            reasons.append("Darstellung/UI")
        elif _matches(path,R2_PREFIXES):
            if RISK_ORDER[level]<2: level="R2"
            reasons.append("Fachlogik/API")
        if _matches(path,R3_PATHS): level="R3"; reasons.append(f"Kern-/Qualitätsgrenze: {path}")
    if any(_matches(path,PROTECTED_DELETE_PATHS) for path in removed): level="R4"; reasons.append("Produktiv-, Test- oder Qualitätsvertrag gelöscht")
    return level,reasons
def main():
    p=argparse.ArgumentParser(); p.add_argument("--mode",choices=MODES,required=True); p.add_argument("--base"); p.add_argument("--head",default="HEAD"); a=p.parse_args(); files=changed(a.base,a.head); removed=deleted(a.base,a.head); risk,reasons=risk_level(files,removed); code=[f for f in files if f.startswith(("app/","scripts/",".github/workflows/"))]; tests=[f for f in files if f.startswith("tests/")]; plan=[f for f in files if f=="TODO.md" or f.startswith("docs/iterationen/")]; agent=[f for f in files if _matches(f,AGENT_PATHS)]
    print(f"# {a.mode} Gate\nGeänderte Dateien: {len(files)}\nRisikoklasse: {risk}\nRisikogründe: "+(", ".join(dict.fromkeys(reasons)) if reasons else "keine Laufzeitänderung erkannt"))
    if removed: print("Gelöscht: "+", ".join(removed))
    if a.mode=="analyse": print("Ergebnis: read-only Analyse abgeschlossen."); return
    if a.mode=="risk":
        if risk=="R4": print("BLOCKIERT: R4 ist standardmäßig nicht automatisch freigabefähig."); raise SystemExit(1)
        print(f"Ergebnis: {risk} erkannt."); return
    if a.mode=="rootcause": print("Trigger: aktiv." if risk in {"R3","R4"} or any("test" in f.lower() for f in files) else "Trigger: nicht erforderlich für diesen Diff."); return
    if a.mode=="plan":
        if code and not plan: print("BLOCKIERT: Laufzeit-/Workflowänderung ohne Plan/TODO."); raise SystemExit(1)
        print("Ergebnis: Planbezug vorhanden."); return
    if a.mode=="regression":
        if risk in {"R1","R2","R3"} and code and not tests: print("BLOCKIERT: R1/R2/R3-Änderung ohne geänderte Regressionstests."); raise SystemExit(1)
        print("Ergebnis: Regressionsschutz berücksichtigt."); return
    if a.mode=="compliance":
        missing=[]
        if code and "CHANGELOG.md" not in files: missing.append("CHANGELOG.md")
        if code and "PROJEKTSTATUS.md" not in files: missing.append("PROJEKTSTATUS.md")
        if risk=="R3" and "projekt-manifest.json" not in files: missing.append("projekt-manifest.json")
        if agent and "AGENTS.md" not in files: missing.append("AGENTS.md")
        if missing: print("BLOCKIERT: Pflichtartefakte fehlen: "+", ".join(sorted(set(missing)))); raise SystemExit(1)
        print("Ergebnis: Plan-/Scope-/Dokumentationskonformität bestanden."); return
    if a.mode=="release":
        if risk=="R4": print("BLOCKIERT: R4 darf nicht automatisch freigegeben werden."); raise SystemExit(1)
        r=_run(["git","diff","--check",a.base or f"{a.head}^",a.head])
        if r.returncode: print("BLOCKIERT: git diff --check meldet Fehler.\n"+r.stdout+r.stderr); raise SystemExit(1)
        if risk in {"R1","R2","R3"} and not tests: print("BLOCKIERT: verhaltensändernder Release ohne Teständerung."); raise SystemExit(1)
        print("Ergebnis: deterministische Release-Vorprüfung bestanden.")
if __name__=="__main__": main()
