# PRODUCTION SMOKE TEST PLAN

**Target System:** Enterprise AI Platform  
**Target Safety Rule:** Smoke tests must target designated staging/simulation environments by default. Auto-targeting live production endpoints is strictly forbidden (`PRODUCTION_SMOKE_TEST_NOT_EXECUTED`).

---

## 1. TEST MATRIX

| Test ID | Endpoint | Method | Expected Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| `ST-01` | `/live` | GET | 200 OK | Confirm process liveness probe |
| `ST-02` | `/ready` | GET | 200 OK | Confirm readiness of dependencies & managers |
| `ST-03` | `/health` | GET | 200 OK | Full system health report |
| `ST-04` | `/health` | GET | Headers | HSTS, X-Frame-Options, CSP, NoSniff security headers |
| `ST-05` | `/docs` | GET | 404 Not Found | Disable OpenAPI Swagger UI in production |
| `ST-06` | `/redoc` | GET | 404 Not Found | Disable ReDoc UI in production |
| `ST-07` | `/openapi.json` | GET | 404 Not Found | Disable raw OpenAPI spec download in production |
| `ST-08` | `/health` | GET | JSON Payload | Verify registered_count = 9 for Intelligence Managers |
