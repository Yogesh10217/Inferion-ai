# Failover and Failback Runbook

## Overview
Guides failover evaluation for Primary, Database, Region, Service, and Dependency failures.

## Safety Invariant
Failover execution defaults to `auto_execution_blocked = True`. Recommendations are provided to SRE operators, but live traffic or regional routing changes are never performed automatically by the framework.

## States
- `NOT_REQUIRED`
- `READY`
- `RECOMMENDED`
- `MANUAL_EXECUTION_REQUIRED`
- `EXECUTED`
- `VALIDATED`
- `BLOCKED`
- `NOT_EXECUTED`
