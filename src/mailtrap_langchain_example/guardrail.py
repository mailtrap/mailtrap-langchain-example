import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+$")


class RecipientNotAllowedError(ValueError):
    pass


def is_recipient_allowed(*, recipient: str, allowed_domain: str, own_email: str) -> bool:
    recipient = recipient.strip().lower()
    if not EMAIL_PATTERN.match(recipient):
        return False

    if own_email and recipient == own_email.strip().lower():
        return True

    domain = recipient.rsplit("@", 1)[1]
    return domain == allowed_domain.strip().lower()


def assert_recipient_allowed(*, recipient: str, allowed_domain: str, own_email: str) -> None:
    if not is_recipient_allowed(
        recipient=recipient, allowed_domain=allowed_domain, own_email=own_email
    ):
        raise RecipientNotAllowedError(
            f"Recipient '{recipient}' is not allowed. This demo only sends to "
            f"@{allowed_domain} addresses or the configured OWN_EMAIL."
        )
