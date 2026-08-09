import { Routes } from '@angular/router';

import { BriefDetail } from './features/brief-detail/brief-detail';
import { Watchlist } from './features/watchlist/watchlist';

export const routes: Routes = [
  { path: '', component: Watchlist },
  { path: 'briefs/:symbol', component: BriefDetail },
];
