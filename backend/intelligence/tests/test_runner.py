from unittest.mock import MagicMock, patch

from django.test import TestCase

from intelligence.models import EarningsBrief, Ticker
from intelligence.services.runner import analyze_ticker

from .factories import make_brief_data


class AnalyzeTickerTests(TestCase):
    @patch("intelligence.services.runner.build_graph")
    def test_creates_ticker_and_persists_brief(self, mock_build_graph):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"brief": make_brief_data("AAPL"), "errors": []}
        mock_build_graph.return_value = mock_graph

        brief = analyze_ticker("aapl")

        self.assertEqual(Ticker.objects.get().symbol, "AAPL")
        self.assertEqual(EarningsBrief.objects.count(), 1)
        self.assertEqual(brief.overall_rating, "Buy")
        self.assertEqual(brief.ticker.symbol, "AAPL")

    @patch("intelligence.services.runner.build_graph")
    def test_reuses_existing_ticker(self, mock_build_graph):
        Ticker.objects.create(symbol="AAPL", company_name="Apple Inc.")
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"brief": make_brief_data("AAPL"), "errors": []}
        mock_build_graph.return_value = mock_graph

        analyze_ticker("AAPL")

        self.assertEqual(Ticker.objects.count(), 1)

    @patch("intelligence.services.runner.build_graph")
    def test_raises_when_no_brief_produced(self, mock_build_graph):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"brief": None, "errors": ["search failed"]}
        mock_build_graph.return_value = mock_graph

        with self.assertRaises(RuntimeError):
            analyze_ticker("AAPL")

        self.assertEqual(EarningsBrief.objects.count(), 0)
