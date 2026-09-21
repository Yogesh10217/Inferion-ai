import pytest


@pytest.mark.asyncio
async def test_create_and_list_reports(get_client, admin_token_headers: dict):
    async with get_client() as client:
        # Create report
        response = await client.post("/v1/admin/reports?type=org_usage", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

        # List reports
        response = await client.get("/v1/admin/reports", headers=admin_token_headers)
        assert response.status_code == 200
        reports = response.json()
        assert len(reports) >= 1
