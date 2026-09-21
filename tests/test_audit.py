import pytest

from app.admin.audit_service import AuditAdminService
from app.core.database import async_session_maker


@pytest.mark.asyncio
async def test_audit_event_recording_and_search(get_client, admin_token_headers: dict):
    async with async_session_maker() as db:
        audit_service = AuditAdminService(db)

        # 1. Record Audit Event
        event = await audit_service.record_event(
            action="user.login",
            actor_id="admin_user_id",
            organization_id="test_org_id",
            resource_type="user",
            resource_id="admin_user_id",
            status="success",
            severity="info",
            details={"ip": "127.0.0.1"},
        )
        assert event.id is not None
        assert event.action == "user.login"

        # 2. Search Audit Events via Service
        events = await audit_service.search_events(organization_id="test_org_id", action="user.login", severity="info")
        assert len(events) >= 1
        assert events[0].actor_id == "admin_user_id"

    # 3. Search Audit Events via REST API
    async with get_client() as client:
        response = await client.get("/v1/admin/audit?organization_id=test_org_id&limit=10", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(e["action"] == "user.login" for e in data)
