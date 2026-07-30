import pytest

from mailtrap_langchain_example.main import _resolve_prompt


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
