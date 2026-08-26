"""CLI Knowledge Wrapper."""

from cli.commands.knowledge import add_knowledge_parser, handle_knowledge_command
from sdk.python.llm_engine.client import LLMEngineClient


def get_client() -> LLMEngineClient:
    return LLMEngineClient()


__all__ = ["add_knowledge_parser", "handle_knowledge_command", "get_client"]
