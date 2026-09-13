# Resilience Testing Guide

## Overview
Provides guidelines for running automated resilience tests across SIMULATION, CONTAINER, INFRASTRUCTURE, and PRODUCTION targets.

## Execution Requirements
- **SIMULATION**: Default mode. Executed safely without real infrastructure.
- **CONTAINER**: Requires Docker engine active.
- **INFRASTRUCTURE**: Requires staging environment credentials.
- **PRODUCTION**: Requires explicit production target configuration and operator sign-off.
