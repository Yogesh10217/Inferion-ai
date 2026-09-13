# Circuit Breaker Policy

## Overview
Governs CircuitBreaker state transitions: `CLOSED` → `OPEN` → `HALF_OPEN` → `CLOSED`.

## Rules
- **Failure Threshold**: Default 5 consecutive failures opens the circuit.
- **Recovery Timeout**: Default 30 seconds before probing in `HALF_OPEN` state.
- **Single Probe Success**: A single successful call in `HALF_OPEN` resets state to `CLOSED`.
