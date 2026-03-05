from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class NormalizedMessage:
    from_phone: str           # formato: +5511999999999
    text: Optional[str]
    media_url: Optional[str]
    media_type: Optional[str]   # 'image', 'audio', 'document'
    instance_name: str
    raw_message_id: str
    timestamp: int


class WhatsAppAdapter(ABC):
    @abstractmethod
    async def send_text(self, instance: str, to: str, text: str) -> dict:
        ...

    @abstractmethod
    async def get_qrcode(self, instance: str) -> str:
        ...

    @abstractmethod
    async def create_instance(self, instance_name: str) -> dict:
        ...

    @abstractmethod
    async def reconnect(self, instance: str) -> dict:
        ...
