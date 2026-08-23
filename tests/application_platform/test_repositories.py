"""Unit tests for Repository Abstraction Layer."""

import pytest
from app.application_platform.repositories import InMemoryApplicationRepository, SQLAlchemyApplicationRepository


def test_in_memory_repository_crud():
    repo = InMemoryApplicationRepository()
    saved = repo.save_application({"application_id": "app_1", "tenant_id": "t1", "name": "App One"})
    assert saved["name"] == "App One"

    fetched = repo.get_application("app_1", "t1")
    assert fetched["name"] == "App One"

    listed = repo.list_applications("t1")
    assert len(listed) == 1

    deleted = repo.delete_application("app_1", "t1")
    assert deleted is True
    assert repo.get_application("app_1", "t1") is None


def test_sqlalchemy_repository_fallback_safety():
    repo = SQLAlchemyApplicationRepository()
    saved = repo.save_application({"application_id": "app_2", "tenant_id": "t1", "name": "App Two"})
    assert saved["name"] == "App Two"
