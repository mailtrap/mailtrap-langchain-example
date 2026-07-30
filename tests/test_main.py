import pytest
from langchain_core.messages import AIMessage, ToolMessage

from mailtrap_langchain_example.main import _last_send_email_result, _resolve_prompt


def test_uses_the_cli_argument_when_given():
    assert _resolve_prompt(["Send", "a", "note", "to", "jane@example.com"], "me@mydomain.com") == (
        "Send a note to jane@example.com"
    )


def test_falls_back_to_a_demo_send_to_own_email():
    assert _resolve_prompt([], "me@mydomain.com") == "Send a welcome email to me@mydomain.com"


def test_own_email_is_only_needed_when_there_is_no_cli_argument():
    """A domain-guardrail-only setup is valid, so an explicit prompt must still work."""
    assert _resolve_prompt(["Send a welcome email to jane@example.com"], "") == (
        "Send a welcome email to jane@example.com"
    )


def test_refuses_to_invent_a_recipient_when_own_email_is_unset():
    """Better to stop than to fall back to an address that can only bounce."""
    with pytest.raises(ValueError, match="OWN_EMAIL is not set"):
        _resolve_prompt([], "")


def test_a_whitespace_only_argument_counts_as_no_argument():
    assert _resolve_prompt(["   "], "me@mydomain.com") == "Send a welcome email to me@mydomain.com"


def test_a_whitespace_only_own_email_counts_as_unset():
    """It is falsy nowhere else, and would build a prompt naming no recipient at all."""
    with pytest.raises(ValueError, match="OWN_EMAIL is not set"):
        _resolve_prompt([], "   ")


def test_trims_padding_around_own_email():
    assert _resolve_prompt([], " me@mydomain.com ") == "Send a welcome email to me@mydomain.com"


def test_reads_the_status_off_the_last_send_email_call():
    """The tool's literal return value, not the model's paraphrase of it."""
    messages = [
        AIMessage(content="On it."),
        ToolMessage(content="REJECTED: nope", tool_call_id="1", name="send_email"),
        ToolMessage(content="SENT to me@mydomain.com", tool_call_id="2", name="send_email"),
        AIMessage(content="All done — your email is on its way!"),
    ]

    assert _last_send_email_result(messages) == "SENT to me@mydomain.com"


def test_reports_no_status_when_send_email_was_never_called():
    messages = [
        ToolMessage(content="irrelevant", tool_call_id="1", name="some_other_tool"),
        AIMessage(content="Which address should I send to?"),
    ]

    assert _last_send_email_result(messages) is None
