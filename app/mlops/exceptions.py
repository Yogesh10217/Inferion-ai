"""MLOps & AI Asset Domain Exceptions Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class MLOpsException(AppException):
    """Base exception for all MLOps domain errors."""

    def __init__(
        self, message: str, code: str = "MLOPS_ERROR", status_code: int = 400, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class AssetNotFoundException(MLOpsException):
    def __init__(self, asset_id: str) -> None:
        super().__init__(message=f"AI Asset '{asset_id}' not found", code="ASSET_NOT_FOUND", status_code=404)


class VersionNotFoundException(MLOpsException):
    def __init__(self, asset_id: str, version: str) -> None:
        super().__init__(
            message=f"Version '{version}' for asset '{asset_id}' not found", code="VERSION_NOT_FOUND", status_code=404
        )


class DeploymentNotFoundException(MLOpsException):
    def __init__(self, deployment_id: str) -> None:
        super().__init__(
            message=f"Deployment '{deployment_id}' not found", code="DEPLOYMENT_NOT_FOUND", status_code=404
        )


class ReleaseNotFoundException(MLOpsException):
    def __init__(self, release_id: str) -> None:
        super().__init__(message=f"Release '{release_id}' not found", code="RELEASE_NOT_FOUND", status_code=404)


class EvaluationFailedException(MLOpsException):
    def __init__(self, eval_id: str, reason: str) -> None:
        super().__init__(message=f"Evaluation '{eval_id}' failed: {reason}", code="EVALUATION_FAILED", status_code=422)


class GovernanceViolationException(MLOpsException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="GOVERNANCE_VIOLATION", status_code=403)


class RollbackFailedException(MLOpsException):
    def __init__(self, deployment_id: str, reason: str) -> None:
        super().__init__(
            message=f"Rollback failed for deployment '{deployment_id}': {reason}",
            code="ROLLBACK_FAILED",
            status_code=500,
        )


class DriftDetectedException(MLOpsException):
    def __init__(self, deployment_id: str, drift_type: str, severity: str) -> None:
        super().__init__(
            message=f"Critical drift '{drift_type}' ({severity}) detected on deployment '{deployment_id}'",
            code="DRIFT_DETECTED",
            status_code=422,
        )
