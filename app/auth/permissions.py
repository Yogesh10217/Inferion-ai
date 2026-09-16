class SystemRoles:
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class SystemPermissions:
    # Inference permissions
    INFERENCE_GENERATE = "inference:generate"

    # Model management permissions
    MODELS_READ = "models:read"
    MODELS_MANAGE = "models:manage"

    # API Key permissions
    API_KEYS_READ = "api_keys:read"
    API_KEYS_MANAGE = "api_keys:manage"

    # Admin permissions
    USERS_MANAGE = "users:manage"
    ROLES_MANAGE = "roles:manage"

    # Metrics
    METRICS_READ = "metrics:read"

    @classmethod
    def all(cls):
        return [
            cls.INFERENCE_GENERATE,
            cls.MODELS_READ,
            cls.MODELS_MANAGE,
            cls.API_KEYS_READ,
            cls.API_KEYS_MANAGE,
            cls.USERS_MANAGE,
            cls.ROLES_MANAGE,
            cls.METRICS_READ,
        ]

    @classmethod
    def developer_permissions(cls):
        return [
            cls.INFERENCE_GENERATE,
            cls.MODELS_READ,
            cls.API_KEYS_READ,
            cls.API_KEYS_MANAGE,
            cls.METRICS_READ,
        ]

    @classmethod
    def viewer_permissions(cls):
        return [
            cls.MODELS_READ,
            cls.METRICS_READ,
        ]
