from app.schemas.inference_response import InferenceResponse


class CacheSerializer:
    """Handles serialization and deserialization of objects for the cache."""

    @staticmethod
    def serialize(response: InferenceResponse) -> str:
        """Serialize an InferenceResponse to a string."""
        # model_dump_json is available in Pydantic v2
        return response.model_dump_json()

    @staticmethod
    def deserialize(data: str) -> InferenceResponse:
        """Deserialize a string back to an InferenceResponse."""
        # model_validate_json is available in Pydantic v2
        return InferenceResponse.model_validate_json(data)
