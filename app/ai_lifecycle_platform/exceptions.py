"""Domain Exceptions for Enterprise AI Lifecycle Platform (Phase 5.33)."""


class AILifecycleException(Exception):
    """Base exception for all AI Lifecycle Platform errors."""


class CrossTenantLifecycleAccessException(AILifecycleException):
    """Raised when an operation attempts to access resources belonging to another tenant."""

    def __init__(self, tenant_id: str, target_tenant_id: str) -> None:
        super().__init__(f"Tenant '{tenant_id}' unauthorized to access lifecycle resource of tenant '{target_tenant_id}'.")
        self.tenant_id = tenant_id
        self.target_tenant_id = target_tenant_id


class AIAssetNotFoundException(AILifecycleException):
    """Raised when a requested AI asset is not found."""

    def __init__(self, asset_id: str) -> None:
        super().__init__(f"AI asset '{asset_id}' not found.")
        self.asset_id = asset_id


class DatasetNotFoundException(AILifecycleException):
    """Raised when a dataset is not found."""

    def __init__(self, dataset_id: str) -> None:
        super().__init__(f"Dataset '{dataset_id}' not found.")
        self.dataset_id = dataset_id


class ModelNotFoundException(AILifecycleException):
    """Raised when a model is not found."""

    def __init__(self, model_id: str) -> None:
        super().__init__(f"Model '{model_id}' not found.")
        self.model_id = model_id


class AgentNotFoundException(AILifecycleException):
    """Raised when an agent is not found."""

    def __init__(self, agent_id: str) -> None:
        super().__init__(f"Agent '{agent_id}' not found.")
        self.agent_id = agent_id


class EvaluationNotFoundException(AILifecycleException):
    """Raised when an evaluation run or suite is not found."""

    def __init__(self, eval_id: str) -> None:
        super().__init__(f"Evaluation '{eval_id}' not found.")
        self.eval_id = eval_id


class InvalidLifecycleTransitionException(AILifecycleException):
    """Raised when an invalid lifecycle state transition is requested."""

    def __init__(self, current_state: str, target_state: str) -> None:
        super().__init__(f"Invalid lifecycle transition from '{current_state}' to '{target_state}'.")
        self.current_state = current_state
        self.target_state = target_state


class ImmutableLifecycleRecordException(AILifecycleException):
    """Raised when attempting to modify a finalized, immutable lifecycle record."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Lifecycle record '{record_id}' is finalized and immutable.")
        self.record_id = record_id


class InvalidPromotionException(AILifecycleException):
    """Raised when promotion requirements are not met."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid promotion: {reason}")
        self.reason = reason


class EvaluationGateFailedException(AILifecycleException):
    """Raised when a hard evaluation or governance gate fails."""

    def __init__(self, gate_name: str, reason: str) -> None:
        super().__init__(f"Governance gate '{gate_name}' failed: {reason}")
        self.gate_name = gate_name
        self.reason = reason


class HighRiskReleaseRequiresApprovalException(AILifecycleException):
    """Raised when a high-risk release or promotion is attempted without approval."""

    def __init__(self, resource_id: str) -> None:
        super().__init__(f"High-risk promotion/release for '{resource_id}' requires explicit human approval.")
        self.resource_id = resource_id


class ArtifactIntegrityException(AILifecycleException):
    """Raised when artifact SHA-256 fingerprint validation fails."""

    def __init__(self, artifact_id: str, expected_hash: str, actual_hash: str) -> None:
        super().__init__(f"Artifact integrity check failed for '{artifact_id}'. Expected {expected_hash}, got {actual_hash}.")
        self.artifact_id = artifact_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash


class LifecycleDelegationBlockedException(AILifecycleException):
    """Raised when delegated execution fails or is blocked."""

    def __init__(self, action: str, reason: str) -> None:
        super().__init__(f"Delegated action '{action}' blocked: {reason}")
        self.action = action
        self.reason = reason
