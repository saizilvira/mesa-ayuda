from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    app_name: str = "Mesa de Ayuda"
    app_version: str = "0.0.1"
    environment: str = "development"
    log_level: str = "INFO"

    # Servicio mock (externo)
    mock_base_url: str = "http://127.0.0.1:8080"
    mock_token: str = "demo-token-prueba-2026"   # se sobreescribe con .env
    mock_timeout: int = 5

    # IA
    ai_provider_url: str = ""
    ai_api_key: str = ""
    ai_timeout: int = 10
    ai_max_retries: int = 2


settings = Settings()