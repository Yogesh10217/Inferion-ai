import pytest
from sdk.python.llm_engine.client import LLMEngineClient

def test_sdk_knowledge_client_presence():
    client = LLMEngineClient()
    assert hasattr(client, 'knowledge')
