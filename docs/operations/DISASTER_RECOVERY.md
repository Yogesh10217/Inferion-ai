# Disaster Recovery Guide

## Backup Procedures
1. **Database & Config Snapshots**
   - Export active routing policies via REST: `GET /v1/routing/policies`
   - Export plugin registry state: `plugins_registry.json`

2. **Secret & Cert Backup**
   - Backup TLS secrets: `kubectl get secret llm-gateway-tls -o yaml > cert_backup.yaml`

## Recovery Procedures
1. **Cluster Recovery**
   - Re-apply Helm chart: `helm install llm-engine deploy/helm/llm-engine`
   - Restore secret payloads and config maps.
