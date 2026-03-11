import httpx
from typing import Optional
from services.whatsapp.adapter import WhatsAppAdapter


class EvolutionAdapter(WhatsAppAdapter):
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {"apikey": api_key, "Content-Type": "application/json"}

    async def _post(self, path: str, body: dict) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}{path}",
                json=body,
                headers=self.headers,
                timeout=15.0,
            )
            resp.raise_for_status()
            return resp.json()

    async def send_text(self, instance: str, to: str, text: str) -> dict:
        # Evolution: remove o + do numero
        number = to.replace("+", "")
        result = await self._post(f"/message/sendText/{instance}", {
            "number": number,
            "text": text,
        })
        return {"message_id": result.get("key", {}).get("id", "")}

    async def get_qrcode(self, instance: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/instance/connect/{instance}",
                headers=self.headers,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("qrcode", {}).get("base64", "")

    async def create_instance(self, instance_name: str) -> dict:
        return await self._post("/instance/create", {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
        })

    async def reconnect(self, instance: str) -> dict:
        return await self._post(f"/instance/restart/{instance}", {})


def normalize_evolution_event(payload: dict) -> Optional[dict]:
    """
    Normaliza um evento do webhook Evolution para formato interno.
    Retorna None se nao for uma mensagem de texto/midia recebida.
    """
    if payload.get("event") != "messages.upsert":
        return None

    data = payload.get("data", {})
    key = data.get("key", {})

    # Ignorar mensagens enviadas pelo proprio bot
    if key.get("fromMe", False):
        return None

    # LID addressing: remoteJid contem um LID (ex: 280693326262354@lid)
    # O numero real esta em remoteJidAlt (ex: 5511999999999@s.whatsapp.net)
    addressing_mode = key.get("addressingMode")
    if addressing_mode == "lid" and key.get("remoteJidAlt"):
        jid = key["remoteJidAlt"]
    else:
        jid = key.get("remoteJid", "")
    # Converter JID para numero: 5511999999999@s.whatsapp.net -> +5511999999999
    phone_raw = jid.split("@")[0]
    from_phone = f"+{phone_raw}"

    msg = data.get("message", {})
    text = msg.get("conversation") or msg.get("extendedTextMessage", {}).get("text")
    media_url = None
    media_type = None

    if "imageMessage" in msg:
        media_type = "image"
    elif "audioMessage" in msg:
        media_type = "audio"
    elif "documentMessage" in msg:
        media_type = "document"

    return {
        "from_phone": from_phone,
        "text": text,
        "media_url": media_url,
        "media_type": media_type,
        "instance_name": payload.get("instance", ""),
        "raw_message_id": key.get("id", ""),
        "timestamp": data.get("messageTimestamp", 0),
    }
