"""Shared test fixtures — a fake EarningsBrief payload matching the shape
the agent's structured output (output_schema.EarningsBrief) produces.
"""


def make_brief_data(ticker: str = "AAPL") -> dict:
    return {
        "ticker": ticker,
        "company_name": "Test Company Inc.",
        "period": "FY2025",
        "business_summary": "A company that makes things.",
        "revenue_model": "Sells things for money.",
        "key_metrics": {"revenue": "$10B", "net_income": "$2B"},
        "quarter_vs_prior": "Revenue grew 5% sequentially.",
        "bull_thesis": {
            "argument": "Growth is accelerating.",
            "supporting_facts": ["Fact one.", "Fact two."],
        },
        "bear_thesis": {
            "argument": "Margins are under pressure.",
            "supporting_facts": ["Fact three.", "Fact four."],
        },
        "key_risks": [
            {"category": "Competitive", "description": "New entrants.", "severity": "Medium"},
        ],
        "management_sentiment": "positive",
        "management_sentiment_evidence": "CEO said growth remains strong.",
        "red_flags": ["Rising inventory."],
        "analyst_consensus": "Buy",
        "price_targets": "$150",
        "overall_rating": "Buy",
        "one_line_summary": "Solid quarter with strong growth.",
    }
