# Secret Security Policy — Phase 5.69

## Overview
Mandates secret handling, canary value detection, and zero-exposure rules across all system logs, artifacts, and API responses.

## Canary Protection Rules
- The canonical `SecretsSanitizer` in `app/deployment/secrets.py` manages secret redacting.
- Canary values (e.g. `super_secret_test_value`, `AKIAIOSFODNN7EXAMPLE`, `dGVzdF9zZWNyZXRfa2V5`) MUST be sanitized to `[REDACTED]` or `[CANARY_VALUE_REDACTED]`.
- Hardcoded secrets in environment variables or code trigger an immediate `CRITICAL` secret security finding and posture penalty.
