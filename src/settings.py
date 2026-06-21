from logging.config import dictConfig

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.logger import LOGGING_CONFIG

# Setting up logging format and configuration for all scripts
dictConfig(LOGGING_CONFIG)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )

    llm: str = "gemini-3.5-flash"


settings = Settings()
