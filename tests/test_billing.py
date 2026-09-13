import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_list_invoices_empty(get_client, admin_token_headers):
    async with get_client() as client:
        response = await client.get("/v1/billing/invoices", headers=admin_token_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_generate_invoice(get_client, admin_token_headers):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30)
    
    async with get_client() as client:
        # This manually triggers generating an invoice for test_org_id
        response = await client.post(
            "/v1/billing/invoices/generate",
            params={
                "organization_id": "test_org_id",
                "start_time": start.isoformat(),
                "end_time": end.isoformat()
            },
            headers=admin_token_headers
        )
        
        assert response.status_code == 200
        invoice = response.json()
        
        assert invoice["organization_id"] == "test_org_id"
        assert invoice["status"] == "generated"
        assert "subtotal" in invoice
        
        # Get invoices again, should have 1
        response2 = await client.get("/v1/billing/invoices", headers=admin_token_headers)
        assert response2.status_code == 200
        invoices = response2.json()
        assert len(invoices) >= 1
