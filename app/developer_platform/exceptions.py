"""Domain Exceptions for Developer Platform Subsystem."""


class DeveloperPlatformException(Exception):
    """Base exception for Developer Platform subsystem."""

    def __init__(self, message: str, code: str = "DEVELOPER_PLATFORM_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class DeveloperNotFoundException(DeveloperPlatformException):
    def __init__(self, developer_id: str):
        super().__init__(f"Developer '{developer_id}' not found", code="DEVELOPER_NOT_FOUND", status_code=404)


class ProjectNotFoundException(DeveloperPlatformException):
    def __init__(self, project_id: str):
        super().__init__(f"Developer project '{project_id}' not found", code="PROJECT_NOT_FOUND", status_code=404)


class InvalidProjectLifecycleTransition(DeveloperPlatformException):
    def __init__(self, current: str, target: str):
        super().__init__(
            f"Invalid project lifecycle transition from '{current}' to '{target}'",
            code="INVALID_PROJECT_LIFECYCLE",
            status_code=409,
        )


class EventSubscriptionNotFoundException(DeveloperPlatformException):
    def __init__(self, subscription_id: str):
        super().__init__(f"Event subscription '{subscription_id}' not found", code="SUBSCRIPTION_NOT_FOUND", status_code=404)


class DeveloperPermissionDeniedException(DeveloperPlatformException):
    def __init__(self, action: str):
        super().__init__(f"Permission denied for developer action '{action}'", code="DEVELOPER_PERMISSION_DENIED", status_code=403)
