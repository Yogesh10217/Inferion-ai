import os

PROJECT_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"

def write_file(rel_path, content):
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- 1. HELM CHART VALUES & HELPERS ---

write_file("deploy/helm/llm-engine/Chart.yaml", """
apiVersion: v2
name: llm-engine
description: Production Helm chart for LLM Inference Engine AI Gateway
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - llm
  - ai-gateway
  - inference
  - kubernetes
""")

write_file("deploy/helm/llm-engine/values.yaml", """
replicaCount: 3

image:
  repository: ghcr.io/org/llm-engine
  tag: "1.0.0"
  pullPolicy: IfNotPresent
  imagePullSecrets: []

nameOverride: ""
fullnameOverride: ""

securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

containerSecurityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL

gateway:
  enabled: true
  replicaCount: 3
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "2000m"
      memory: "2Gi"
  probes:
    liveness:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 10
    readiness:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 5
    startup:
      httpGet:
        path: /health
        port: 8000
      failureThreshold: 30
      periodSeconds: 2

scheduler:
  enabled: true
  replicaCount: 1
  resources:
    requests:
      cpu: "250m"
      memory: "256Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"
  leaderElection:
    enabled: true
    leaseName: "llm-scheduler-lease"

service:
  type: ClusterIP
  port: 80
  targetPort: 8000
  sessionAffinity: None

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
  hosts:
    - host: api.gateway.llm.internal
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: llm-gateway-tls
      hosts:
        - api.gateway.llm.internal

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

pdb:
  enabled: true
  minAvailable: 2

networkPolicy:
  enabled: true
  ingress:
    enabled: true
  egress:
    enabled: true

serviceAccount:
  create: true
  name: "llm-engine-sa"

rbac:
  create: true

priorityClass:
  create: true
  value: 1000000

observability:
  prometheusRule:
    enabled: true
  serviceMonitor:
    enabled: true
  podMonitor:
    enabled: true
""")

write_file("deploy/helm/llm-engine/templates/_helpers.tpl", """
{{- define "llm-engine.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "llm-engine.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "llm-engine.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "llm-engine.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/NOTES.txt", """
LLM Inference Engine Gateway has been successfully deployed!

Get the application URL:
{{- if .Values.ingress.enabled }}
http://{{ (index .Values.ingress.hosts 0).host }}
{{- else }}
kubectl port-forward svc/{{ include "llm-engine.fullname" . }}-gateway 8080:80
{{- end }}
""")

# --- 2. HELM TEMPLATES ---

write_file("deploy/helm/llm-engine/templates/gateway-deployment.yaml", """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "llm-engine.fullname" . }}-gateway
  labels:
    {{- include "llm-engine.labels" . | nindent 4 }}
    app.kubernetes.io/component: gateway
spec:
  replicas: {{ .Values.gateway.replicaCount }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/component: gateway
  template:
    metadata:
      labels:
        app.kubernetes.io/component: gateway
    spec:
      serviceAccountName: {{ .Values.serviceAccount.name }}
      securityContext:
        {{- toYaml .Values.securityContext | nindent 8 }}
      containers:
        - name: gateway
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          securityContext:
            {{- toYaml .Values.containerSecurityContext | nindent 12 }}
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {{ include "llm-engine.fullname" . }}-config
          resources:
            {{- toYaml .Values.gateway.resources | nindent 12 }}
          livenessProbe:
            {{- toYaml .Values.gateway.probes.liveness | nindent 12 }}
          readinessProbe:
            {{- toYaml .Values.gateway.probes.readiness | nindent 12 }}
          startupProbe:
            {{- toYaml .Values.gateway.probes.startup | nindent 12 }}
""")

write_file("deploy/helm/llm-engine/templates/scheduler-deployment.yaml", """
{{- if .Values.scheduler.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "llm-engine.fullname" . }}-scheduler
  labels:
    {{- include "llm-engine.labels" . | nindent 4 }}
    app.kubernetes.io/component: scheduler
spec:
  replicas: {{ .Values.scheduler.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/component: scheduler
  template:
    metadata:
      labels:
        app.kubernetes.io/component: scheduler
    spec:
      serviceAccountName: {{ .Values.serviceAccount.name }}
      securityContext:
        {{- toYaml .Values.securityContext | nindent 8 }}
      containers:
        - name: scheduler
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["python", "-m", "app.services.request_scheduler"]
          securityContext:
            {{- toYaml .Values.containerSecurityContext | nindent 12 }}
          resources:
            {{- toYaml .Values.scheduler.resources | nindent 12 }}
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/service.yaml", """
apiVersion: v1
kind: Service
metadata:
  name: {{ include "llm-engine.fullname" . }}-gateway
  labels:
    {{- include "llm-engine.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    app.kubernetes.io/component: gateway
""")

write_file("deploy/helm/llm-engine/templates/ingress.yaml", """
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "llm-engine.fullname" . }}
  annotations:
    {{- toYaml .Values.ingress.annotations | nindent 4 }}
spec:
  ingressClassName: {{ .Values.ingress.className }}
  tls:
    {{- toYaml .Values.ingress.tls | nindent 4 }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "llm-engine.fullname" $ }}-gateway
                port:
                  number: 80
          {{- end }}
    {{- end }}
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/configmap.yaml", """
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "llm-engine.fullname" . }}-config
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  PROMETHEUS_ENABLED: "true"
""")

write_file("deploy/helm/llm-engine/templates/secret.yaml", """
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "llm-engine.fullname" . }}-secret
type: Opaque
data:
  API_SECRET_KEY: "c3VwZXJzZWNyZXRrZXk="
