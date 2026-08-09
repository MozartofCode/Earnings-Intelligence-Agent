from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EarningsBrief, Ticker
from .serializers import EarningsBriefSerializer, TickerSerializer


class TickerViewSet(viewsets.ModelViewSet):
    queryset = Ticker.objects.all()
    serializer_class = TickerSerializer
    lookup_field = "symbol"
    http_method_names = ["get", "post", "delete"]

    @action(detail=True, methods=["post"])
    def analyze(self, request, symbol=None):
        """Trigger an agent run for this ticker.

        Delegates to the (currently stubbed) LangGraph agent in
        intelligence/services/agent/graph.py. Returns 501 until that
        module is implemented.
        """
        ticker = get_object_or_404(Ticker, symbol=symbol.upper())

        from .services.agent.graph import build_graph

        try:
            build_graph()
        except NotImplementedError as exc:
            return Response(
                {"detail": str(exc), "ticker": ticker.symbol},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        return Response(
            {"detail": "Agent run not yet wired up to persist a brief."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class EarningsBriefViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EarningsBrief.objects.select_related("ticker").all()
    serializer_class = EarningsBriefSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("ticker")
        if symbol:
            queryset = queryset.filter(ticker__symbol=symbol.upper())
        return queryset
