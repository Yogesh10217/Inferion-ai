# Security Hardening Guide

## Container Hardening
- **Non-Root Execution**: Container configured with `runAsNonRoot: true`, UID 1000.
- **Read-Only Root Filesystem**: Mounted with `readOnlyRootFilesystem: true`.
- **Capability Drops**: All Linux capabilities dropped (`capabilities.drop: ["ALL"]`).
- **Seccomp Profile**: Configured with `RuntimeDefault`.

## Network Isolation
- **NetworkPolicies**: Strict ingress rules limiting traffic to TCP port 8000.
