import mailtrap as mt
import requests
from langchain_core.tools import tool

from mailtrap_langchain_example.config import get_settings
from mailtrap_langchain_example.guardrail import RecipientNotAllowedError, assert_recipient_allowed


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send a transactional email via Mailtrap.

    Args:
        to: recipient email address. For this demo it MUST be on the
            example.com domain or the operator's own verified address.
        subject: email subject line.
        body: plain-text email body.

    Returns:
        A short status string confirming the send, or an explanation if the
        recipient was rejected by the guardrail.
    """
    settings = get_settings()
    to = to.strip()

    try:
        assert_recipient_allowed(
            recipient=to,
            allowed_domain=settings.allowed_recipient_domain,
            own_email=settings.own_email,
        )
    except RecipientNotAllowedError as error:
        return f"REJECTED: {error}"

    client = mt.MailtrapClient(
        token=settings.mailtrap_api_token,
        sandbox=settings.mailtrap_sandbox,
        inbox_id=settings.mailtrap_inbox_id if settings.mailtrap_sandbox else None,
    )
    mail = mt.Mail(
        sender=mt.Address(email=settings.mailtrap_sender_email, name=settings.mailtrap_sender_name),
        to=[mt.Address(email=to)],
        subject=subject,
        text=body,
    )
    try:
        response = client.send(mail)
    except (mt.exceptions.MailtrapError, requests.exceptions.RequestException) as error:
        return f"FAILED to send to {to}: {error}"

    message_ids = response.get("message_ids", [])
    return f"SENT to {to} (message_ids={message_ids})"
