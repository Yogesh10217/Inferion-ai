# API Security Policy — Phase 5.69

## Overview
Defines mandatory HTTP security headers, CORS policies, authentication requirements, and interactive documentation exposure rules for all platform API endpoints.

## Mandatory Header Invariants
- `Strict-Transport-Security` (HSTS): `max-age=31536000; includeSubDomains`
- `Content-Security-Policy` (CSP): Strict default-src policy
- `X-Frame-Options`: `DENY` or `SAMEORIGIN`
- `X-Content-Type-Options`: `nosniff`
- `Referrer-Policy`: `strict-origin-when-cross-origin`

## Documentation Protection
- Interactive API Swagger/OpenAPI documentation (`/docs`, `/redoc`) MUST be disabled or protected with strict RBAC in production environments (`is_production=True`).
