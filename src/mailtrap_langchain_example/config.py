from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", frozen=True
    )

    mailtrap_api_token: str = ""
    mailtrap_sender_email: str = ""
    mailtrap_sender_name: str = "Demo Bot"
    mailtrap_inbox_id: str = "123567"
    mailtrap_sandbox: bool = True
    allowed_recipient_domain: str = "example.com"
    own_email: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""


def get_settings() -> Settings:
    return Settings()
