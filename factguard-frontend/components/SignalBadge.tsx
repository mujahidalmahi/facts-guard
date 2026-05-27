'use client';

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const CFG: Record<string, { bg: string; tx: string; bd: string; label: string; icon: LucideIcon }> = {
  Bullish: {
    bg: 'rgba(16,185,129,0.1)', tx: 'var(--color-accent-emerald)', bd: 'rgba(16,185,129,0.25)',
    label: 'BULLISH', icon: TrendingUp,
  },
  Bearish: {
    bg: 'rgba(239,68,68,0.1)', tx: 'var(--color-accent-red)', bd: 'rgba(239,68,68,0.25)',
    label: 'BEARISH', icon: TrendingDown,
  },
  Neutral: {
    bg: 'rgba(245,158,11,0.1)', tx: 'var(--color-accent-amber)', bd: 'rgba(245,158,11,0.25)',
    label: 'NEUTRAL', icon: Minus,
  },
};

export function SignalBadge({ signal }: { signal: string }) {
  const c = CFG[signal as keyof typeof CFG] ?? CFG.Neutral;
  const Icon = c.icon;

  return (
    <span
      className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-black border"
      style={{ backgroundColor: c.bg, color: c.tx, borderColor: c.bd }}
    >
      <Icon className="size-4" />
      {c.label}
    </span>
  );
}
