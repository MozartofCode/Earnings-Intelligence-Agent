"""Shared helper that runs the agent for a ticker and persists the brief.

Used by the synchronous management command (run_watchlist), the Celery task
that backs the async /analyze endpoint (intelligence/tasks.py), and tests.
"""

from ..models import EarningsBrief, Ticker
from .agent.graph import build_graph


def analyze_ticker(symbol: str) -> EarningsBrief:
    """Run the agent for `symbol` and persist the resulting EarningsBrief.

    Raises RuntimeError if the agent run completes without producing a brief.
    """
    ticker, _ = Ticker.objects.get_or_create(symbol=symbol.upper())
    graph = build_graph()

    result = graph.invoke(
        {
            "ticker": ticker.symbol,
            "messages": [],
            "raw_documents": [],
            "retrieved_context": "",
            "brief": None,
            "errors": [],
        }
    )

    brief_data = result.get("brief")
    if not brief_data:
        raise RuntimeError(
            f"Agent run for {symbol} produced no brief. Errors: {result.get('errors')}"
        )

    return EarningsBrief.objects.create(
        ticker=ticker,
        company_name=brief_data["company_name"],
        period=brief_data["period"],
        business_summary=brief_data["business_summary"],
        revenue_model=brief_data["revenue_model"],
        key_metrics=brief_data["key_metrics"],
        quarter_vs_prior=brief_data["quarter_vs_prior"],
        bull_thesis=brief_data["bull_thesis"],
        bear_thesis=brief_data["bear_thesis"],
        key_risks=brief_data["key_risks"],
        management_sentiment=brief_data["management_sentiment"],
        management_sentiment_evidence=brief_data["management_sentiment_evidence"],
        red_flags=brief_data["red_flags"],
        analyst_consensus=brief_data.get("analyst_consensus"),
        price_targets=brief_data.get("price_targets"),
        overall_rating=brief_data["overall_rating"],
        one_line_summary=brief_data["one_line_summary"],
    )
