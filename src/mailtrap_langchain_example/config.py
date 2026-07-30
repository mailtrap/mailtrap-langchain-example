from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", frozen=True
    )

    mailtrap_api_token: str = Field(min_length=1)
    mailtrap_sender_email: str = Field(min_length=1)
    mailtrap_sender_name: str = "Demo Bot"
    allowed_recipient_domain: str = "example.com"
    own_email: str = ""
    llm_provider: str = "google_genai"
    llm_model: str = "gemini-flash-lite-latest"
    llm_api_key: str = Field(min_length=1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
