"""Structured output contract for a completed earnings brief.

This is the Pydantic schema the LangGraph agent (graph.py) must produce via
`llm.with_structured_output(EarningsBrief)`. It's implemented (not a stub)
because the Django API/serializers and the agent both need to agree on this
shape — EarningsBrief here should stay in sync with
intelligence.models.EarningsBrief.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class Risk(BaseModel):
    category: str = Field(description="e.g. Competitive, Regulatory, Macro, Execution")
    description: str = Field(description="Plain-English description of the specific risk")
    severity: str = Field(description="Low / Medium / High")


class Thesis(BaseModel):
    argument: str = Field(description="Core one-sentence argument")
    supporting_facts: List[str] = Field(description="3-5 specific, data-backed bullet points")


class EarningsBrief(BaseModel):
    ticker: str
    company_name: str
    period: str = Field(description="e.g. FY2024 or Q3 2024")

    business_summary: str = Field(description="2-3 sentence plain-English business description")
    revenue_model: str = Field(description="How the company actually makes money")

    key_metrics: dict = Field(description="Revenue, net income, margins, YoY growth rates")
    quarter_vs_prior: str = Field(description="Key changes vs prior quarter in plain English")

    bull_thesis: Thesis
    bear_thesis: Thesis

    key_risks: List[Risk]
    management_sentiment: Sentiment
    management_sentiment_evidence: str = Field(
        description="Specific quote or data point from the earnings call justifying the score"
    )

    red_flags: List[str] = Field(
        description="Concrete concerns pulled from filings — not generic warnings"
    )

    analyst_consensus: Optional[str] = Field(default=None)
    price_targets: Optional[str] = Field(default=None)

    overall_rating: str = Field(description="Strong Buy / Buy / Hold / Sell / Strong Sell")
    one_line_summary: str = Field(description="One sentence capturing the essential story")
