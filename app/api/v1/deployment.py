from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from app.deployment.configuration_fingerprint import ConfigurationFingerprintEngine
from app.deployment.manager import DeploymentPlatformManager
from app.deployment.models import StartupState

router = APIRouter(tags=["Deployment Platform"])


def get_deployment_manager(request: Request) -> DeploymentPlatformManager:
    container = getattr(request.app.state, "container", None)
    if not hasattr(request.app.state, "deployment_manager"):
        manager = DeploymentPlatformManager(container=container)
        try:
            manager.startup()
        except Exception:  # nosec B110
            pass
        request.app.state.deployment_manager = manager
    elif request.app.state.deployment_manager.startup_manager.state == StartupState.INITIALIZED:
        try:
            request.app.state.deployment_manager.startup()
        except Exception:  # nosec B110
            pass
    return request.app.state.deployment_manager


@router.get("/health")
@router.get("/v1/deployment/health")
async def health_check(
    manager: DeploymentPlatformManager = Depends(get_deployment_manager),
) -> Dict[str, Any]:
    report = manager.check_health()
    return {
        "status": report.status.value,
        "environment": report.environment,
        "version": report.version,
        "checks": [
            {
                "category": c.category.value,
                "name": c.name,
                "status": c.status.value,
                "details": c.details,
            }
            for c in report.checks
        ],
    }


@router.get("/ready")
@router.get("/v1/deployment/ready")
async def readiness_check(
    manager: DeploymentPlatformManager = Depends(get_deployment_manager),
) -> Dict[str, Any]:
    res = manager.check_readiness()
    if not res.get("ready", False):
        raise HTTPException(status_code=503, detail=res)
    return res


@router.get("/live")
@router.get("/v1/deployment/live")
async def liveness_check(
    manager: DeploymentPlatformManager = Depends(get_deployment_manager),
) -> Dict[str, Any]:
    return manager.check_liveness()


@router.get("/v1/deployment/status")
async def deployment_status(
    manager: DeploymentPlatformManager = Depends(get_deployment_manager),
) -> Dict[str, Any]:
    release_res = manager.validate_release()
    config = manager.get_config()
    return {
        "environment": config.environment.value,
        "application_name": config.application_name,
        "application_version": config.application_version,
        "deployment_version": config.deployment_version,
        "release_status": release_res.status.value,
        "readiness_classification": release_res.readiness_classification.value,
        "passed_checks": release_res.passed_checks,
        "failed_checks": release_res.failed_checks,
        "blocking_reasons": release_res.blocking_reasons,
    }


@router.get("/v1/deployment/diagnostics")
async def deployment_diagnostics(
    manager: DeploymentPlatformManager = Depends(get_deployment_manager),
) -> Dict[str, Any]:
    diag = manager.get_diagnostics()
    return {
        "application_name": diag.application_name,
        "application_version": diag.application_version,
        "deployment_version": diag.deployment_version,
        "environment": diag.environment,
        "startup_state": diag.startup_state.value,
        "uptime_seconds": diag.uptime_seconds,
        "registered_managers": diag.registered_managers,
        "configuration_valid": diag.configuration_valid,
        "observability_active": diag.observability_active,
        "readiness_classification": diag.readiness_classification.value,
        "dependency_health": [
            {
                "category": d.category.name,
                "name": d.name,
                "status": d.status.value,
                "required": d.required,
                "latency_ms": d.latency_ms,
            }
            for d in diag.dependency_health
        ],
    }


@router.get("/v1/deployment/configuration")
async def sanitized_configuration(
    manager: DeploymentPlatformManager = Depends(get_deployment_manager),
) -> Dict[str, Any]:
    config = manager.get_config()
    fp = ConfigurationFingerprintEngine.generate_fingerprint(config)

    # Return sanitized configuration representation only
    return {
        "environment": config.environment.value,
        "application_name": config.application_name,
        "application_version": config.application_version,
        "deployment_version": config.deployment_version,
        "region": config.region,
        "debug_enabled": config.debug_enabled,
        "cache_enabled": config.cache_enabled,
        "messaging_enabled": config.messaging_enabled,
        "observability_enabled": config.observability_enabled,
        "log_level": config.log_level,
        "configuration_fingerprint": fp.fingerprint_hash,
    }
