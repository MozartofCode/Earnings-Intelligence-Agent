import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../../core/services/api.service';
import { EarningsBrief } from '../../core/models/brief.model';

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
}
