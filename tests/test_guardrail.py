import pytest

from mailtrap_langchain_example.guardrail import (
    RecipientNotAllowedError,
    assert_recipient_allowed,
    is_recipient_allowed,
)

ALLOWED_DOMAIN = "example.com"
OWN_EMAIL = "test@gmail.com"


def test_allows_recipient_on_allowed_domain():
    assert is_recipient_allowed(
        recipient="jane@example.com", allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


def test_allows_recipient_matching_own_email_exactly():
    assert is_recipient_allowed(
        recipient=OWN_EMAIL, allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


@pytest.mark.parametrize("recipient", ["Jane@EXAMPLE.com", OWN_EMAIL.upper()])
def test_is_case_insensitive(recipient):
    assert is_recipient_allowed(
        recipient=recipient, allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


def test_rejects_other_domains():
    assert not is_recipient_allowed(
        recipient="wrong@gmail.com", allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


def test_rejects_subdomain_of_allowed_domain():
    assert not is_recipient_allowed(
        recipient="jane@mail.example.com", allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


@pytest.mark.parametrize(
    "recipient", ["not-an-email", "@example.com", "jane@", "jane@example.com@"]
)
def test_rejects_malformed_address(recipient):
    assert not is_recipient_allowed(
        recipient=recipient, allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


def test_rejects_double_at_sign():
    assert not is_recipient_allowed(
        recipient="dssa@@sadsa.io", allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


def test_rejects_mismatched_domain_without_dot():
    assert not is_recipient_allowed(
        recipient="jane@example", allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


def test_allows_dotless_allowed_domain_when_configured():
    assert is_recipient_allowed(recipient="user@corp", allowed_domain="corp", own_email=OWN_EMAIL)


def test_rejects_address_with_whitespace():
    assert not is_recipient_allowed(
        recipient="jane doe@example.com", allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
    )


def test_assert_raises_on_disallowed_recipient():
    with pytest.raises(RecipientNotAllowedError):
        assert_recipient_allowed(
            recipient="attacker@gmail.com", allowed_domain=ALLOWED_DOMAIN, own_email=OWN_EMAIL
        )
