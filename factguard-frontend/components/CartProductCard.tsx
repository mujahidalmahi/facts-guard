'use client';

import {
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  AlertCircle,
  Clock,
} from 'lucide-react';

import type {
  CartListingEntry,
} from '@/types';

const TRUST_MAP: Record<string, { Icon: any; color: string; label: string }> = {
  GREEN: { Icon: ShieldCheck, color: '#16a34a', label: 'Trusted' },
  YELLOW: { Icon: AlertCircle, color: '#d97706', label: 'Unverified' },
  RED: { Icon: AlertTriangle, color: '#dc2626', label: 'Risky' },
};

const COUNTERFEIT_COLORS: Record<string, string> = {
  None: 'text-emerald-400',
  Low: 'text-amber-400',
  Medium: 'text-orange-400',
  High: 'text-red-400',
};

export function CartProductCard({
  listing,
}: {
  listing: CartListingEntry;
}) {
  const t = TRUST_MAP[listing.trust_level] ?? TRUST_MAP['YELLOW'];
  const { Icon } = t;

  return (
    <div
      className='rounded-2xl border p-4 space-y-3 transition-all
      hover:shadow-lg bg-[var(--card)] border-[var(--card-border)]'
    >
      <div className='flex items-center justify-between'>
        <span className='font-bold text-sm'>
          {listing.merchant}
        </span>

        <span
          className='flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full border'
          style={{
            color: t.color,
            borderColor: `${t.color}44`,
            background: `${t.color}11`,
          }}
        >
          <Icon className='size-3' />
          {t.label}
        </span>
      </div>

      <p className='text-sm line-clamp-2'>
        {listing.title}
      </p>

      <p className='text-2xl font-black text-[var(--foreground)]'>
        ${listing.price?.toFixed(2)}
      </p>

      <div className='flex items-center gap-2 text-xs'>
        <span className={`font-mono ${COUNTERFEIT_COLORS[listing.counterfeit_risk] ?? 'text-slate-400'}`}>
          Counterfeit: {listing.counterfeit_risk}
        </span>
        <span className='text-[var(--muted-foreground)]'>·</span>
        <span className='text-[var(--muted-foreground)]'>
          {listing.condition}
        </span>
        {!listing.in_stock && (
          <>
            <span className='text-[var(--muted-foreground)]'>·</span>
            <span className='text-red-400 font-semibold'>Out of stock</span>
          </>
        )}
      </div>

      {listing.deal_score > 0 && (
        <div className='flex items-center gap-1 text-xs text-[var(--muted-foreground)]'>
          <Clock className='size-3' />
          Deal score: {listing.deal_score}/100
        </div>
      )}

      <p className='text-xs text-[var(--muted-foreground)] leading-relaxed'>
        {listing.trust_reason}
      </p>

      <a
        href={listing.url}
        target='_blank'
        rel='noopener noreferrer'
        className='flex items-center gap-1.5 text-xs font-semibold
          text-[var(--accent)] hover:text-[var(--accent-hover)]
          transition-colors min-h-[48px] py-2'
      >
        <ExternalLink className='size-3' />
        Shop on {listing.merchant}
      </a>
    </div>
  );
}
