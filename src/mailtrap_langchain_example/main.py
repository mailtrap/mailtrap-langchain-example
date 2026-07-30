import sys

from langchain_core.messages import ToolMessage

from mailtrap_langchain_example.agent import build_agent
from mailtrap_langchain_example.config import get_settings


def main() -> None:
    try:
        settings = get_settings()
        prompt = _resolve_prompt(sys.argv[1:], settings.own_email)
        agent = build_agent()
    except ValueError as error:
        sys.exit(f"{error}\n\nCheck .env — see the Setup section of README.md.")

    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    tool_result = _last_send_email_result(result["messages"])
    if tool_result is not None:
        print(tool_result)
    else:
        reply = result["messages"][-1].text
        print(reply or "The model returned no text and did not call send_email.")


def _resolve_prompt(cli_words: list[str], own_email: str) -> str:
    prompt = " ".join(cli_words)
    if prompt:
        return prompt

    if not own_email:
        raise ValueError(
            "No recipient for a run with no argument: OWN_EMAIL is not set.\n"
            "Either set it, or name a recipient in the prompt:\n"
            '  uv run mailtrap-langchain-example "Send a welcome email to you@yourdomain.com"'
        )

    return f"Send a welcome email to {own_email}"


def _last_send_email_result(messages) -> str | None:
    """Prefer the tool's own literal return value over the LLM's paraphrase."""
    for message in reversed(messages):
        if isinstance(message, ToolMessage) and message.name == "send_email":
            return message.text
    return None


if __name__ == "__main__":
    main()
