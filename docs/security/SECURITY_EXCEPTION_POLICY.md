# Security Exception Policy — Phase 5.69

## Overview
Governs temporary exceptions for security policy violations and vulnerabilities.

## Mandatory Controls
1. **Time-To-Live (TTL)**: Every exception must have a strict expiration timestamp (`expires_at`).
2. **Justification & Owner**: Mandatory business justification and accountable owner.
3. **Automatic Expiration**: Expired exceptions automatically revert to `is_active = False` during evaluation.
4. **No Critical Production Exceptions**: CRITICAL vulnerabilities in production environments cannot be excepted without CISO/manual review override.
