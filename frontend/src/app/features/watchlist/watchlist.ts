import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/services/api.service';
import { Ticker } from '../../core/models/ticker.model';

const AVATAR_COLORS = ['#4f46e5', '#0891b2', '#c026d3', '#d97706', '#16a34a', '#dc2626'];

@Component({
  selector: 'app-watchlist',
  imports: [FormsModule, RouterLink, DatePipe],
  templateUrl: './watchlist.html',
  styleUrl: './watchlist.scss',
})
export class Watchlist {
  private readonly api = inject(ApiService);

  tickers = signal<Ticker[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);
  newSymbol = '';
  submitting = signal(false);
  analyzeStatus = signal<Record<string, string>>({});
  analyzeErrorDetail = signal<Record<string, string>>({});
  private analyzeErrors = new Set<string>();
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
      },
      error: () => {
        this.error.set('Could not reach the API. Is the Django server running?');
        this.loading.set(false);
      },
    });
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
    this.analyzeErrors.delete(symbol);
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
        this.analyzeErrors.add(symbol);
        this.analyzeErrorDetail.update((s) => ({ ...s, [symbol]: detail }));
        this.analyzeStatus.update((s) => ({ ...s, [symbol]: 'Not implemented yet' }));
      },
    });
  }

  isAnalyzeError(symbol: string): boolean {
    return this.analyzeErrors.has(symbol);
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
