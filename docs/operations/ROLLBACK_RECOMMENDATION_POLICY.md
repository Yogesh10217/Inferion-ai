# Rollback Recommendation Policy

## Critical Safety Rule

> [!CAUTION]
> A recommendation is **NEVER** an automatic execution.

For example, `ROLLBACK_RECOMMENDED` must **NOT** automatically alter live production containers, databases, DNS, or infrastructure. All remediation requires explicit human operator authorization.
