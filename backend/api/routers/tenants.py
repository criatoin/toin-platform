from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.deps import require_service_token
from db.client import supabase

router = APIRouter()


class TenantCreate(BaseModel):
    name: str
    slug: str
    plan_name: str = "basic"


@router.post("/", status_code=201, dependencies=[Depends(require_service_token)])
def create_tenant(body: TenantCreate):
    plan = supabase.table("plans").select("id").eq("name", body.plan_name).single().execute()
    if not plan.data:
        raise HTTPException(400, "Plan not found")

    result = supabase.table("tenants").insert({
        "name": body.name,
        "slug": body.slug,
        "plan_id": plan.data["id"],
    }).execute()
    return result.data[0]


@router.get("/{slug}", dependencies=[Depends(require_service_token)])
def get_tenant(slug: str):
    result = supabase.table("tenants").select("*, plans(*)").eq("slug", slug).single().execute()
    if not result.data:
        raise HTTPException(404, "Tenant not found")
    return result.data
