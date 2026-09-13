# Container Security Policy — Phase 5.69

## Overview
Defines security constraints for containerized runtimes operating within the Enterprise AI Platform.

## Core Rules
1. **Non-Root Execution**: Containers must execute as non-root user (UID != 0).
2. **Read-Only Root Filesystem**: Root filesystem must be read-only (`read_only_root_fs = True`).
3. **Privilege Escalation**: `allow_privilege_escalation = False`.
4. **Port Restrictions**: Privileged ports (< 1024) are prohibited unless explicitly proxied.
5. **Image Digest Binding**: All production images must be referenced via immutable SHA-256 digests (`sha256:...`).
