from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env"
    )
    app_name: str = "DevTalks"
    debug: bool = False

    database_url: str
    redis_url: str

    secret_key: str
    algorithm: str = "HS256"


settings = Settings()


