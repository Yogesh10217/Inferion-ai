# SLO & Error Budget Policy

## Overview

Service Level Objectives (SLOs) define target operational standards. Error Budgets represent the acceptable margin of unreliability over an evaluation window.

## Canonical Targets

- **Availability**: >= 99.9%
- **Error Rate**: <= 1.0%
- **Latency (p95)**: <= 500ms
- **Probe Health**: 100% healthy

## Error Budget Equation

$$\text{Remaining Budget} = \max(0.0, \text{Total Budget} - \text{Consumed Budget})$$

Negative error budgets are strictly forbidden. When consumption reaches 100%, the Error Budget status transitions to `EXHAUSTED`.
