from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment.

    We use pydantic.BaseSettings so environment variables, a .env file,
    or system environment can configure the app. This is more testable
    and safer than reading raw os.environ everywhere.
    """

    # For local development we provide a SQLite fallback so the app
    # starts even if DATABASE_URL is not set in the environment.
    # In production set `DATABASE_URL` to your Postgres URL.
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = "change-me"
    APP_ENV: str = "development"
    DOWNLOADS_DIR: Path = Path.home() / "Downloads"
    # External provider settings
    DID_API_KEY: str | None = None
    DID_API_URL: str = "https://api.d-id.com/talks"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
