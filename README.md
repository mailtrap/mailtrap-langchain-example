# mailtrap-langchain-example

A minimal example showing the [Mailtrap Python SDK](https://github.com/mailtrap/mailtrap-python)
wrapped as a [LangChain](https://python.langchain.com) tool, driven by an agent that decides to
send an email from a natural-language prompt.

**This is not a published PyPI package** — clone it and run it directly as an example.

## What it does

`send_email` is a LangChain tool (`src/mailtrap_langchain_example/mailtrap_tool.py`) that calls
the Mailtrap Email API. `agent.py` builds an agent with LangChain's `create_agent`, given this
single tool; `main.py` is the CLI entry point that takes a prompt like:

> "Send a welcome email to jane@example.com"

The LLM decides to call `send_email`, which sends the email through Mailtrap.

## Guardrail

To make this safe to run as a demo, `send_email` only allows sending to:
- addresses on the `ALLOWED_RECIPIENT_DOMAIN` (default `example.com`), or
- the address configured in `OWN_EMAIL`

Any other recipient is rejected by `guardrail.py` **before** the Mailtrap SDK is touched, so the
agent can never accidentally email a real third party while you're experimenting with prompts.
See `tests/test_guardrail.py` for the guardrail's behavior.

`send_email` returns one of three statuses: `SENT to ...` (delivered), `REJECTED: ...` (blocked by
the guardrail, Mailtrap never contacted), or `FAILED to send to ...` (the guardrail passed but the
Mailtrap API call itself errored — bad token, bad inbox ID, network issue, etc.).

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
copy .env.example .env         # Windows: copy, macOS/Linux: cp
```

`uv sync` creates `.venv`, installs all dependencies from `pyproject.toml`/`uv.lock`, and installs
this package itself in editable mode (so its console script and absolute imports work).

Fill in `.env`. `MAILTRAP_API_TOKEN`, `MAILTRAP_SENDER_EMAIL`, and `MAILTRAP_INBOX_ID` are
**required** — `Settings` (`config.py`) has no fallback for them, so a missing value fails fast
with a clear `pydantic.ValidationError` at startup instead of silently sending from `""`:
- `MAILTRAP_API_TOKEN` — from your Mailtrap account
- `MAILTRAP_SENDER_EMAIL` / `MAILTRAP_SENDER_NAME` — the "from" address/name on sent emails
- `MAILTRAP_SANDBOX` — `true` (default) sends into a Mailtrap Sandbox inbox (safe for testing);
  `false` sends real mail via the production Sending API (requires `MAILTRAP_SENDER_EMAIL` to be
  on a domain verified in your Mailtrap account's Sending Domains settings; `MAILTRAP_INBOX_ID` is
  ignored in this mode, but must still be set to *some* value since it's a required field)
- `MAILTRAP_INBOX_ID` — required. Find it in the Mailtrap dashboard under **Email Testing →
  Inboxes → (your inbox) → Integration**, or from the inbox's URL
  (`mailtrap.io/inboxes/<inbox_id>/messages`)
- `ALLOWED_RECIPIENT_DOMAIN` — the guardrail's allowed domain (default `example.com`)
- `OWN_EMAIL` — your own address, exempted from the domain guardrail
- `LLM_PROVIDER` / `LLM_MODEL` — passed to `init_chat_model` as `"<provider>:<model>"`. Supported:
  `openai` (default, e.g. `gpt-4o-mini`) or `anthropic` (e.g. `claude-3-5-haiku-latest`)
- `LLM_API_KEY` — the API key for whichever `LLM_PROVIDER` you picked. Passed explicitly to
  `init_chat_model(..., api_key=settings.llm_api_key)` in `agent.py`, so it flows from `.env` →
  `Settings` → the model constructor directly

## Run

```bash
uv run mailtrap-langchain-example "Send a welcome email to jane@example.com"
```

Or with no argument, it runs the demo prompt above by default.

## Tests

```bash
uv run pytest
```

`test_guardrail.py` is pure unit tests (no network). `test_mailtrap_tool.py` mocks the Mailtrap
client so no real email is sent during testing.

## Known limitation

Real (non-sandbox) sending via `MAILTRAP_SANDBOX=false` has not been tested end-to-end against a
live Mailtrap account with a verified sending domain — only the guardrail/config logic that picks
`sandbox=settings.mailtrap_sandbox` has been verified. Sandbox mode (the default) **has** been
verified end-to-end against a live Mailtrap sandbox account (agent → tool →
`MailtrapClient.send()` → message received in the dashboard).

## Reference material

- [Mailtrap API docs](https://api-docs.mailtrap.io/)
- [Mailtrap Python SDK](https://github.com/mailtrap/mailtrap-python)
- [LangChain docs (Python)](https://python.langchain.com)
- [LangChain — Custom Tools](https://python.langchain.com/docs/how_to/custom_tools/)
