from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extrai tenant_id do JWT (header Authorization) e o injeta em request.state.
    O backend usa service_role_key diretamente — este middleware serve para o
    frontend autenticado via Supabase Auth (JWT).
    Implementacao completa quando adicionar autenticacao JWT na Task 4+.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.tenant_id = None
        response = await call_next(request)
        return response
