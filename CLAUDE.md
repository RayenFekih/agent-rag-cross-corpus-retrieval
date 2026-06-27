# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This is an **initial draft**. Agent interfaces and the retrieval connector exist, but the Google ADK orchestration, prompt content, and end-to-end pipeline are not yet implemented. `main.py` is currently empty.

## Commands

```sh
# Install dependencies
poetry install

# Add Google ADK when implementation begins
poetry add 'google-adk>=2.0,<3.0'

# Run the pipeline (target interface, not yet implemented)
poetry run python main.py "your query"

# Lint
poetry run ruff check src/
poetry run ruff format src/

# Lint with auto-fix
poetry run ruff check --fix src/

# Tests
poetry run pytest
poetry run pytest tests/path/to/test_file.py::test_name  # single test
poetry run pytest --cov=src                              # with coverage
```

## Architecture

The intended pipeline is a **retrieval loop** orchestrated with **Google ADK v2.0**:

```
User query → QueryRewriterAgent → SearchPlanAgent → Retrieval Engine (Discovery Engine)
                ↑                                           ↓
                └──── EvaluationAgent (insufficient) ───────┘
                                   ↓ (sufficient)
                             LLM Generator → Grounded answer
```

### Key source files

| File | Role |
|---|---|
| `src/agents.py` | Abstract `Agent` base class; `QueryRewriterAgent`, `SearchPlanAgent`, `EvaluationAgent` stubs — each reads prompts from `src/prompts.py` and LLM name from `settings.llm` |
| `src/prompts.py` | System and user prompt strings for each agent — currently empty placeholders |
| `src/retrieval.py` | `search_agent_search()` calls Google Cloud Discovery Engine (Vertex AI Search) and returns ranked result dicts including keyword/semantic similarity scores |
| `src/utils.py` | `load_service_account_credentials()` and `create_discovery_engine_client()` — creates the Discovery Engine client from a service account JSON file |
| `src/settings.py` | Pydantic `BaseSettings` loaded from `.env`; exposes `llm`, `PROJECT_ID`, `LOCATION`, `APP_ID`, `CREDENTIALS_PATH` |
| `src/logger.py` | Logging config: DEBUG to stdout, ERROR to rotating `logs/error.log` (5 MB, 3 backups); initialized at import time via `dictConfig` in `settings.py` |

### Configuration (`.env`)

```dotenv
GOOGLE_API_KEY=your_key_here
LLM=gemini-3.5-flash          # default if omitted
PROJECT_ID=...
LOCATION=global
APP_ID=...
CREDENTIALS_PATH=./credentials/your-sa.json
```

The `Settings` object is a singleton imported as `from src.settings import settings`. Logging is initialized as a side effect of importing `settings`.

### Retrieval connector

`search_agent_search()` in `src/retrieval.py` takes a pre-built `SearchServiceClient` (from `src/utils.py`) and returns a list of dicts with fatwa-domain fields (`fatwa_id`, `fatwa_title`, `fatwa_tree`, `fatwa_date`, `fatwa_summary`) plus Discovery Engine rank signals. The domain fields are specific to the current corpus; adapt `parse_search_result()` when connecting additional corpora.

## Google Developer Knowledge MCP

Configure the **Google Developer Knowledge MCP** at the project level to get up-to-date Google ADK v2.0 documentation while implementing agents and orchestration. Use it to verify agent construction, tool integration, and retrieval patterns before committing.

## Linting rules (ruff.toml)

Line length: 115. Enabled rule sets: `E`, `F`, `UP`, `B`, `I`, `NPY`, `PD`, `PT`. `E501` (line-length) is ignored. Double quotes, 4-space indent.
