"""Settings are read from environment variables / a .env file (12-factor style)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://bl_user:bl_pass@127.0.0.1:3306/business_listings"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_bulk_rows: int = 5000  # guard against accidental giant payloads

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
