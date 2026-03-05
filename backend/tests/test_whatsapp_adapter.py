import pytest
from unittest.mock import AsyncMock, patch
from services.whatsapp.evolution import EvolutionAdapter, normalize_evolution_event


@pytest.mark.asyncio
async def test_send_text_message():
    adapter = EvolutionAdapter(base_url="http://fake", api_key="test")
    with patch.object(adapter, "_post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = {"key": {"id": "MSG123"}}
        result = await adapter.send_text(
            instance="toin-test",
            to="+5511999999999",
            text="Ola!"
        )
    assert result["message_id"] == "MSG123"
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_normalize_webhook_payload():
    raw = {
        "event": "messages.upsert",
        "instance": "toin-test",
        "data": {
            "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": False, "id": "ABC"},
            "message": {"conversation": "Quero agendar uma reuniao"},
            "messageTimestamp": 1700000000,
        },
    }
    normalized = normalize_evolution_event(raw)
    assert normalized["from_phone"] == "+5511999999999"
    assert normalized["text"] == "Quero agendar uma reuniao"
    assert normalized["instance_name"] == "toin-test"


def test_normalize_ignores_outgoing_messages():
    raw = {
        "event": "messages.upsert",
        "instance": "toin-test",
        "data": {
            "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": True, "id": "ABC"},
            "message": {"conversation": "mensagem enviada"},
            "messageTimestamp": 1700000000,
        },
    }
    assert normalize_evolution_event(raw) is None


def test_normalize_ignores_non_message_events():
    raw = {"event": "connection.update", "instance": "toin-test", "data": {}}
    assert normalize_evolution_event(raw) is None
