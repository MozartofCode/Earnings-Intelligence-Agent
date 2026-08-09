from django.contrib import admin

from .models import EarningsBrief, Ticker


@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ("symbol", "company_name", "added_at")
    search_fields = ("symbol", "company_name")


@admin.register(EarningsBrief)
class EarningsBriefAdmin(admin.ModelAdmin):
    list_display = ("ticker", "period", "overall_rating", "management_sentiment", "created_at")
    list_filter = ("overall_rating", "management_sentiment")
    search_fields = ("ticker__symbol", "period")
