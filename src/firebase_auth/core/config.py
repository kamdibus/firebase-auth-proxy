from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using the same Firebase env vars as frontend service."""

    model_config = SettingsConfigDict(env_file=['.env.local', '.env'], env_file_encoding='utf-8', extra='ignore')

    # Firebase Admin SDK Configuration (exact same names as frontend service)
    firebase_admin_private_key: str
    firebase_admin_client_email: str
    firebase_admin_project_id: str

    # Service Configuration
    port: int = 8001
    log_level: str = 'INFO'
    environment: str = 'development'


def get_settings() -> Settings:
    return Settings()
