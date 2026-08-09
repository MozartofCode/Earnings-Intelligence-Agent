# Earnings Intelligence Agent

An autonomous agent that accepts a stock ticker, collects 10-K/10-Q filings from SEC
EDGAR, earnings call transcripts, and analyst reports, and produces a structured
investment brief (bull/bear thesis, risk scores, management sentiment, red flags).

- **Backend**: Django + Django REST Framework
- **Frontend**: Angular
- **Agent**: LangGraph — **intentionally left unimplemented** (see below)
- **Database**: SQLite locally, swappable to Postgres/AWS RDS via `DATABASE_URL`

## Project layout

```
backend/    Django project (config/) + intelligence app (models, DRF API, agent stubs)
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

API available at `http://localhost:8000/api/`:

- `GET/POST /api/tickers/` — list / add tickers
- `DELETE /api/tickers/{symbol}/` — remove a ticker
- `POST /api/tickers/{symbol}/analyze/` — trigger an agent run (501 until the agent is implemented)
- `GET /api/briefs/` — list briefs (optionally `?ticker=SYMBOL`)
- `GET /api/briefs/{id}/` — retrieve one brief

## Frontend setup

```bash
cd frontend
npm install
npx ng serve
```

Open `http://localhost:4200`. The dev environment (`src/environments/environment.development.ts`)
points at `http://localhost:8000/api`.

## The agent — build this yourself

`backend/intelligence/services/agent/` contains the LangGraph agent scaffolding,
intentionally left as stubs:

- `output_schema.py` — **implemented**. The Pydantic `EarningsBrief` schema shared
  between the agent and the Django API/models.
- `graph.py` — stub. Intended LangGraph state machine (`collect_data` →
  `execute_tools` → `rag` → `generate_brief`) is documented in the module docstring.
- `tools.py` — stub. Intended SEC EDGAR + web search tools are documented in the
  module docstring.
- `retriever.py` — stub. Intended Chroma/ParentDocumentRetriever RAG layer is
  documented in the module docstring.

`intelligence/views.py`'s `TickerViewSet.analyze` action already calls
`graph.build_graph()` and returns its `NotImplementedError` as an HTTP 501 — once
`build_graph()` is implemented, wire the returned brief into an
`intelligence.models.EarningsBrief` row there (or inside `graph.py`).

`requirements.txt` already lists the agent dependencies (LangChain, LangGraph,
langchain-anthropic, ChromaDB, sentence-transformers, search provider SDKs) so
`pip install -r requirements.txt` leaves you ready to start.

`python manage.py run_watchlist` is a management-command placeholder for running
the agent across the tickers in the `WATCHLIST` env var — it's a manual entry
point for now; wire it into a scheduler (Celery beat, cron, AWS EventBridge, etc.)
at deploy time.

## Deployment (later)

Not scaffolded yet — planned: Postgres on AWS RDS (just set `DATABASE_URL`),
Django + Angular deployed to AWS.
