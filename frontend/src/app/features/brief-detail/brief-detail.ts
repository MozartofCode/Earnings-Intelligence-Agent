import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../../core/services/api.service';
import { EarningsBrief, Sentiment } from '../../core/models/brief.model';

const SENTIMENT_LABELS: Record<Sentiment, string> = {
  very_positive: 'Very Positive',
  positive: 'Positive',
  neutral: 'Neutral',
  negative: 'Negative',
  very_negative: 'Very Negative',
};

@Component({
  selector: 'app-brief-detail',
  imports: [RouterLink],
  templateUrl: './brief-detail.html',
  styleUrl: './brief-detail.scss',
})
export class BriefDetail {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);

  symbol = signal<string>('');
  briefs = signal<EarningsBrief[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  constructor() {
    const symbol = this.route.snapshot.paramMap.get('symbol') ?? '';
    this.symbol.set(symbol);
    this.api.listBriefs(symbol).subscribe({
      next: (briefs) => {
        this.briefs.set(briefs);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not reach the API. Is the Django server running?');
        this.loading.set(false);
      },
    });
  }

  get latest(): EarningsBrief | undefined {
    return this.briefs()[0];
  }

  get metricEntries(): { key: string; value: string }[] {
    const metrics = this.latest?.key_metrics;
    if (!metrics) return [];
    return Object.entries(metrics).map(([key, value]) => ({
      key: this.humanizeKey(key),
      value: String(value),
    }));
  }

  private humanizeKey(key: string): string {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());
  }

  ratingTone(rating: string): 'buy' | 'hold' | 'sell' {
    const normalized = rating.toLowerCase();
    if (normalized.includes('sell')) return 'sell';
    if (normalized.includes('buy')) return 'buy';
    return 'hold';
  }

  /** Needle position (0-100) along the sell↔buy verdict meter. */
  ratingPosition(rating: string): number {
    const normalized = rating.toLowerCase();
    if (normalized.includes('strong sell')) return 6;
    if (normalized.includes('strong buy')) return 94;
    if (normalized.includes('sell')) return 25;
    if (normalized.includes('buy')) return 75;
    return 50;
  }

  sentimentClass(sentiment: Sentiment): string {
    if (sentiment === 'very_positive' || sentiment === 'positive') return 'badge-success';
    if (sentiment === 'very_negative' || sentiment === 'negative') return 'badge-danger';
    return 'badge-neutral';
  }

  sentimentLabel(sentiment: Sentiment): string {
    return SENTIMENT_LABELS[sentiment] ?? sentiment;
  }

  severityTone(severity: string): 'high' | 'medium' | 'low' {
    const normalized = severity.toLowerCase();
    if (normalized === 'high') return 'high';
    if (normalized === 'medium') return 'medium';
    return 'low';
  }
}
