# Incident Escalation Policy

## Overview

The Escalation Engine evaluates active incidents against time and repeat-count criteria to promote severity levels along the escalation ladder:

```
P4 -> P3 -> P2 -> P1
```

## Notification Statuses

- `NOTIFICATION_READY`: External notification integration is configured and ready.
- `NOTIFICATION_SIMULATED`: Non-destructive simulated notification logged.
- `NOTIFICATION_NOT_CONFIGURED`: Default state when webhooks/pager integrations are unconfigured.
- `NOT_EXECUTED`: Production notification dispatch preserved as unexecuted.
