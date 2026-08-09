import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { EarningsBrief } from '../models/brief.model';
import { Ticker } from '../models/ticker.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  listTickers(): Observable<Ticker[]> {
    return this.http.get<Ticker[]>(`${this.baseUrl}/tickers/`);
  }

  addTicker(symbol: string, companyName = ''): Observable<Ticker> {
    return this.http.post<Ticker>(`${this.baseUrl}/tickers/`, {
      symbol,
      company_name: companyName,
    });
  }

  removeTicker(symbol: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/tickers/${symbol}/`);
  }

  analyzeTicker(symbol: string): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/tickers/${symbol}/analyze/`, {});
  }

  listBriefs(symbol?: string): Observable<EarningsBrief[]> {
    const url = symbol
      ? `${this.baseUrl}/briefs/?ticker=${symbol}`
      : `${this.baseUrl}/briefs/`;
    return this.http.get<EarningsBrief[]>(url);
  }

  getBrief(id: number): Observable<EarningsBrief> {
    return this.http.get<EarningsBrief>(`${this.baseUrl}/briefs/${id}/`);
  }
}
