from rest_framework import serializers

from .models import EarningsBrief, Ticker


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        fields = ["id", "symbol", "company_name", "added_at"]
        read_only_fields = ["id", "added_at"]

    def validate_symbol(self, value):
        return value.upper()


class EarningsBriefSerializer(serializers.ModelSerializer):
    ticker = serializers.SlugRelatedField(slug_field="symbol", read_only=True)

    class Meta:
        model = EarningsBrief
        fields = [
            "id",
            "ticker",
            "company_name",
            "period",
            "business_summary",
            "revenue_model",
            "key_metrics",
            "quarter_vs_prior",
            "bull_thesis",
            "bear_thesis",
            "key_risks",
            "management_sentiment",
            "management_sentiment_evidence",
            "red_flags",
            "analyst_consensus",
            "price_targets",
            "overall_rating",
            "one_line_summary",
            "created_at",
        ]
        read_only_fields = fields
