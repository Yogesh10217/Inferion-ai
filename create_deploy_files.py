import os

PROJECT_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"

# Deployment Directories
directories = [
    "deploy/kubernetes/base",
    "deploy/kubernetes/overlays/production",
    "deploy/helm/llm-engine/templates",
    "deploy/scripts/k6",
    "docs/operations"
]

for d in directories:
    os.makedirs(os.path.join(PROJECT_ROOT, d), exist_ok=True)

def write_file(path, content):
    with open(os.path.join(PROJECT_ROOT, path), "w") as f:
        f.write(content.strip() + "\n")

# Helm Chart
write_file("deploy/helm/llm-engine/Chart.yaml", """
apiVersion: v2
name: llm-engine
description: LLM Inference Engine API Gateway
type: application
version: 0.1.0
appVersion: "1.0.0"
""")

write_file("deploy/helm/llm-engine/values.yaml", """
replicaCount: 3
image:
  repository: ghcr.io/org/llm-engine
  tag: "latest"
  pullPolicy: IfNotPresent

scheduler:
  enabled: true
  replicaCount: 1

securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL

resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "2000m"
    memory: "2Gi"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: false
""")

write_file("deploy/helm/llm-engine/templates/gateway-deployment.yaml", """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-gateway
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
    spec:
      securityContext:
        {{- toYaml .Values.securityContext | nindent 8 }}
      containers:
        - name: gateway
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
""")

# K6 scripts
write_file("deploy/scripts/k6/smoke.js", """
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 1,
  duration: '10s',
};

export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, { 'status was 200': (r) => r.status == 200 });
}
""")

# Operational Runbooks
write_file("docs/operations/RUNBOOK.md", """
# Operational Runbooks
- Gateway Failures
- Provider Outages
- Scheduler Issues
- Plugin Failures
- Routing Degradation
- Recovery Procedures
""")

write_file("docs/operations/DISASTER_RECOVERY.md", """
# Disaster Recovery
- Backup Procedures
- Restoration Procedures
- Secret Rotation
""")

write_file("docs/operations/SECURITY_HARDENING.md", """
# Security Hardening
- Non-root containers
- Seccomp profiles
- Network Policies
""")

print("Deployment files created.")
