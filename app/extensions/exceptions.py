"""Domain Exceptions for Plugin & Extension Framework."""


class ExtensionFrameworkException(Exception):
    """Base exception for Extension framework."""

    def __init__(self, message: str, code: str = "EXTENSION_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class ExtensionNotFoundException(ExtensionFrameworkException):
    def __init__(self, extension_id: str):
        super().__init__(f"Extension '{extension_id}' not found", code="EXTENSION_NOT_FOUND", status_code=404)


class InvalidExtensionManifestException(ExtensionFrameworkException):
    def __init__(self, reason: str):
        super().__init__(f"Invalid extension manifest: {reason}", code="INVALID_MANIFEST", status_code=422)


class ExtensionSecurityViolationException(ExtensionFrameworkException):
    def __init__(self, reason: str):
        super().__init__(f"Extension security violation: {reason}", code="SECURITY_VIOLATION", status_code=403)


class ExtensionDependencyConflictException(ExtensionFrameworkException):
    def __init__(self, reason: str):
        super().__init__(f"Extension dependency error: {reason}", code="DEPENDENCY_ERROR", status_code=409)


class InvalidExtensionLifecycleTransition(ExtensionFrameworkException):
    def __init__(self, current: str, target: str):
        super().__init__(f"Invalid extension lifecycle transition from '{current}' to '{target}'", code="INVALID_LIFECYCLE", status_code=409)


class ExtensionRuntimeExecutionException(ExtensionFrameworkException):
    def __init__(self, extension_id: str, reason: str):
        super().__init__(f"Extension '{extension_id}' execution failed: {reason}", code="RUNTIME_EXECUTION_FAILED", status_code=500)
