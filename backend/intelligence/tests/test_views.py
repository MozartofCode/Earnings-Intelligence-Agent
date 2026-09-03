from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from intelligence.models import AnalysisRun, EarningsBrief, Ticker

from .factories import make_brief_data


class TickerViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_list_is_empty_initially(self):
        response = self.client.get("/api/tickers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_create_uppercases_symbol(self):
        response = self.client.post("/api/tickers/", {"symbol": "aapl"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["symbol"], "AAPL")

    def test_delete_removes_ticker(self):
        Ticker.objects.create(symbol="AAPL")
        response = self.client.delete("/api/tickers/AAPL/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ticker.objects.count(), 0)

    def test_analyze_missing_ticker_404s(self):
        response = self.client.post("/api/tickers/NOPE/analyze/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("intelligence.views.run_agent_analysis")
    def test_analyze_enqueues_task_and_returns_pending_run(self, mock_task):
        Ticker.objects.create(symbol="AAPL")

        response = self.client.post("/api/tickers/AAPL/analyze/")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        data = response.json()
        self.assertEqual(data["status"], AnalysisRun.Status.PENDING)
        self.assertEqual(data["ticker"], "AAPL")
        self.assertIsNone(data["brief"])

        run = AnalysisRun.objects.get(id=data["id"])
        mock_task.delay.assert_called_once_with(run.id)


class EarningsBriefViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aapl = Ticker.objects.create(symbol="AAPL")
        self.msft = Ticker.objects.create(symbol="MSFT")
        data = {k: v for k, v in make_brief_data().items() if k != "ticker"}
        EarningsBrief.objects.create(ticker=self.aapl, **data)
        EarningsBrief.objects.create(ticker=self.msft, **data)

    def test_list_returns_all_briefs(self):
        response = self.client.get("/api/briefs/")
        self.assertEqual(len(response.json()), 2)

    def test_filters_by_ticker(self):
        response = self.client.get("/api/briefs/?ticker=aapl")
        results = response.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ticker"], "AAPL")

    def test_is_read_only(self):
        response = self.client.post("/api/briefs/", {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AnalysisRunViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ticker = Ticker.objects.create(symbol="AAPL")

    def test_retrieve_pending_run(self):
        run = AnalysisRun.objects.create(ticker=self.ticker)
        response = self.client.get(f"/api/analysis-runs/{run.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "pending")

    def test_filters_by_ticker(self):
        other = Ticker.objects.create(symbol="MSFT")
        AnalysisRun.objects.create(ticker=self.ticker)
        AnalysisRun.objects.create(ticker=other)

        response = self.client.get("/api/analysis-runs/?ticker=AAPL")
        results = response.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ticker"], "AAPL")

    def test_run_includes_brief_once_succeeded(self):
        data = {k: v for k, v in make_brief_data().items() if k != "ticker"}
        brief = EarningsBrief.objects.create(ticker=self.ticker, **data)
        run = AnalysisRun.objects.create(
            ticker=self.ticker, status=AnalysisRun.Status.SUCCESS, brief=brief
        )

        response = self.client.get(f"/api/analysis-runs/{run.id}/")
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["brief"]["overall_rating"], "Buy")


class AnalyzeThrottleTests(TestCase):
    """Exercises the real configured ANALYZE_THROTTLE_RATE rather than
    overriding it: DRF's SimpleRateThrottle binds THROTTLE_RATES as a class
    attribute at import time, so override_settings(REST_FRAMEWORK=...) does
    not reach an already-imported throttle class.
    """

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        Ticker.objects.create(symbol="AAPL")

    @patch("intelligence.views.run_agent_analysis")
    def test_requests_beyond_the_configured_rate_are_throttled(self, mock_task):
        from rest_framework.throttling import ScopedRateThrottle

        num_requests, _ = ScopedRateThrottle().parse_rate(
            ScopedRateThrottle.THROTTLE_RATES["analyze"]
        )

        responses = [
            self.client.post("/api/tickers/AAPL/analyze/") for _ in range(num_requests + 1)
        ]

        self.assertTrue(all(r.status_code == status.HTTP_202_ACCEPTED for r in responses[:-1]))
        self.assertEqual(responses[-1].status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class ApiTokenPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch.dict("os.environ", {"API_AUTH_TOKEN": "secret123"})
    def test_unsafe_request_without_token_is_rejected(self):
        response = self.client.post("/api/tickers/", {"symbol": "AAPL"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.dict("os.environ", {"API_AUTH_TOKEN": "secret123"})
    def test_unsafe_request_with_token_is_allowed(self):
        response = self.client.post(
            "/api/tickers/", {"symbol": "AAPL"}, HTTP_AUTHORIZATION="Token secret123"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch.dict("os.environ", {"API_AUTH_TOKEN": "secret123"})
    def test_safe_request_never_needs_token(self):
        response = self.client.get("/api/tickers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_token_configured_means_open(self):
        response = self.client.post("/api/tickers/", {"symbol": "AAPL"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
