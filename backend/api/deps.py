from fastapi import Header, HTTPException
from api.config import settings


async def require_service_token(x_service_token: str = Header(...)):
    """Para endpoints internos/admin chamados pelo próprio sistema."""
    if x_service_token != settings.secret_key:
        raise HTTPException(status_code=403, detail="Invalid service token")


async def get_tenant_from_jwt(authorization: str = Header(...)):
    """
    Placeholder — implementado completamente na Task 2.
    Valida JWT do Supabase e retorna o tenant do usuário.
    """
    raise HTTPException(status_code=501, detail="JWT auth not yet implemented")
