"""
Endpoint temporário para autorizar o Google Calendar via OAuth2.
Processo de uma vez só:
  1. Acesse https://api.whats.criatoin.com.br/calendar/auth
  2. Faça login com danillo@criatoin.com.br e autorize
  3. Copie o refresh_token retornado
  4. Configure GOOGLE_REFRESH_TOKEN no Coolify
"""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from api.config import settings

router = APIRouter()

REDIRECT_URI = "https://api.whats.criatoin.com.br/calendar/callback"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _build_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )


@router.get("/auth")
def calendar_auth():
    """Inicia o fluxo OAuth2. Acesse no browser com danillo@criatoin.com.br."""
    flow = _build_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="select_account consent",  # força escolha de conta
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
def calendar_callback(code: str):
    """Recebe o callback do Google e retorna o refresh_token."""
    flow = _build_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    return JSONResponse({
        "status": "success",
        "refresh_token": creds.refresh_token,
        "instruction": "Copie o refresh_token acima e configure GOOGLE_REFRESH_TOKEN no Coolify",
    })
