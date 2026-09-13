# Deployment Health Monitoring

## Overview

The `DeploymentHealthCorrelator` binds candidate deployment metadata from Phase 5.66 and 5.67 (Deployment Identity, Artifact Digest, Release Candidate ID, Traffic %) with post-deployment operational telemetry.

## Scoring Model

The Deployment Health Score is evaluated on a 0–100 scale:
- Deductions apply for breached SLOs (-30), warning SLOs (-10), exhausted error budget (-40), and active incidents (-25).
- Score >= 70 with 0 breached SLOs and 0 active incidents = `IS_HEALTHY = True`.
