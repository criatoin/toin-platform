import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from api.main import app


@pytest.fixture
def mock_tenant():
    return {"id": "tenant-123", "name": "Empresa Teste", "slug": "empresa-teste"}


@pytest.mark.asyncio
async def test_list_conversations(mock_tenant):
    with patch("api.deps.supabase") as mock_db:
        mock_auth = MagicMock()
        mock_auth.user.id = "user-123"
        mock_db.auth.get_user.return_value = mock_auth
        mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "tenants": mock_tenant
        }
        mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/conversations/",
                headers={"Authorization": "Bearer fake-token"},
            )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_toggle_bot(mock_tenant):
    conversation_id = "conv-123"
    with patch("api.deps.supabase") as mock_db, \
         patch("api.routers.conversations.supabase") as mock_conv_db:
        mock_auth = MagicMock()
        mock_auth.user.id = "user-123"
        mock_db.auth.get_user.return_value = mock_auth
        mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "tenants": mock_tenant
        }
        mock_conv_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": conversation_id, "bot_active": False}
        ]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.patch(
                f"/conversations/{conversation_id}/bot",
                json={"bot_active": False},
                headers={"Authorization": "Bearer fake-token"},
            )
    assert resp.status_code == 200
    assert resp.json()["bot_active"] == False
