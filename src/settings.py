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
    PROJECT_ID: str = "iweb-dev-fatwatok-search-0"
    LOCATION: str = "global"
    APP_ID: str = "fatwa-semantic-search_1780905407665"
    CREDENTIALS_PATH: str = "./credentials/iweb-dev-fatwatok-search-0-cr_sa.json"
    max_retries: int = 3
    demo_scenario: int = 2  # 0 = real retrieval, 1 = sufficient on first try, 2 = retry once


settings = Settings()
