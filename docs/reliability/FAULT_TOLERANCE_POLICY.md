# Fault Tolerance Policy

## Overview
Governs controlled fault scenario evaluation across 10 failure types:
1. `DEPENDENCY_FAILURE`
2. `DATABASE_FAILURE`
3. `CACHE_FAILURE`
4. `EVENTBUS_FAILURE`
5. `AUTH_FAILURE`
6. `SECRET_PROVIDER_FAILURE`
7. `NETWORK_FAILURE`
8. `CONTAINER_FAILURE`
9. `APPLICATION_FAILURE`
10. `OBSERVABILITY_FAILURE`

## Safety Control
Fault testing defaults strictly to simulation mode (`is_simulation = True`).
Live destructive fault injection is blocked unless explicit override flags and targets are supplied.
