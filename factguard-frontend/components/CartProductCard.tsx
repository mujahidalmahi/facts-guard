'use client';

import {
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  AlertCircle,
} from 'lucide-react';

import type {
  CartListing,
} from '@/types';

const TRUST = {
  green: {
    Icon: ShieldCheck,
    color: '#16a34a',
    bg: '#f0fdf4',
    label: 'Trusted',
    border: '#86efac',
  },

  yellow: {
    Icon: AlertCircle,
    color: '#d97706',
    bg: '#fffbeb',
    label: 'Unverified',
    border: '#fde68a',
  },

  red: {
    Icon: AlertTriangle,
    color: '#dc2626',
    bg: '#fef2f2',
    label: 'Risky',
    border: '#fca5a5',
  },
};

export function CartProductCard({
  listing,
}: {
  listing: CartListing;
}) {
  const t =
    TRUST[
      listing.trust_signal
    ] ?? TRUST.yellow;

  const { Icon } = t;

  return (
    <div
      className='rounded-2xl border
      p-4 space-y-3 transition-all
      hover:shadow-lg'
      style={{
        borderColor: t.border,
        background:
          'var(--card)',
      }}
    >
      <div className='flex items-center justify-between'>
        <span className='font-bold text-sm'>
          {listing.platform}
        </span>

        <span
          className='flex items-center
          gap-1 text-xs font-semibold
          px-2 py-1 rounded-full border'
          style={{
            color: t.color,
            background: t.bg,
            borderColor:
              t.border,
          }}
        >
          <Icon className='size-3' />
          {t.label}
        </span>
      </div>

      <p className='text-sm line-clamp-2'>
        {listing.title}
      </p>

      <p
        className='text-xs
        text-[var(--muted-foreground)]
        line-clamp-2'
      >
        {listing.snippet}
      </p>

      <a
        href={listing.url}
        target='_blank'
        rel='noopener noreferrer'
        className='flex items-center
        gap-1.5 text-xs
        font-semibold
        text-[var(--accent)]
        hover:text-[var(--accent-hover)]
        transition-colors min-h-[48px] py-2'
      >
        <ExternalLink className='size-3' />
        Shop on {listing.platform}
      </a>
    </div>
  );
}