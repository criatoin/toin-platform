import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from unittest.mock import patch


TEST_TOKEN = "test-service-token"


@pytest.mark.asyncio
async def test_create_tenant():
    with patch("api.deps.settings") as mock_settings:
        mock_settings.secret_key = TEST_TOKEN
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/tenants/",
                json={"name": "Empresa Teste", "slug": "empresa-teste", "plan_name": "basic"},
                headers={"X-Service-Token": TEST_TOKEN},
            )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "empresa-teste"


@pytest.mark.asyncio
async def test_get_tenant():
    with patch("api.deps.settings") as mock_settings:
        mock_settings.secret_key = TEST_TOKEN
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/tenants/empresa-teste",
                headers={"X-Service-Token": TEST_TOKEN},
            )
    assert resp.status_code == 200
