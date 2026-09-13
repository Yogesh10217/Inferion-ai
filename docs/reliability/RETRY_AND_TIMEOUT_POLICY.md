# Retry and Timeout Policy

## Overview
Governs bounded retry attempts (`FIXED_DELAY`, `EXPONENTIAL_BACKOFF`) and component timeout limits.

## Infinite Retry Loop Protection
Retries strictly enforce `max_attempts` (default 3). Infinite loops are prevented by deterministic iteration bounds and max delay caps.
