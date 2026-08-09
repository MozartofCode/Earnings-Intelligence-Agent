"""Manual entry point for running the agent across the configured watchlist.

Usage: python manage.py run_watchlist

Placeholder for weekly/cron scheduling (APScheduler, Celery beat, or AWS
EventBridge) to be added later at deploy time. For now this just calls the
(stubbed) agent directly for each ticker in the WATCHLIST env var.
"""

import os

from django.core.management.base import BaseCommand

from intelligence.services.agent.graph import build_graph


class Command(BaseCommand):
    help = "Run the earnings intelligence agent across the WATCHLIST env var tickers."

    def handle(self, *args, **options):
        watchlist = os.getenv("WATCHLIST", "").split(",")
        watchlist = [t.strip().upper() for t in watchlist if t.strip()]

        if not watchlist:
            self.stdout.write(self.style.WARNING("WATCHLIST env var is empty — nothing to run."))
            return

        for ticker in watchlist:
            self.stdout.write(f"Running agent for {ticker}...")
            try:
                build_graph()
            except NotImplementedError as exc:
                self.stdout.write(self.style.ERROR(f"{ticker}: {exc}"))
