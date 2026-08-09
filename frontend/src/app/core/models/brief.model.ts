export interface Thesis {
  argument: string;
  supporting_facts: string[];
}

export interface Risk {
  category: string;
  description: string;
  severity: string;
}

export type Sentiment = 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative';

export interface EarningsBrief {
  id: number;
  ticker: string;
  company_name: string;
  period: string;
  business_summary: string;
  revenue_model: string;
  key_metrics: Record<string, unknown>;
  quarter_vs_prior: string;
  bull_thesis: Thesis;
  bear_thesis: Thesis;
  key_risks: Risk[];
  management_sentiment: Sentiment;
  management_sentiment_evidence: string;
  red_flags: string[];
  analyst_consensus: string | null;
  price_targets: string | null;
  overall_rating: string;
  one_line_summary: string;
  created_at: string;
}
