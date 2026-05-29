import type { Verdict, AppMode } from '@/types';

export const VERDICT_COLORS: Record<Verdict, string> = {
  Verified: 'bg-emerald-700 text-white dark:bg-emerald-600',
  'Likely True': 'bg-teal-700 text-white dark:bg-teal-600',
  'Mixed Evidence': 'bg-amber-600 text-white dark:bg-amber-500',
  'Likely Misleading': 'bg-orange-700 text-white dark:bg-orange-600',
  Unverified: 'bg-slate-600 text-white dark:bg-slate-500',
};

export const VERDICT_GLOW: Record<Verdict, string> = {
  Verified: '#10B981',
  'Likely True': '#6366F1',
  'Mixed Evidence': '#F59E0B',
  'Likely Misleading': '#EF4444',
  Unverified: '#64748B',
};

export const MODE_LABELS: Record<AppMode, string> = {
  verify: 'AI Fact Intelligence',
  financial: 'Live Market Oracle',
  security: 'Real-Time Threat Monitor',
  cart: 'Price Trust Engine',
};

export const MODE_HEADLINES: Record<AppMode, string> = {
  verify: 'FactGuard',
  financial: 'Market Intel',
  security: 'ThreatGuard',
  cart: 'CartGuard',
};
