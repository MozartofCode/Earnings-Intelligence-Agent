from django.test import TestCase

from intelligence.models import AnalysisRun, EarningsBrief, Ticker

from .factories import make_brief_data


class TickerModelTests(TestCase):
    def test_str_is_symbol(self):
        ticker = Ticker.objects.create(symbol="AAPL")
        self.assertEqual(str(ticker), "AAPL")

    def test_ordering_is_alphabetical(self):
        Ticker.objects.create(symbol="MSFT")
        Ticker.objects.create(symbol="AAPL")
        Ticker.objects.create(symbol="NVDA")
        self.assertEqual(list(Ticker.objects.values_list("symbol", flat=True)), ["AAPL", "MSFT", "NVDA"])


class EarningsBriefModelTests(TestCase):
    def test_str_includes_ticker_and_period(self):
        ticker = Ticker.objects.create(symbol="AAPL")
        brief = EarningsBrief.objects.create(ticker=ticker, **{k: v for k, v in make_brief_data().items() if k != "ticker"})
        self.assertEqual(str(brief), "AAPL — FY2025")

    def test_ordering_is_newest_first(self):
        ticker = Ticker.objects.create(symbol="AAPL")
        data = {k: v for k, v in make_brief_data().items() if k != "ticker"}
        older = EarningsBrief.objects.create(ticker=ticker, **{**data, "period": "FY2024"})
        newer = EarningsBrief.objects.create(ticker=ticker, **{**data, "period": "FY2025"})
        self.assertEqual(list(EarningsBrief.objects.all()), [newer, older])


class AnalysisRunModelTests(TestCase):
    def test_defaults_to_pending(self):
        ticker = Ticker.objects.create(symbol="AAPL")
        run = AnalysisRun.objects.create(ticker=ticker)
        self.assertEqual(run.status, AnalysisRun.Status.PENDING)
        self.assertEqual(str(run), "AAPL — pending")

    def test_deleting_ticker_cascades(self):
        ticker = Ticker.objects.create(symbol="AAPL")
        AnalysisRun.objects.create(ticker=ticker)
        ticker.delete()
        self.assertEqual(AnalysisRun.objects.count(), 0)

    def test_deleting_brief_nulls_out_run(self):
        ticker = Ticker.objects.create(symbol="AAPL")
        data = {k: v for k, v in make_brief_data().items() if k != "ticker"}
        brief = EarningsBrief.objects.create(ticker=ticker, **data)
        run = AnalysisRun.objects.create(ticker=ticker, status=AnalysisRun.Status.SUCCESS, brief=brief)

        brief.delete()
        run.refresh_from_db()
        self.assertIsNone(run.brief)
