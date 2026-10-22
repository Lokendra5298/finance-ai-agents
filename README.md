# Financial AI Advisor — Groq + Phidata

An educational **AI-powered financial research assistant** built with the legacy **Phidata (`phi`)** framework and **Groq** for LLM inference. It combines Yahoo Finance stock data, DuckDuckGo web research, optional multi-agent coordination, and a browser-based interface backed by SQLite conversation storage.

> **Project scope:** This README documents the `p3_financial_advisor` files (`test_api.py`, `agents.py`, and `ui_playground.py`) discussed in this project. The linked AI Doctor repository is a different application and its audio/vision dependencies are **not** required here.

## Features

- **Single-agent analysis** in `test_api.py`: maps supported company names to ticker symbols and retrieves available financial data and analyst recommendations.
- **Multi-agent research** in `agents.py`: a Financial Analyst using Yahoo Finance and a Web Researcher using DuckDuckGo are coordinated by a team agent.
- **Browser interface** in `ui_playground.py`: choose the Finance or Web agent, enter a question, and view its answer at `/`.
- **SQLite storage** via `SqlAgentStorage` (`agents.db`) to preserve agent sessions; the custom `/ask` route does not yet implement isolated per-user browser sessions.
- **Groq API only** for model inference. No OpenAI API key or `OpenAIChat` import is needed.
- **Tool-call limits** to reduce repeated searches. External services may still rate-limit or fail.

## Tech stack

| Component | Technology |
| --- | --- |
| Agent framework | Phidata (`phi`, legacy API) |
| LLM inference | Groq (`GROQ_API_KEY`) |
| Market data | Yahoo Finance via `YFinanceTools` |
| Web research | DuckDuckGo via `DuckDuckGo` |
| API and local interface | FastAPI / Phidata Playground / Uvicorn |
| Conversation persistence | SQLite via SQLAlchemy |
| Language | Python 3.12 (the development environment shown) |

## Project structure

```text
p3_financial_advisor/
├── test_api.py          # Single financial agent
├── agents.py            # Financial + web research team
├── ui_playground.py     # Local web UI and Playground API
├── requirements.txt
├── README.md
├── .env                  # Local secret, do not commit
├── .gitignore
└── agents.db             # Generated at runtime
```

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate     # Windows PowerShell (use .venv\Scripts\Activate.ps1)
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The requirements file lists **direct dependencies**, not a frozen lockfile. Once the application works in your environment, record reproducible versions using `python -m pip freeze > requirements-lock.txt` (review the resulting packages before committing).

### 3. Set your Groq API key

Create `.env`:

```dotenv
GROQ_API_KEY=gsk_replace_with_your_key
GROQ_MODEL_ID=qwen/qwen3.8-27b
```

Get an API key at <https://console.groq.com/keys>. **Model IDs and access can change.** Check your account's available models at <https://console.groq.com/docs/models>. Change `MODEL_ID` in `test_api.py` and `agents.py` if those scripts have a hard-coded model name; the supplied web UI reads `GROQ_MODEL_ID` from `.env`.

Create `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
agents.db
*.db-journal
.pytest_cache/
```

## Run

### Single financial agent

```bash
python test_api.py
```

Example question: `Summarise and compare analyst recommendations for Apple, Tesla and Nvidia.`

### Multi-agent financial research

```bash
python agents.py
```

Example question: `Summarise analyst recommendations and share recent information about Nvidia.`

### Local web interface

```bash
python ui_playground.py
```

Open <http://localhost:7777/> for the local app, <http://localhost:7777/docs> for API documentation, and <http://localhost:7777/health> for a basic health check. The legacy hosted Phidata Playground may also connect to the application at <https://phidata.app/playground>, depending on the version and service availability.

If running on a remote development server, use SSH port forwarding (or another secure method) to access the service locally. **Do not expose `/ask` to the public internet without authentication and appropriate protections.**

## Example questions

- `What are Nvidia's available analyst recommendations?`
- `Compare Apple and Tesla based on available stock fundamentals.`
- `Find recent developments about Nvidia and cite sources.`

## How it works

```text
User
  ├─ test_api.py -> Groq financial agent -> Yahoo Finance
  ├─ agents.py   -> Groq team coordinator
  │                  ├─ Financial Analyst -> Yahoo Finance
  │                  └─ Web Researcher    -> DuckDuckGo
  └─ ui_playground.py -> FastAPI local UI -> chosen Groq agent
                                              └─ SQLite agent storage
```

The web interface currently exposes **two independent agents**, not the coordinating team from `agents.py`.

## Troubleshooting

| Issue | Recommended action |
| --- | --- |
| `ModuleNotFoundError: fastapi` | Run `python -m pip install -r requirements.txt` in the active environment. |
| `ModuleNotFoundError: openai` | Remove obsolete `from phi.model.openai import OpenAIChat` imports; this project uses Groq only. |
| Groq `model_not_found` (404) | Inspect the current Groq model catalog and select a model available to your key that supports tool calling. |
| DuckDuckGo `403 Ratelimit` | Reduce search frequency; stop retrying after failures. Search availability is not guaranteed. |
| `{"detail":"Not Found"}` at `/` | Ensure you are running the **updated** `ui_playground.py` that defines the `/` route and that port 7777 points to this server. |
| Excessive terminal logs | Use `debug_mode=False`, `show_tool_calls=False`, `stream=False`, and tool-call limits. |
| `get_client_ip: command not found` | Investigate your shell configuration; it is separate from the Groq/Phidata application. |

## Limitations and safety

- Financial figures and analyst ratings depend on third-party tools and may be delayed, incomplete, or unavailable.
- LLM output can be wrong; verify important facts against primary sources.
- Tool limits reduce repeated requests but do not impose a hard execution-time timeout.
- The current custom `/ask` API lacks authentication and explicit multi-user session isolation.
- The local UI shows Markdown as plain text; it does not render formatted Markdown tables.
- This is a learning/research project, **not personalized investment advice**.

## Credits

Built using Phidata, Groq, Yahoo Finance, DuckDuckGo, FastAPI and SQLite. The linked [AI Doctor 2.0](https://github.com/AIwithhassan/ai-doctor-2.0-voice-and-vision) project is a separate reference and is not a dependency.
