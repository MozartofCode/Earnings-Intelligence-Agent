from rest_framework.routers import DefaultRouter

from .views import EarningsBriefViewSet, TickerViewSet

router = DefaultRouter()
router.register("tickers", TickerViewSet, basename="ticker")
router.register("briefs", EarningsBriefViewSet, basename="brief")

urlpatterns = router.urls