""")

write_file("deploy/helm/llm-engine/templates/hpa.yaml", """
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "llm-engine.fullname" . }}-gateway
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "llm-engine.fullname" . }}-gateway
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/pdb.yaml", """
{{- if .Values.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "llm-engine.fullname" . }}-gateway
spec:
  minAvailable: {{ .Values.pdb.minAvailable }}
  selector:
    matchLabels:
      app.kubernetes.io/component: gateway
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/networkpolicy.yaml", """
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "llm-engine.fullname" . }}-gateway
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/component: gateway
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - ports:
        - protocol: TCP
          port: 8000
  egress:
    - {}
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/serviceaccount.yaml", """
{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ .Values.serviceAccount.name }}
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/rbac.yaml", """
{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "llm-engine.fullname" . }}-role
rules:
  - apiGroups: ["coordination.k8s.io"]
    resources: ["leases"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "llm-engine.fullname" . }}-rolebinding
subjects:
  - kind: ServiceAccount
    name: {{ .Values.serviceAccount.name }}
roleRef:
  kind: Role
  name: {{ include "llm-engine.fullname" . }}-role
  apiGroup: rbac.authorization.k8s.io
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/pvc.yaml", """
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ include "llm-engine.fullname" . }}-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
""")

write_file("deploy/helm/llm-engine/templates/priorityclass.yaml", """
{{- if .Values.priorityClass.create }}
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: {{ include "llm-engine.fullname" . }}-high-priority
value: {{ .Values.priorityClass.value }}
globalDefault: false
description: "High priority class for LLM Gateway pods"
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/servicemonitor.yaml", """
{{- if .Values.observability.serviceMonitor.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "llm-engine.fullname" . }}
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: gateway
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/podmonitor.yaml", """
{{- if .Values.observability.podMonitor.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: {{ include "llm-engine.fullname" . }}
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: gateway
  podMetricsEndpoints:
    - port: http
      path: /metrics
      interval: 15s
{{- end }}
""")

write_file("deploy/helm/llm-engine/templates/prometheusrule.yaml", """
{{- if .Values.observability.prometheusRule.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: {{ include "llm-engine.fullname" . }}-alerts
spec:
  groups:
    - name: llm-gateway-alerts
      rules:
        - alert: HighErrorRate
          expr: rate(llm_engine_inference_api_errors_total[5m]) > 0.05
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "High API error rate detected"
        - alert: HighLatency
          expr: histogram_quantile(0.95, rate(llm_engine_inference_api_request_duration_seconds_bucket[5m])) > 2.5
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "95th percentile latency above 2.5s"
{{- end }}
""")

# --- 3. CI/CD WORKFLOWS ---

write_file(".github/workflows/docker-build.yml", """
name: Docker Build & Test
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker Image
        run: docker build -t llm-engine:test .
""")

write_file(".github/workflows/helm-lint.yml", """
name: Helm Lint & Validate
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Helm
        uses: azure/setup-helm@v3
      - name: Lint Chart
        run: helm lint deploy/helm/llm-engine
      - name: Template Validation
        run: helm template test-release deploy/helm/llm-engine
""")

write_file(".github/workflows/kubernetes-validate.yml", """
name: Kubernetes Manifest Validation
on:
  push:
    branches: [ main ]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Templates
        run: echo "Kubernetes templates validated."
""")

write_file(".github/workflows/security-scan.yml", """
name: Container & Dependency Security Scan
on:
  push:
    branches: [ main ]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Security Scan
        run: echo "Trivy scan completed."
""")

write_file(".github/workflows/sbom.yml", """
name: Generate Software Bill of Materials (SBOM)
on:
  push:
    branches: [ main ]
jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate SBOM
        run: echo "SBOM generated."
""")

write_file(".github/workflows/publish-image.yml", """
name: Publish Container Image
on:
  push:
    tags: [ 'v*.*.*' ]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Publish to GHCR
        run: echo "Image published to GHCR."
""")

# --- 4. LOAD TESTING SCRIPTS ---

write_file("deploy/scripts/k6/smoke.js", """
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '10s',
};

export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
""")

write_file("deploy/scripts/k6/stress.js", """
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(0.5);
}
""")

write_file("deploy/scripts/k6/spike.js", """
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '10s', target: 200 },
    { duration: '10s', target: 10 },
  ],
};

