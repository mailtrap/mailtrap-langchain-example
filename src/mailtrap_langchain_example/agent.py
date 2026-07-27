import sys

from langchain.agents import create_agent

from .config import get_settings
from .mailtrap_tool import send_email

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

DEMO_PROMPT = "Send a welcome email to jane@example.com"


def build_agent():
    settings = get_settings()
    return create_agent(
        model=f"{settings.llm_provider}:{settings.llm_model}",
        tools=[send_email],
        system_prompt=SYSTEM_PROMPT,
    )


def _last_send_email_result(messages) -> str | None:
    """The LLM's final reply is a paraphrase, not a source of truth — it can
    claim success even when send_email actually returned REJECTED/FAILED (or
    invent details for a call that never happened). Prefer the tool's own
    literal return value when one exists.
    """
    for message in reversed(messages):
        if getattr(message, "type", None) == "tool" and getattr(message, "name", None) == "send_email":
            return message.content
    return None


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or DEMO_PROMPT
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    tool_result = _last_send_email_result(result["messages"])
    if tool_result is not None:
        print(tool_result)
    else:
        # No send_email call happened (e.g. the model asked for a valid
        # recipient instead) — the LLM's own reply is all there is to show.
        print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
