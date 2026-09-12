# Triggerbasierte Subagenten v2

Die Subagenten sind absichtlich getrennt, damit Analyse, Risiko, Planung und Prüfung nicht unbemerkt zu Implementierung werden. Produktivcode wird ausschließlich in der Umsetzungsphase verändert; alle hier beschriebenen Agenten sind Prüf-/Dokumentationsrollen.

## Triggerkette
`Änderung → Analyse → Risiko R0–R4 → Fehlerursachen-Trigger → Plan/TODO → Umsetzung → Regression → Plan-Prüfung → Release-Prüfung → Release-Gate`

### 1. Analyse-Agent
Trigger bei Code-, Test-, Workflow-, Manifest-, Standard- oder Agentenänderungen sowie bei bestätigten Fehlern. Liefert Ist-Zustand, Abhängigkeiten, Risiken, Wiederverwendungsmöglichkeiten und notwendige Prüfungen. Keine Implementierung.

### 2. Risiko-Agent
Klassifiziert R0 bis R4 und bestimmt die notwendige Prüftiefe. R3 verlangt besondere Persistenz-/Recoveryprüfungen. R4 ist standardmäßig blockiert.

### 3. Fehlerursachen-Agent
Wird bei Fehlern, Crashs, Datenproblemen oder R3/R4-Änderungen aktiviert. Trennt Symptom, Root Cause und Folgefehler. Liefert Reproduktionsbedingungen und den notwendigen dauerhaften Regressionstest.

### 4. Plan-Agent
Darf nur `TODO.md`, Iterationspläne und optionale Planberichte schreiben. Der Plan enthält Ziel, Nicht-Ziele, Risikoklasse, kleinste Änderung, Fehler-/Recoverypfade, Tests, Rollback und Fertig-Kriterium.

### 5. Regressions-Agent
Prüft read-only, welche bestehenden Funktionen indirekt betroffen sind, welche Tests bereits schützen und welche neuen Tests für Fehlerpfade, Neustart, Crash oder Recovery fehlen.

### 6. Plan-Prüfer
Prüft Scope, Planbezug, Testabdeckung, Dokumentationssynchronität, Self-Repair-Allowlist/Denylist und Rückfallfähigkeit. Ungeplante Nebenumbauten oder Sicherheitsabschwächungen blockieren.

### 7. Release-Prüfer
Bewertet den finalen Commit als Ganzes. Freigabe nur als `RELEASE READY`; kritische Hinweise zu Datenintegrität, Recovery, Sicherheit oder fehlgeschlagenen Tests können nicht als unverbindliche Warnung durchgewunken werden.

## Automatische CI-Entsprechung
`.github/workflows/agents.yml` führt die sieben deterministischen Gates seriell aus. `scripts/agent_gate.py` bestimmt Diff, Risikoklasse und Pflichtartefakte. `scripts/validate_agents.py` kontrolliert zusätzlich Rollenverträge, Manifest und Workflow-Verdrahtung.

## Triggerlogik
- `app/`: Analyse, Risiko, Plan, Regression, Compliance und Release.
- Persistenz/DB/Projektstruktur/Recovery/CI: mindestens R3 plus Fehlerursachen-Trigger.
- `.agents/`, `AGENTS.md`, Agentenworkflow oder Validatorskripte: Rollenvertragsprüfung zwingend.
- bestätigte Regression: Root Cause + dauerhafter Regressionstest.
- R4: keine automatische Freigabe.

## Grundregel
Ein Prüfagent darf einen blockierenden Befund nicht selbst durch Codeänderung „lösen“. Er liefert Evidenz und Prüfresultat; die Umsetzung bleibt getrennt. Dadurch ist später nachvollziehbar, ob der Plan eingehalten und ein Fehler wirklich behoben wurde.
