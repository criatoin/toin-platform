"""
Endpoint para autorizar o Google Calendar via OAuth2.
Processo de uma vez só:
  1. Acesse https://api.whats.criatoin.com.br/calendar/auth
  2. Faça login com danillo@criatoin.com.br e autorize
  3. Copie o refresh_token retornado
  4. Informe ao desenvolvedor para configurar GOOGLE_REFRESH_TOKEN no Coolify
"""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from api.config import settings

router = APIRouter()

REDIRECT_URI = "https://api.whats.criatoin.com.br/calendar/callback"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _build_flow(code_verifier: str | None = None) -> Flow:
    flow = Flow.from_client_config(
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
    if code_verifier is not None:
        flow.code_verifier = code_verifier
    return flow


@router.get("/auth")
def calendar_auth():
    """Inicia o fluxo OAuth2. Acesse no browser com danillo@criatoin.com.br."""
    flow = _build_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="select_account consent",
    )
    # Salva o code_verifier PKCE em cookie seguro para usar no callback
    resp = RedirectResponse(auth_url)
    if flow.code_verifier:
        resp.set_cookie(
            "toin_cv",
            flow.code_verifier,
            httponly=True,
            secure=True,
            max_age=300,  # 5 minutos
            samesite="lax",
        )
    return resp


@router.get("/callback")
def calendar_callback(request: Request, code: str):
    """Recebe o callback do Google e retorna o refresh_token."""
    # Recupera o code_verifier do cookie
    code_verifier = request.cookies.get("toin_cv")
    flow = _build_flow(code_verifier=code_verifier)
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "hint": "Tente novamente em /calendar/auth"},
            status_code=400,
        )
    creds = flow.credentials
    return JSONResponse({
        "status": "success",
        "refresh_token": creds.refresh_token,
        "instruction": "Copie o refresh_token e informe ao desenvolvedor para configurar no Coolify",
    })
