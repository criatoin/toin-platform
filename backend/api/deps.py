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
