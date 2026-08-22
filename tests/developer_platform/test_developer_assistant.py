"""Unit tests for DeveloperAssistantManager."""

import pytest
from app.developer_platform.developer_assistant import DeveloperAssistantManager


def test_developer_assistant_recommendation_and_redaction():
    assistant = DeveloperAssistantManager()
    rec = assistant.assist_developer("How to handle exceptions?", repository_id="repo_101", tenant_id="t_ast")

    assert rec.guidance is not None
    assert len(rec.source_references) > 0
    assert rec.confidence > 0.8
