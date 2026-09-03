"""Manual entry point for running the agent across the configured watchlist.

Usage: python manage.py run_watchlist

For scheduled runs, prefer the Celery Beat periodic task
(intelligence.tasks.run_watchlist_task, wired up via CELERY_BEAT_SCHEDULE in
config/settings.py) — this command remains as a manual/cron-friendly
alternative that doesn't require a running Celery worker.
"""

import os

from django.core.management.base import BaseCommand

from intelligence.services.runner import analyze_ticker


class Command(BaseCommand):
    help = "Run the earnings intelligence agent across the WATCHLIST env var tickers."

    def handle(self, *args, **options):
        watchlist = os.getenv("WATCHLIST", "").split(",")
        watchlist = [t.strip().upper() for t in watchlist if t.strip()]

        if not watchlist:
            self.stdout.write(self.style.WARNING("WATCHLIST env var is empty — nothing to run."))
            return

        for symbol in watchlist:
            self.stdout.write(f"Running agent for {symbol}...")
            try:
                analyze_ticker(symbol)
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"{symbol}: agent run failed: {exc}"))
                continue
            self.stdout.write(self.style.SUCCESS(f"{symbol}: brief saved."))
