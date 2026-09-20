# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of the LLM Inference Engine seriously. If you discover a security vulnerability within this project, please follow these guidelines:

1. **Do NOT open a public GitHub issue** for security vulnerabilities.
2. Email your findings directly to the security team or maintainer.
3. Include detailed steps to reproduce the issue, proof of concept (PoC), and potential impact.

### Security Best Practices

When deploying this engine in production:
- **JWT Secret**: Always set `JWT_SECRET` to a cryptographically strong random string of at least 32 characters.
- **CORS Policy**: Ensure `CORS_ORIGINS` explicitly lists allowed origin URLs. Wildcards (`*`), empty values, and unencrypted HTTP (except localhost) are rejected by default in production.
- **Database SSL**: Set `DB_SSL_VERIFY=true` to enforce strict SSL certificate verification for database connections.
- **Rate Limiting**: Keep `RATE_LIMITING_ENABLED=true` to protect endpoints against brute force and denial of service.
