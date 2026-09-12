# Entwicklerdokumentation

## Projektphase

Das Repository befindet sich im neu aufgesetzten FOUNDATION-Zustand.

## Geplante Hauptebenen

```text
app/
├── bootstrap/
├── core/
├── services/
├── modules/
├── jobs/
├── ui/
└── diagnostics/
```

## Geplante Kernbausteine

- Startup Controller
- Application State
- Event Bus
- Command Bus
- Project Service
- Database Service
- Settings Service
- Logging Service
- Recovery Service
- Health Service
- Job Manager / Watchdog

## Entwicklungsprinzip

Neue Verzeichnisse und Module werden erst angelegt, wenn ihre Implementierung tatsächlich beginnt. Leere Architekturattrappen werden vermieden.
