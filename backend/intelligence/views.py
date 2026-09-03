from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import AnalysisRun, EarningsBrief, Ticker
from .serializers import AnalysisRunSerializer, EarningsBriefSerializer, TickerSerializer
from .tasks import run_agent_analysis


class TickerViewSet(viewsets.ModelViewSet):
    queryset = Ticker.objects.all()
    serializer_class = TickerSerializer
    lookup_field = "symbol"
    http_method_names = ["get", "post", "delete"]

    def get_throttles(self):
        if self.action == "analyze":
            self.throttle_scope = "analyze"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    @action(detail=True, methods=["post"])
    def analyze(self, request, symbol=None):
        """Enqueue an async agent run for this ticker.

        The actual work (LLM calls, SEC/web fetches) happens in a Celery task
        (intelligence.tasks.run_agent_analysis) so this returns immediately.
        Poll GET /api/analysis-runs/{id}/ for status; it carries the finished
        brief once status is "success".
        """
        ticker = get_object_or_404(Ticker, symbol=symbol.upper())

        run = AnalysisRun.objects.create(ticker=ticker)
        run_agent_analysis.delay(run.id)

        serializer = AnalysisRunSerializer(run)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class EarningsBriefViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EarningsBrief.objects.select_related("ticker").all()
    serializer_class = EarningsBriefSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("ticker")
        if symbol:
            queryset = queryset.filter(ticker__symbol=symbol.upper())
        return queryset


class AnalysisRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only: poll here for the status of a run started via
    POST /api/tickers/{symbol}/analyze/.
    """

    queryset = AnalysisRun.objects.select_related("ticker", "brief").all()
    serializer_class = AnalysisRunSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("ticker")
        if symbol:
            queryset = queryset.filter(ticker__symbol=symbol.upper())
        return queryset
