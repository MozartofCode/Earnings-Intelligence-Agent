from unittest.mock import patch

from django.test import TestCase, override_settings

from intelligence.models import AnalysisRun, EarningsBrief, Ticker
from intelligence.tasks import run_agent_analysis, run_watchlist_task

from .factories import make_brief_data


class RunAgentAnalysisTaskTests(TestCase):
    def setUp(self):
        self.ticker = Ticker.objects.create(symbol="AAPL")
        self.run = AnalysisRun.objects.create(ticker=self.ticker)

    @patch("intelligence.tasks.analyze_ticker")
    def test_success_updates_run_and_attaches_brief(self, mock_analyze_ticker):
        data = {k: v for k, v in make_brief_data().items() if k != "ticker"}
        brief = EarningsBrief.objects.create(ticker=self.ticker, **data)
        mock_analyze_ticker.return_value = brief

        run_agent_analysis(self.run.id)

        self.run.refresh_from_db()
        self.assertEqual(self.run.status, AnalysisRun.Status.SUCCESS)
        self.assertEqual(self.run.brief, brief)
        self.assertEqual(self.run.error, "")

    @patch("intelligence.tasks.analyze_ticker")
    def test_failure_marks_run_failed_with_error(self, mock_analyze_ticker):
        mock_analyze_ticker.side_effect = RuntimeError("agent blew up")

        run_agent_analysis(self.run.id)

        self.run.refresh_from_db()
        self.assertEqual(self.run.status, AnalysisRun.Status.FAILED)
        self.assertIn("agent blew up", self.run.error)
        self.assertIsNone(self.run.brief)


class RunWatchlistTaskTests(TestCase):
    @override_settings()
    @patch("intelligence.tasks.analyze_ticker")
    @patch.dict("os.environ", {"WATCHLIST": "AAPL, msft"})
    def test_runs_agent_for_each_watchlist_ticker(self, mock_analyze_ticker):
        run_watchlist_task()

        called_symbols = [call.args[0] for call in mock_analyze_ticker.call_args_list]
        self.assertEqual(called_symbols, ["AAPL", "MSFT"])

    @patch("intelligence.tasks.analyze_ticker")
    @patch.dict("os.environ", {"WATCHLIST": "AAPL,MSFT"})
    def test_continues_after_one_ticker_fails(self, mock_analyze_ticker):
        mock_analyze_ticker.side_effect = [RuntimeError("boom"), None]

        run_watchlist_task()

        self.assertEqual(mock_analyze_ticker.call_count, 2)

    @patch("intelligence.tasks.analyze_ticker")
    @patch.dict("os.environ", {"WATCHLIST": ""})
    def test_empty_watchlist_is_a_noop(self, mock_analyze_ticker):
        run_watchlist_task()
        mock_analyze_ticker.assert_not_called()
