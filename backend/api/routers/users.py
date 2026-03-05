from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.deps import require_service_token
from db.client import supabase

router = APIRouter()


class UserCreate(BaseModel):
    tenant_id: str
    email: str
    role: str = "agent"


@router.post("/", status_code=201, dependencies=[Depends(require_service_token)])
def create_user(body: UserCreate):
    result = supabase.table("users").insert({
        "tenant_id": body.tenant_id,
        "email": body.email,
        "role": body.role,
    }).execute()
    return result.data[0]


@router.get("/{user_id}", dependencies=[Depends(require_service_token)])
def get_user(user_id: str):
    result = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if not result.data:
        raise HTTPException(404, "User not found")
    return result.data
