from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import tenants, users, whatsapp, conversations, contacts
from api.routers import calendar_auth

app = FastAPI(title="TOIN Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://whats.criatoin.com.br",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(calendar_auth.router, prefix="/calendar", tags=["calendar"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "toin-backend"}
