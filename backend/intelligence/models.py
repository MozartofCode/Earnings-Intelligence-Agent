from django.db import models


class Ticker(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=255, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["symbol"]

    def __str__(self):
        return self.symbol


class EarningsBrief(models.Model):
    """Mirrors the agent's EarningsBrief Pydantic schema (see
    intelligence/services/agent/output_schema.py). Nested structures
    (thesis, risks, key metrics) are stored as JSON since their shape is
    already validated by that schema before a brief is saved.
    """

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="briefs")
    company_name = models.CharField(max_length=255)
    period = models.CharField(max_length=50)

    business_summary = models.TextField()
    revenue_model = models.TextField()
    key_metrics = models.JSONField(default=dict)
    quarter_vs_prior = models.TextField()

    bull_thesis = models.JSONField(default=dict)
    bear_thesis = models.JSONField(default=dict)

    key_risks = models.JSONField(default=list)
    management_sentiment = models.CharField(max_length=20)
    management_sentiment_evidence = models.TextField()

    red_flags = models.JSONField(default=list)

    analyst_consensus = models.TextField(blank=True, null=True)
    price_targets = models.CharField(max_length=255, blank=True, null=True)

    overall_rating = models.CharField(max_length=20)
    one_line_summary = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticker.symbol} — {self.period}"
