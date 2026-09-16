import hashlib
import json

from app.schemas.request import InferenceRequest


class CacheKeyBuilder:
    """Builder for generating deterministic cache keys."""

    PREFIX = "v1"

    @classmethod
    def generate_key(cls, provider_id: str, model_id: str, request: InferenceRequest) -> str:
        """
        Generate a deterministic cache key based on provider, model, and request parameters.
        """
        # Normalize messages
        normalized_messages = []
        for msg in request.messages:
            if isinstance(msg, dict):
                normalized_messages.append({"role": msg.get("role", ""), "content": msg.get("content", "")})
            else:
                normalized_messages.append({"role": getattr(msg, "role", ""), "content": getattr(msg, "content", "")})

        # Key components
        components = {
            "messages": normalized_messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stop": sorted(request.stop) if request.stop else None,
            "max_tokens": request.max_tokens,
        }

        # Create deterministic JSON string (sorted keys)
        serialized = json.dumps(components, sort_keys=True, separators=(",", ":"))

        # Hash the string
        hash_digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        return f"{cls.PREFIX}:{provider_id}:{model_id}:{hash_digest}"
