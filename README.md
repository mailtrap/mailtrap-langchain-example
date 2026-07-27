# mailtrap-langchain-example

A minimal example showing the [Mailtrap Python SDK](https://github.com/mailtrap/mailtrap-python)
wrapped as a [LangChain](https://python.langchain.com) tool, driven by an agent that decides to
send an email from a natural-language prompt.

**This is not a published PyPI package** — clone it and run it directly as an example.

## What it does

`send_email` is a LangChain tool (`src/mailtrap_langchain_example/mailtrap_tool.py`) that calls
the Mailtrap Email API. An agent (`src/mailtrap_langchain_example/agent.py`), built with
LangChain's `create_agent`, is given this single tool and a prompt like:

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

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
copy .env.example .env         # Windows: copy, macOS/Linux: cp
```

Fill in `.env`:
- `MAILTRAP_API_TOKEN` — from your Mailtrap account
- `MAILTRAP_SENDER_EMAIL` / `MAILTRAP_SENDER_NAME` — the "from" address/name on sent emails
- `MAILTRAP_SANDBOX` — `true` (default) sends into a Mailtrap Sandbox inbox (safe for testing,
  requires `MAILTRAP_INBOX_ID`); `false` sends real mail via the production Sending API (requires
  `MAILTRAP_SENDER_EMAIL` to be on a domain verified in your Mailtrap account's Sending Domains
  settings; `MAILTRAP_INBOX_ID` is ignored)
- `MAILTRAP_INBOX_ID` — required when `MAILTRAP_SANDBOX=true`. Find it in the Mailtrap dashboard
  under **Email Testing → Inboxes → (your inbox) → Integration**, or from the inbox's URL
  (`mailtrap.io/inboxes/<inbox_id>/messages`)
- `ALLOWED_RECIPIENT_DOMAIN` — the guardrail's allowed domain (default `example.com`)
- `OWN_EMAIL` — your own address, exempted from the domain guardrail
- `LLM_PROVIDER` / `LLM_MODEL` — passed to `create_agent` as `"<provider>:<model>"`. Defaults to
  `openai` / `gpt-4o-mini`; set `LLM_PROVIDER=groq` with an appropriate `LLM_MODEL` (e.g.
  `llama-3.3-70b-versatile`) to use [Groq](https://console.groq.com/keys) instead, or
  `LLM_PROVIDER=anthropic` (e.g. `claude-3-5-haiku-latest`) for Anthropic. Any other provider
  LangChain's `create_agent` supports works too, as long as its `langchain-<provider>` package
  is installed
- `OPENAI_API_KEY`, `GROQ_API_KEY`, or `ANTHROPIC_API_KEY` — whichever matches `LLM_PROVIDER`

## Run

```bash
python scripts/run_agent.py "Send a welcome email to jane@example.com"
```

Or with no argument, it runs the demo prompt above by default.

## Tests

```bash
pytest
```

`test_guardrail.py` is pure unit tests (no network). `test_mailtrap_tool.py` mocks the Mailtrap
client so no real email is sent during testing.

## Reference material

- [Mailtrap API docs](https://api-docs.mailtrap.io/)
- [Mailtrap Python SDK](https://github.com/mailtrap/mailtrap-python)
- [LangChain docs (Python)](https://python.langchain.com)
- [LangChain — Custom Tools](https://python.langchain.com/docs/how_to/custom_tools/)
