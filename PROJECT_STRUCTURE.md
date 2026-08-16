# Project structure — Discord Thread Bot

Purpose
- Short description: a Discord bot that scans forum threads, summarizes them, stores summaries in a vector database (ChromaDB), and uses an LLM to answer new forum posts by retrieving relevant past solutions.

High-level flow
- `bot.py` boots the bot, loads extensions, and listens for forum thread events.
- Cogs (in `cogs/`) implement commands and the thread-processing logic.
- `cogs/commands.py` exposes admin slash commands: set forum channel and `scan_forum` which summarizes threads and indexes them.
- `cogs/ai_chat.py` contains LLM agents: summarizer, query optimizer, and response agent.
- `vector_database/` holds the ChromaDB helper to add/retrieve summaries.
- `database/` holds SQL helpers for storing guild configuration and verification.

Repository layout
- `bot.py` — entrypoint. Loads environment, initializes DB, registers cogs, and handles `on_thread_create`.
- `cogs/` — Discord extension modules:
  - `commands.py` — slash commands for admins and the scanning loop.
  - `ai_chat.py` — LLM agent wrappers and helper functions (`get_response`, `get_summerization`, `generate_search_query`).
- `vector_database/vector_db.py` — adapter code for ChromaDB operations: `add_text_to_chromadb`, `retrieve_memory`.
- `database/sql.py` — local sqlite helpers (init DB, store/get forum channel, guild verification).
- `img/` — screenshots used in the README.
- `requirements.txt` & `pyproject.toml` — dependency manifests (both present; prefer using one workflow and a lockfile for reproducible installs).
- `chroma_db/` — local chroma sqlite DB and collection data.

Important files to read first
- `bot.py` — to understand lifecycle and event handlers.
- `cogs/commands.py` — for the scanning flow and Discord API usage.
- `cogs/ai_chat.py` — shows which LLMs are used, how prompts are composed.
- `vector_database/vector_db.py` — how documents are indexed and queried.

Environment variables
- `BOT_TOKEN` — Discord bot token. Required to run the bot.
- `GEMINI_API_KEY` (or other provider keys) — LLM provider key used by `pydantic_ai` Agents. `cogs/ai_chat.py` raises if missing.
- Additional variables may be used by downstream libs (e.g., Google creds). Keep secrets out of the repo and provide a `.env.example` for clients.

How the main pieces interact
1. Admin runs `/set_up_forum` to store a forum channel ID in the sqlite DB.
2. `/scan_forum` collects thread messages, runs `get_summerization()` (LLM), and calls `add_text_to_chromadb(thread_id, summary)`.
3. On new thread creation (`on_thread_create` in `bot.py`):
   - Compose a search-friendly query using `generate_search_query()` (LLM).
   - Call `retrieve_memory(query)` to get past summaries.
   - Call `get_response(query, memories)` to get a final LLM answer and post it in the thread.

Developer notes for other AIs
- Imports: code uses `pydantic_ai.Agent` wrappers — each Agent is run asynchronously (use `await agent.run(...)`).
- Fail-fast behavior: `cogs/ai_chat.py` currently raises if `GEMINI_API_KEY` is missing; consider graceful degradation if keys are unavailable.
- Rate limiting: Discord calls are mostly paginated/async; the scanner uses a small `asyncio.sleep(0.3)` between thread inserts. Add retry/backoff around network/LLM calls.
- DB files: `chroma_db/chroma.sqlite3` and `database` sqlite are local; avoid committing them and include them in `.gitignore`.

Running the project (local quickstart)
1. Create a virtual environment (Python 3.13+ by current `pyproject.toml` requirement or adjust lower):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` with required variables (example shown below) and ensure it's in `.gitignore`:

```
BOT_TOKEN=your_discord_token
GEMINI_API_KEY=your_gemini_or_llm_key
```

3. Initialize DB (the project calls `init_db()` on import). If a manual step is required, run the helper from `database/sql.py`.
4. Run the bot:

```bash
python bot.py
```

Security and freelancing recommendations
- Add `.env.example` and ensure `.gitignore` explicitly excludes `.env`, `chroma_db/`, and sqlite DBs before publishing.
- Replace `print()` calls with `logging` and a config-friendly logger.
- Do not raise on missing API keys at import time; instead, warn and disable LLM features for safer local testing.

Extending the project
- Add tests for `database/sql.py` and `vector_database/vector_db.py` to validate DB and indexing logic.
- Add a `Dockerfile` and `docker-compose.yml` for easier client deployments.
- Add CI (GitHub Actions) to run linting, type checks, and tests on PRs.

Contact / Author
- Original author: Renerfia (see README)

---
If you want, I can: add a `.env.example`, switch prints to `logging`, or create a short `USAGE.md` targeted at clients. Tell me which to do next.
