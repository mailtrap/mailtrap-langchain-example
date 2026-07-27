import sys

from langchain_core.messages import ToolMessage

from mailtrap_langchain_example.agent import build_agent

DEMO_PROMPT = "Send a welcome email to jane@example.com"


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


def _last_send_email_result(messages) -> str | None:
    """Prefer the tool's own literal return value over the LLM's paraphrase."""
    for message in reversed(messages):
        if isinstance(message, ToolMessage) and message.name == "send_email":
            return message.content
    return None


if __name__ == "__main__":
    main()
