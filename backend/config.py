from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    db_url: str = Field(default="postgresql+asyncpg://authone:authone@localhost:5432/authone")
    casbin_model_path: str = Field(default="rbac_model.conf")
    # policy is stored in Postgres; path is unused, but kept for compatibility
    log_level: str = Field(default="INFO")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"