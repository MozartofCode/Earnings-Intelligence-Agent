import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/services/api.service';
import { Ticker } from '../../core/models/ticker.model';

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
  analyzeStatus = signal<Record<string, string>>({});

  constructor() {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.api.listTickers().subscribe({
      next: (tickers) => {
        this.tickers.set(tickers);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not reach the API. Is the Django server running?');
        this.loading.set(false);
      },
    });
  }

  addTicker(): void {
    const symbol = this.newSymbol.trim().toUpperCase();
    if (!symbol) {
      return;
    }
    this.api.addTicker(symbol).subscribe({
      next: () => {
        this.newSymbol = '';
        this.refresh();
      },
      error: (err) => {
        this.error.set(err?.error?.symbol?.[0] ?? 'Could not add ticker.');
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
    this.analyzeStatus.update((s) => ({ ...s, [symbol]: 'Running...' }));
    this.api.analyzeTicker(symbol).subscribe({
      next: () => {
        this.analyzeStatus.update((s) => ({ ...s, [symbol]: 'Done' }));
      },
      error: (err) => {
        const detail = err?.error?.detail ?? 'Analysis is not available yet.';
        this.analyzeStatus.update((s) => ({ ...s, [symbol]: detail }));
      },
    });
  }
}
