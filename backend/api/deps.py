from fastapi import Header, HTTPException
from db.client import supabase
from api.config import settings


async def require_service_token(x_service_token: str = Header(...)):
    """Para endpoints internos/admin chamados pelo proprio sistema."""
    if x_service_token != settings.secret_key:
        raise HTTPException(status_code=403, detail="Invalid service token")


async def get_tenant_from_slug(slug: str):
    result = supabase.table("tenants").select("*").eq("slug", slug).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return result.data


async def get_tenant_from_jwt(authorization: str = Header(...)):
    """Valida JWT do Supabase e retorna o tenant do usuario autenticado."""
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(401, "Invalid token")

    user_record = (
        supabase.table("users")
        .select("*, tenants(*)")
        .eq("id", user.user.id)
        .maybe_single()
        .execute()
    )
    if not user_record or not user_record.data:
        raise HTTPException(403, "User has no tenant")
    return user_record.data["tenants"]
