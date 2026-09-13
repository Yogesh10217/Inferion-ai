# Disaster Recovery Execution Runbook

## Overview
Defines disaster recovery plan structure, validation workflows, and safety controls.

## Safety Rule & Auto Execution Blocking
All destructive DR actions default to `auto_execution_blocked = True`.
Actions such as database restores, regional failover, infrastructure replacements, and secret rotations require manual approval unless an explicitly approved real production target is attached.

## Recovery Execution Lifecycle States
1. `NOT_STARTED`
2. `PRECHECKING`
3. `PLAN_VALIDATING`
4. `BACKUP_VALIDATING`
5. `RESTORE_PREPARING`
6. `RECOVERY_SIMULATING`
7. `RECOVERY_VALIDATING`
8. `RECOVERY_READY`
9. `MANUAL_EXECUTION_REQUIRED`
10. `COMPLETED`
11. `FAILED`
12. `BLOCKED`
13. `NOT_EXECUTED`

## Truthfulness Boundary
Unless a real production target is configured and empirically executed against, the status `PRODUCTION_DISASTER_RECOVERY_EXECUTED` remains strictly `NOT_EXECUTED`.
