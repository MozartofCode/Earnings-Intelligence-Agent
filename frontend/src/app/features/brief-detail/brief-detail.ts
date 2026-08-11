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

  ratingClass(rating: string): string {
    const normalized = rating.toLowerCase();
    if (normalized.includes('strong buy') || normalized.includes('buy')) return 'badge-success';
    if (normalized.includes('sell')) return 'badge-danger';
    return 'badge-neutral';
  }

  sentimentClass(sentiment: Sentiment): string {
    if (sentiment === 'very_positive' || sentiment === 'positive') return 'badge-success';
    if (sentiment === 'very_negative' || sentiment === 'negative') return 'badge-danger';
    return 'badge-neutral';
  }

  sentimentLabel(sentiment: Sentiment): string {
    return SENTIMENT_LABELS[sentiment] ?? sentiment;
  }

  severityClass(severity: string): string {
    const normalized = severity.toLowerCase();
    if (normalized === 'high') return 'badge-danger';
    if (normalized === 'medium') return 'badge-warning';
    return 'badge-neutral';
  }
}
