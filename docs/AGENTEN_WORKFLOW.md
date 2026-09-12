# Triggerbasierte Subagenten

Die Subagenten sind absichtlich getrennt, damit Analyse, Planung und Prüfung nicht unbemerkt zu Implementierung werden.

## Triggerkette
`Änderung erkannt → Analyse → Plan/TODO → Umsetzung → Plan-Prüfung → Release-Gate`

### Analyse
Trigger bei Änderungen an Code, Tests, Workflows, Manifest oder bei bestätigten Fehlern. Liefert Risiko- und Abhängigkeitsbild.

### Planung
Trigger bei Handlungsbedarf. Darf ausschließlich Todo/Plan dokumentieren. Ziel ist die kleinste robuste Lösung und die Reduktion unnötiger Komplexität.

### Plan-Prüfung
Trigger nach Umsetzung und vor Freigabe. Prüft Planabweichungen, fehlende Tests, Dokumentationsdrift und neue Risiken.

## Automatische CI-Entsprechung
`.github/workflows/agents.yml` führt deterministische Prüfungen aus. Sie ersetzen keine semantische Analyse durch ein Sprachmodell, sichern aber harte Regeln automatisch ab: Codeänderung braucht Planbezug; Codeänderung braucht Tests; Status und Changelog müssen synchron bleiben.
