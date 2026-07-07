from pydantic import BaseSettings

# class Settings(BaseSettings) — Pydantic reads environment variables into typed attributes (12-factor app).
# DATABASE_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES — central config values; set via .env or environment.
# class Config: env_file = "../../.env" — point to repo-level .env during local development.

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        # Point to repository-level .env (two folders up from this file)
        env_file = "../../.env"


settings = Settings()
