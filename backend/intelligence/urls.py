from rest_framework.routers import DefaultRouter

from .views import AnalysisRunViewSet, EarningsBriefViewSet, TickerViewSet

router = DefaultRouter()
router.register("tickers", TickerViewSet, basename="ticker")
router.register("briefs", EarningsBriefViewSet, basename="brief")
router.register("analysis-runs", AnalysisRunViewSet, basename="analysis-run")

urlpatterns = router.urls
