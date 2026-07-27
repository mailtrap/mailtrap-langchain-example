import os

os.environ.setdefault("MAILTRAP_API_TOKEN", "test-token")
os.environ.setdefault("MAILTRAP_SENDER_EMAIL", "sender@yourdomain.com")
os.environ.setdefault("ALLOWED_RECIPIENT_DOMAIN", "example.com")
os.environ.setdefault("OWN_EMAIL", "test@test.io")

from mailtrap_langchain_example import mailtrap_tool  # noqa: E402


class FakeMailtrapClient:
    last_mail = None

    def __init__(self, token, sandbox=False, inbox_id=None):
        self.token = token
        self.sandbox = sandbox
        self.inbox_id = inbox_id

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
