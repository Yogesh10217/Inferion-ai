# Alert Management Policy

## Overview

The Alert Management framework ensures actionable, high-precision alerts while suppressing alert fatigue.

## Severity Levels

- `INFO`: Informational event (no operator action required).
- `WARNING`: Early degradation signal or SLO at risk.
- `CRITICAL`: Active SLO breach or major component failure.
- `EMERGENCY`: Platform outage or total error budget exhaustion.

## Alert Deduplication Policy

Alerts are deduplicated deterministically by `AlertDeduplicationEngine` using SHA-256 fingerprints.

Fingerprint components:
- `alert_type`
- `service`
- `severity`
- `deployment_identity`
- `normalized_summary`

> [!NOTE]
> Volatile fields such as timestamps are strictly excluded from the deduplication hash so that 100 identical errors collapse into 1 canonical alert with `occurrence_count = 100`.
