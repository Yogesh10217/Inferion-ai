# Recovery Audit Policy

## Overview
Governs evidence collection, secret sanitization, SHA-256 fingerprinting, and audit log tamper detection.

## Secret Sanitization
All raw evidence payloads are processed through `SecretsSanitizer`. Secrets such as `password123`, `canary_secret`, `admin123`, and `super_secret_test_value` are redacted before fingerprinting.

## Audit Validation
Any fingerprint mismatch or timestamp ordering anomaly immediately fails audit validation and blocks reliability certification.
