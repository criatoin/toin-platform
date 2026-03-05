from supabase import create_client, Client
from api.config import settings


def get_supabase() -> Client:
    """
    Retorna client Supabase com service_role_key.
    O service_role_key bypassa todas as RLS policies — usar somente no backend.
    """
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# Singleton para uso no backend
supabase: Client = get_supabase()
