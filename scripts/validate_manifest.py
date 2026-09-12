#!/usr/bin/env python3
import json
from pathlib import Path
m=json.loads(Path("projekt-manifest.json").read_text(encoding="utf-8"))
errors=[]
if m.get("schema_version") != 1: errors.append("schema_version muss 1 sein")
app=m.get("app",{})
if app.get("version") != "0.1.0": errors.append("App-Version muss 0.1.0 sein")
ui=m.get("ui",{})
if ui.get("areas") != list("ABCDEFGHIJKLMN"): errors.append("A-N-Bereiche unvollständig")
if len(ui.get("themes",[])) != 5: errors.append("genau fünf Themes erforderlich")
q=m.get("quality",{})
if q.get("manual_user_acceptance_required") is not False: errors.append("manuelle Nutzerabnahme muss false sein")
b=m.get("backup",{})
if b.get("keep_previous") != 2: errors.append("zwei Vorgängerversionen erforderlich")
if errors:
    for e in errors: print("FEHLER:",e)
    raise SystemExit(1)
print("OK   Manifest konsistent")
