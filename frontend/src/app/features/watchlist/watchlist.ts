import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/services/api.service';
import { Ticker } from '../../core/models/ticker.model';
import { EarningsBrief } from '../../core/models/brief.model';

const AVATAR_COLORS = ['#3f7d4f', '#4c6fa0', '#7a6a3f', '#8a7d66', '#b5622b', '#a8402f'];
const FRESH_WINDOW_HOURS = 48;

export interface StatusChip {
  label: string;
  tone: 'fresh' | 'stale' | 'none' | 'live';
}

@Component({
  selector: 'app-watchlist',
  imports: [FormsModule, RouterLink, DatePipe],
  templateUrl: './watchlist.html',
  styleUrl: './watchlist.scss',
})
export class Watchlist {
  private readonly api = inject(ApiService);

  tickers = signal<Ticker[]>([]);
  latestBriefs = signal<Record<string, EarningsBrief>>({});
  loading = signal(true);
  error = signal<string | null>(null);
  newSymbol = '';
  submitting = signal(false);
  analyzeStatus = signal<Record<string, string>>({});
  analyzeErrorDetail = signal<Record<string, string>>({});
  private analyzeRunning = new Set<string>();

  constructor() {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.api.listTickers().subscribe({
      next: (tickers) => {
        this.tickers.set(tickers);
        this.loading.set(false);
        this.error.set(null);
        this.loadLatestBriefs();
      },
      error: () => {
        this.error.set('Could not reach the API. Is the Django server running?');
        this.loading.set(false);
      },
    });
  }

  private loadLatestBriefs(): void {
    this.api.listBriefs().subscribe({
      next: (briefs) => {
        const latest: Record<string, EarningsBrief> = {};
        for (const brief of briefs) {
          const existing = latest[brief.ticker];
          if (!existing || new Date(brief.created_at) > new Date(existing.created_at)) {
            latest[brief.ticker] = brief;
          }
        }
        this.latestBriefs.set(latest);
      },
      error: () => {
        // Briefs are supplementary to the watchlist rows; a failure here
        // shouldn't block the ticker list from rendering.
      },
    });
  }

  hasBrief(symbol: string): boolean {
    return !!this.latestBriefs()[symbol];
  }

  briefFor(symbol: string): EarningsBrief | undefined {
    return this.latestBriefs()[symbol];
  }

  statusChip(symbol: string): StatusChip {
    if (this.isAnalyzeRunning(symbol)) {
      return { label: 'ANALYZING…', tone: 'live' };
    }
    const brief = this.latestBriefs()[symbol];
    if (!brief) {
      return { label: 'NOT ANALYZED', tone: 'none' };
    }
    const hours = (Date.now() - new Date(brief.created_at).getTime()) / 3_600_000;
    const age = hours < 24 ? `${Math.max(1, Math.round(hours))}H AGO` : `${Math.round(hours / 24)}D AGO`;
    return hours < FRESH_WINDOW_HOURS
      ? { label: `FRESH · ${age}`, tone: 'fresh' }
      : { label: `STALE · ${age}`, tone: 'stale' };
  }

  ratingBadgeClass(rating: string): string {
    const normalized = rating.toLowerCase();
    if (normalized.includes('sell')) return 'badge-danger';
    if (normalized.includes('buy')) return 'badge-success';
    return 'badge-warning';
  }

  addTicker(): void {
    const symbol = this.newSymbol.trim().toUpperCase();
    if (!symbol || this.submitting()) {
      return;
    }
    this.submitting.set(true);
    this.api.addTicker(symbol).subscribe({
      next: () => {
        this.newSymbol = '';
        this.submitting.set(false);
        this.refresh();
      },
      error: (err) => {
        this.error.set(err?.error?.symbol?.[0] ?? 'Could not add ticker.');
        this.submitting.set(false);
      },
    });
  }

  removeTicker(symbol: string): void {
    this.api.removeTicker(symbol).subscribe({
      next: () => this.refresh(),
      error: () => this.error.set(`Could not remove ${symbol}.`),
    });
  }

  analyze(symbol: string): void {
    this.analyzeRunning.add(symbol);
    this.analyzeStatus.update((s) => ({ ...s, [symbol]: 'Running…' }));
    this.api.analyzeTicker(symbol).subscribe({
      next: () => {
        this.analyzeRunning.delete(symbol);
        this.analyzeStatus.update((s) => ({ ...s, [symbol]: 'Done' }));
      },
      error: (err) => {
        const detail: string = err?.error?.detail ?? 'Analysis is not available yet.';
        this.analyzeRunning.delete(symbol);
        this.analyzeErrorDetail.update((s) => ({ ...s, [symbol]: detail }));
        this.analyzeStatus.update((s) => ({ ...s, [symbol]: 'Not implemented yet' }));
      },
    });
  }

  isAnalyzeRunning(symbol: string): boolean {
    return this.analyzeRunning.has(symbol);
  }

  avatarColor(symbol: string): string {
    let hash = 0;
    for (let i = 0; i < symbol.length; i++) {
      hash = symbol.charCodeAt(i) + ((hash << 5) - hash);
    }
    return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
  }
}
