# Earnings Intelligence Agent

An autonomous agent that accepts a stock ticker, collects 10-K/10-Q filings from SEC
EDGAR, earnings call transcripts, and analyst reports, and produces a structured
investment brief (bull/bear thesis, risk scores, management sentiment, red flags).

- **Backend**: Django + Django REST Framework
- **Frontend**: Angular
- **Agent**: LangGraph (see below)
- **Async**: Celery + Redis back the `/analyze` endpoint and scheduled watchlist runs
- **Database**: SQLite locally, swappable to Postgres/AWS RDS via `DATABASE_URL`

## Project layout

```
backend/    Django project (config/) + intelligence app (models, DRF API, agent, Celery tasks)
frontend/   Angular app (watchlist + brief-detail pages)
```

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Analysis runs go through Celery, so `/analyze` needs a broker and a worker
running too (see [Async task queue](#async-task-queue) below) — otherwise the
endpoint will accept the request but nothing will ever process it.

API available at `http://localhost:8000/api/`:

- `GET/POST /api/tickers/` — list / add tickers
- `DELETE /api/tickers/{symbol}/` — remove a ticker
- `POST /api/tickers/{symbol}/analyze/` — enqueue an agent run for this ticker;
  returns `202` with an `AnalysisRun` (`status: "pending"`)
- `GET /api/analysis-runs/{id}/` — poll a run's status (`pending` → `running` →
  `success`/`failed`); carries the finished `brief` once `success`
- `GET /api/analysis-runs/?ticker=SYMBOL` — a ticker's runs, newest first
- `GET /api/briefs/` — list briefs (optionally `?ticker=SYMBOL`)
- `GET /api/briefs/{id}/` — retrieve one brief

Run the test suite (mocks the LLM/SEC/web calls, so it needs no API keys or
network access):

```bash
python manage.py test intelligence
```

## Frontend setup

```bash
cd frontend
npm install
npx ng serve
```

Open `http://localhost:4200`. The dev environment (`src/environments/environment.development.ts`)
points at `http://localhost:8000/api`.

## The agent

`backend/intelligence/services/agent/` contains the LangGraph agent:

- `output_schema.py` — the Pydantic `EarningsBrief` schema shared between the
  agent and the Django API/models.
- `tools.py` — SEC EDGAR tools (`get_sec_filings`, `fetch_filing_text`) plus
  web search tools (`search_earnings_transcript`, `search_analyst_reports`,
  `search_company_news`) via `ddgs` (default, no key) or Tavily
  (`SEARCH_PROVIDER=tavily` + `TAVILY_API_KEY`).
- `retriever.py` — a Chroma-backed `ParentDocumentRetriever` (400-token child
  chunks for matching, 2000-token parent chunks for context) with
  `all-MiniLM-L6-v2` embeddings, plus `multi_query_retrieve` which runs several
  targeted queries and dedupes the results into one context string.
- `graph.py` — the LangGraph state machine: `collect_data` (LLM decides which
  tools to call) ⇄ `execute_tools`, looping until the LLM stops requesting
  tools (capped at `MAX_COLLECT_ROUNDS`), then `rag` → `generate_brief`
  (`llm.with_structured_output(EarningsBrief)`).

`intelligence/services/runner.py`'s `analyze_ticker(symbol)` runs the graph and
persists the result as an `intelligence.models.EarningsBrief` row — it's the
one place that logic lives, shared by the async task, the management command,
and the tests.

Set `LLM_PROVIDER` (`groq` or `anthropic`) and the matching API key, and
`EDGAR_USER_AGENT` to a descriptive string identifying your app (SEC EDGAR
requires this), then (with Redis + a Celery worker running, see below):

```bash
python manage.py runserver
curl -X POST http://localhost:8000/api/tickers/AAPL/analyze/
# -> 202 {"id": 1, "status": "pending", ...}
curl http://localhost:8000/api/analysis-runs/1/
# -> poll until "status": "success" (or "failed"), then it carries "brief"
```

## Async task queue

`POST /analyze` enqueues a Celery task (`intelligence.tasks.run_agent_analysis`)
instead of blocking on the agent run — the request returns immediately with a
pending `AnalysisRun` to poll. This needs Redis (the default broker/result
backend) and a running worker:

```bash
redis-server
celery -A config worker -l info
```

For scheduled watchlist runs, run Celery Beat too — it fires
`intelligence.tasks.run_watchlist_task` on the schedule in
`CELERY_BEAT_SCHEDULE` (`config/settings.py`, configurable via the
`WATCHLIST_SCHEDULE_*` env vars, default: Monday mornings):

```bash
celery -A config beat -l info
```

`python manage.py run_watchlist` remains as a synchronous, cron-friendly
alternative that needs no Celery worker.

No Redis handy for quick local testing? Set `CELERY_TASK_ALWAYS_EAGER=True` in
`.env` to run tasks synchronously in-process — `/analyze` will block again,
but nothing else needs to run.

## API protection

Two env vars, both no-ops by default so local dev and the bundled frontend
work unchanged:

- `ANALYZE_THROTTLE_RATE` (default `10/hour`) — caps calls to `/analyze` per
  client, since each one triggers billed LLM calls.
- `API_AUTH_TOKEN` — if set, unsafe requests (`POST`/`DELETE`) must send
  `Authorization: Token <value>`; `GET` stays open either way. Set this before
  exposing the API beyond localhost — the frontend doesn't send this header,
  so leave it unset while using the bundled UI.

## Deployment (later)

Not scaffolded yet — planned: Postgres on AWS RDS (just set `DATABASE_URL`),
Django + Angular deployed to AWS, managed Redis for Celery.
