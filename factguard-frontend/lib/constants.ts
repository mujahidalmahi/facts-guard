import { Verdict } from '@/types';

export const VERDICT_COLORS: Record<Verdict, string> = {
  Verified: 'bg-emerald-700 text-white dark:bg-emerald-600',
  'Likely True': 'bg-teal-700 text-white dark:bg-teal-600',
  'Mixed Evidence': 'bg-amber-600 text-white dark:bg-amber-500',
  'Likely Misleading': 'bg-orange-700 text-white dark:bg-orange-600',
  Unverified: 'bg-slate-600 text-white dark:bg-slate-500',
};