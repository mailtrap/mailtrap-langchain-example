import pytest

from mailtrap_langchain_example import mailtrap_tool
from mailtrap_langchain_example.config import get_settings


@pytest.fixture(autouse=True)
def mailtrap_env(monkeypatch):
    """Set every required setting, so the tests pass with no .env on disk."""
    monkeypatch.setenv("MAILTRAP_API_TOKEN", "test-token")
    monkeypatch.setenv("MAILTRAP_SENDER_EMAIL", "sender@yourdomain.com")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("ALLOWED_RECIPIENT_DOMAIN", "example.com")
    monkeypatch.setenv("OWN_EMAIL", "test@test.io")
    # get_settings is cached, so drop anything a previous test cached — and
    # don't leave these test values behind for the next one.
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class FakeMailtrapClient:
    last_mail = None

    def __init__(self, token):
        self.token = token

    def send(self, mail):
        FakeMailtrapClient.last_mail = mail
        return {"success": True, "message_ids": ["fake-id-123"]}


def test_rejects_disallowed_recipient_without_calling_mailtrap(monkeypatch):
    monkeypatch.setattr(mailtrap_tool.mt, "MailtrapClient", FakeMailtrapClient)
    FakeMailtrapClient.last_mail = None

    result = mailtrap_tool.send_email.invoke(
        {"to": "attacker@gmail.com", "subject": "hi", "body": "hello"}
    )

    assert result.startswith("REJECTED")
    assert FakeMailtrapClient.last_mail is None


def test_sends_to_allowed_recipient(monkeypatch):
    monkeypatch.setattr(mailtrap_tool.mt, "MailtrapClient", FakeMailtrapClient)
    FakeMailtrapClient.last_mail = None

    result = mailtrap_tool.send_email.invoke(
        {"to": "jane@example.com", "subject": "Welcome", "body": "Hi Jane!"}
    )

    assert result.startswith("SENT to jane@example.com")
    assert FakeMailtrapClient.last_mail is not None
    assert FakeMailtrapClient.last_mail.to[0].email == "jane@example.com"


def test_tags_every_send_with_the_category_for_mailtrap_stats(monkeypatch):
    monkeypatch.setattr(mailtrap_tool.mt, "MailtrapClient", FakeMailtrapClient)
    FakeMailtrapClient.last_mail = None

    mailtrap_tool.send_email.invoke(
        {"to": "jane@example.com", "subject": "Welcome", "body": "Hi Jane!"}
    )

    mail = FakeMailtrapClient.last_mail
    assert mail.category == "langchain-example"
    assert mail.headers == {"X-MT-Category": "langchain-example"}


def test_allows_own_email_override(monkeypatch):
    monkeypatch.setattr(mailtrap_tool.mt, "MailtrapClient", FakeMailtrapClient)
    FakeMailtrapClient.last_mail = None

    result = mailtrap_tool.send_email.invoke(
        {"to": "test@test.io", "subject": "Test", "body": "Hi!"}
    )

    assert result.startswith("SENT to")


def test_reports_failure_instead_of_raising_when_mailtrap_send_fails(monkeypatch):
    class FailingMailtrapClient(FakeMailtrapClient):
        def send(self, mail):
            raise mailtrap_tool.mt.exceptions.APIError(status=401, errors=["Invalid API token"])

    monkeypatch.setattr(mailtrap_tool.mt, "MailtrapClient", FailingMailtrapClient)

    result = mailtrap_tool.send_email.invoke(
        {"to": "jane@example.com", "subject": "Welcome", "body": "Hi Jane!"}
    )

    assert result.startswith("FAILED to send to jane@example.com")
