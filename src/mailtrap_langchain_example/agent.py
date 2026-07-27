from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from mailtrap_langchain_example.config import get_settings
from mailtrap_langchain_example.mailtrap_tool import send_email

SYSTEM_PROMPT = (
    "You are an assistant that sends transactional emails on request. "
    "Use the send_email tool whenever the user asks you to send, notify, "
    "or welcome someone by email. The user's message must contain an "
    "explicit, complete recipient email address in local-part@domain form. "
    "Pass that address to send_email exactly as the user wrote it — do not "
    "invent, guess, default, complete, or auto-correct it in any way (do not "
    "strip stray characters, do not fill in a missing local part). If the "
    "text after 'to' is missing, incomplete (e.g. '@example.com' with no "
    "local part), or otherwise not a complete address, do not call "
    "send_email — ask the user to provide a valid recipient address instead. "
    "Always relay send_email's returned status (SENT or REJECTED) to the "
    "user faithfully — never claim an email was sent if the tool did not "
    "return a SENT result."
)


def build_agent():
    settings = get_settings()
    model = init_chat_model(
        f"{settings.llm_provider}:{settings.llm_model}",
        api_key=settings.llm_api_key,
    )
    return create_agent(
        model=model,
        tools=[send_email],
        system_prompt=SYSTEM_PROMPT,
    )
