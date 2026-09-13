# Business Continuity Plan

## Overview
Establishes critical service prioritization, minimum capability thresholds (default 80%), recovery ordering, and operational fallbacks.

## Service Criticality Tiers
- **CRITICAL**: Tier 1 services (Core API, Authentication, Database). Max downtime: 5 minutes.
- **HIGH**: Tier 2 services (Model Router, Caching, EventBus). Max downtime: 15 minutes.
- **MEDIUM**: Tier 3 services (Metrics, Logging, Analytics). Max downtime: 60 minutes.
- **LOW**: Tier 4 services (Non-critical reporting, background tasks). Max downtime: 24 hours.

## Classifications
- `CONTINUITY_READY`
- `CONTINUITY_WARNING`
- `CONTINUITY_AT_RISK`
- `CONTINUITY_BLOCKED`
- `NOT_EXECUTED`
