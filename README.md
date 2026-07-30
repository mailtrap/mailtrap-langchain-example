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

`create_agent` is LangChain 1.x's replacement for the 0.x `AgentExecutor`, which no longer exists
in `langchain.agents` (it now lives in the deprecated `langchain-classic`). It compiles to a
LangGraph `CompiledStateGraph` running the same tool-calling loop — so this is the standard
`@tool` + LangGraph agent pattern.

## Guardrail

To make this safe to run as a demo, `send_email` only allows sending to:
- addresses on the `ALLOWED_RECIPIENT_DOMAIN` (default `example.com`), or
- the address configured in `OWN_EMAIL`

Any other recipient is rejected by `guardrail.py` **before** the Mailtrap SDK is touched, so the
agent can never accidentally email a real third party while you're experimenting with prompts.
See `tests/test_guardrail.py` for the guardrail's behavior.

`send_email` returns one of three statuses: `SENT to ...` (delivered), `REJECTED: ...` (blocked by
the guardrail, Mailtrap never contacted), or `FAILED to send to ...` (the guardrail passed but the
Mailtrap API call itself errored — bad token, unverified sending domain, network issue, etc.).

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
cp .env.example .env           # Windows: copy .env.example .env
```

Fill in `.env`. `MAILTRAP_API_TOKEN`, `MAILTRAP_SENDER_EMAIL`, and `LLM_API_KEY` are **required and
must be non-empty** — a value that is missing *or* left blank stops the run at startup (`config.py`)
and names the offending settings, before any LLM or Mailtrap call is made.

- `MAILTRAP_API_TOKEN` — from your Mailtrap account
- `MAILTRAP_SENDER_EMAIL` / `MAILTRAP_SENDER_NAME` — the "from" address/name on sent emails. Mail
  goes out through the production **Sending API**, so `MAILTRAP_SENDER_EMAIL` must be on a domain
  verified in your Mailtrap account's **Sending Domains** settings
- `ALLOWED_RECIPIENT_DOMAIN` — the guardrail's allowed domain (default `example.com`)
- `OWN_EMAIL` — your own address, exempted from the domain guardrail
- `LLM_PROVIDER` / `LLM_MODEL` — passed to `init_chat_model` as `"<provider>:<model>"`. Installed
  and ready to use: `google_genai` (default, `gemini-flash-lite-latest` — free tier, no billing
  account needed), `openai` (e.g. `gpt-4o-mini`), or `anthropic` (e.g. `claude-3-5-haiku-latest`).
  Any other provider LangChain supports works too, once its `langchain-<provider>` package is
  installed — nothing in the code is provider-specific. The default deliberately uses a moving
  `-latest` alias (Google retires pinned models for new accounts) and the `-lite` tier (the
  free-tier daily cap is per model, and `-lite` has the most usable one)
- `LLM_API_KEY` — required. The key for whichever `LLM_PROVIDER` you picked. Passed explicitly to
  `init_chat_model`, so the provider's own `GOOGLE_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`
  environment variable is **not** consulted

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
client so no real email is sent during testing, and sets every required setting itself, so the
suite passes without a `.env` file and without real credentials.

Beyond the suite, the agent → tool → `MailtrapClient.send()` flow has been run end-to-end against a
live Mailtrap account. Sending now defaults to the production Sending API, which delivers real mail
only from a verified sending domain — that specific path has not been exercised against a live
verified domain here.

## Reference material

- [Mailtrap API docs](https://api-docs.mailtrap.io/)
- [Mailtrap Python SDK](https://github.com/mailtrap/mailtrap-python)
- [LangChain docs (Python)](https://python.langchain.com)
- [LangChain — Custom Tools](https://python.langchain.com/docs/how_to/custom_tools/)
