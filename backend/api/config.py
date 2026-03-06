from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    evolution_api_url: str
    evolution_api_key: str
    openrouter_api_key: str
    google_calendar_credentials_json: str = "{}"
    google_calendar_id: str = "primary"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    secret_key: str
    webhook_secret: str = ""



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
