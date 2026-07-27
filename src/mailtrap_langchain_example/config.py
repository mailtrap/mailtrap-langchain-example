import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    mailtrap_api_token: str
    mailtrap_sender_email: str
    mailtrap_sender_name: str
    mailtrap_inbox_id: str
    mailtrap_sandbox: bool
    allowed_recipient_domain: str
    own_email: str
    llm_provider: str
    llm_model: str


def get_settings() -> Settings:
    return Settings(
        mailtrap_api_token=os.environ.get("MAILTRAP_API_TOKEN", ""),
        mailtrap_sender_email=os.environ.get("MAILTRAP_SENDER_EMAIL", ""),
        mailtrap_sender_name=os.environ.get("MAILTRAP_SENDER_NAME", "Demo Bot"),
        mailtrap_inbox_id=os.environ.get("MAILTRAP_INBOX_ID", "123567"),
        mailtrap_sandbox=os.environ.get("MAILTRAP_SANDBOX", "true").strip().lower()
        in ("1", "true", "yes"),
        allowed_recipient_domain=os.environ.get("ALLOWED_RECIPIENT_DOMAIN", "example.com"),
        own_email=os.environ.get("OWN_EMAIL", ""),
        llm_provider=os.environ.get("LLM_PROVIDER", "openai"),
        llm_model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    )
