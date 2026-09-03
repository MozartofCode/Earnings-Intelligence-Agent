import logging
import os

from celery import shared_task

from .models import AnalysisRun
from .services.runner import analyze_ticker

logger = logging.getLogger(__name__)


@shared_task
def run_agent_analysis(run_id: int) -> None:
    """Celery task backing the async /analyze endpoint. Runs the agent for
    the run's ticker and updates the AnalysisRun row with the outcome.
    """
    run = AnalysisRun.objects.select_related("ticker").get(id=run_id)
    run.status = AnalysisRun.Status.RUNNING
    run.save(update_fields=["status", "updated_at"])

    try:
        brief = analyze_ticker(run.ticker.symbol)
    except Exception as exc:
        logger.exception("Agent run failed for %s", run.ticker.symbol)
        run.status = AnalysisRun.Status.FAILED
        run.error = str(exc)
        run.save(update_fields=["status", "error", "updated_at"])
        return

    run.status = AnalysisRun.Status.SUCCESS
    run.brief = brief
    run.save(update_fields=["status", "brief", "updated_at"])


@shared_task
def run_watchlist_task() -> None:
    """Periodic task (wire up via CELERY_BEAT_SCHEDULE) that runs the agent
    for every ticker in the WATCHLIST env var, same as `manage.py run_watchlist`.
    """
    watchlist = [t.strip().upper() for t in os.getenv("WATCHLIST", "").split(",") if t.strip()]
    for symbol in watchlist:
        try:
            analyze_ticker(symbol)
        except Exception:
            logger.exception("Watchlist run failed for %s", symbol)