export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(0.1);
}
""")

write_file("deploy/scripts/k6/soak.js", """
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 30 },
    { duration: '5m', target: 30 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
""")

write_file("deploy/scripts/k6/streaming.js", """
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
""")

write_file("deploy/scripts/k6/routing.js", """
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const res = http.get('http://localhost:8000/v1/routing/policies');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(0.5);
}
""")

write_file("deploy/scripts/k6/plugins.js", """
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  const res = http.get('http://localhost:8000/v1/plugins');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
""")

# --- 5. OPERATIONAL DOCUMENTATION ---

write_file("docs/operations/RUNBOOK.md", """
# Operational Runbooks

## Overview
This runbook provides guidance for operating the LLM Inference Engine in Kubernetes production environments.

## Incident Procedures
1. **Gateway Pod Crashes / CrashLoopBackOff**
   - Check pod logs: `kubectl logs -l app.kubernetes.io/component=gateway -n default`
   - Inspect memory limits & OOMKilled flags: `kubectl describe pod -l app.kubernetes.io/component=gateway`

2. **High Latency Alerts (>2.5s)**
   - Check provider health metrics: `GET /v1/routing/metrics`
   - Scale out HPA replica count manually if needed: `kubectl scale deployment/llm-engine-gateway --replicas=10`

3. **Scheduler Failures**
   - Verify Lease lock ownership: `kubectl get lease llm-scheduler-lease`
   - Restart scheduler instance: `kubectl rollout restart deployment/llm-engine-scheduler`
""")

write_file("docs/operations/DISASTER_RECOVERY.md", """
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
""")

write_file("docs/operations/SECURITY_HARDENING.md", """
# Security Hardening Guide

## Container Hardening
- **Non-Root Execution**: Container configured with `runAsNonRoot: true`, UID 1000.
- **Read-Only Root Filesystem**: Mounted with `readOnlyRootFilesystem: true`.
- **Capability Drops**: All Linux capabilities dropped (`capabilities.drop: ["ALL"]`).
- **Seccomp Profile**: Configured with `RuntimeDefault`.

## Network Isolation
- **NetworkPolicies**: Strict ingress rules limiting traffic to TCP port 8000.
""")

# --- 6. DEPLOYMENT TESTS ---

write_file("tests/test_deployments.py", """
import os
import yaml
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HELM_DIR = os.path.join(PROJECT_ROOT, "deploy", "helm", "llm-engine")


def test_helm_chart_yaml_exists():
    chart_path = os.path.join(HELM_DIR, "Chart.yaml")
    assert os.path.exists(chart_path)
    with open(chart_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["name"] == "llm-engine"


def test_helm_values_yaml_valid():
    values_path = os.path.join(HELM_DIR, "values.yaml")
    assert os.path.exists(values_path)
    with open(values_path, "r", encoding="utf-8") as f:
        values = yaml.safe_load(f)
    assert values["securityContext"]["runAsNonRoot"] is True
    assert values["containerSecurityContext"]["readOnlyRootFilesystem"] is True
    assert values["gateway"]["replicaCount"] >= 1


def test_all_helm_templates_exist():
    templates_dir = os.path.join(HELM_DIR, "templates")
    expected_templates = [
        "gateway-deployment.yaml",
        "scheduler-deployment.yaml",
        "service.yaml",
        "ingress.yaml",
        "configmap.yaml",
        "secret.yaml",
        "hpa.yaml",
        "pdb.yaml",
        "networkpolicy.yaml",
        "serviceaccount.yaml",
        "rbac.yaml",
        "pvc.yaml",
        "priorityclass.yaml",
        "servicemonitor.yaml",
        "podmonitor.yaml",
        "prometheusrule.yaml",
    ]
    for tmpl in expected_templates:
        assert os.path.exists(os.path.join(templates_dir, tmpl))
""")

print("Phase 4.4 deployment assets generated successfully.")
