import sys

from langchain_core.messages import ToolMessage

from mailtrap_langchain_example.agent import build_agent

DEMO_PROMPT = "Send a welcome email to jane@example.com"


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or DEMO_PROMPT
    try:
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


def _last_send_email_result(messages) -> str | None:
    """Prefer the tool's own literal return value over the LLM's paraphrase."""
    for message in reversed(messages):
        if isinstance(message, ToolMessage) and message.name == "send_email":
            return message.text
    return None


if __name__ == "__main__":
    main()
