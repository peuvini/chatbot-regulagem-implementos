from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/regulagem_implementos"
    app_name: str = "Chatbot de Regulagem de Implementos"
    environment: str = "development"
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def app_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def project_dir(self) -> Path:
        return self.app_dir.parents[1]

    @property
    def ocr_dir(self) -> Path:
        return self.project_dir / "ocr"

    @property
    def artifacts_dir(self) -> Path:
        return self.app_dir.parents[0] / "artifacts"

    @property
    def model_path(self) -> Path:
        return self.artifacts_dir / "power_model.json"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
