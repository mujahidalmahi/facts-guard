'use client';

import { motion } from 'framer-motion';
import { ExternalLink, ShieldCheck, AlertTriangle, AlertCircle } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { CartListingEntry } from '@/types';

const TRUST_MAP: Record<string, { Icon: LucideIcon; color: string; label: string }> = {
  GREEN: { Icon: ShieldCheck, color: '#16a34a', label: 'Trusted' },
  YELLOW: { Icon: AlertCircle, color: '#d97706', label: 'Unverified' },
  RED: { Icon: AlertTriangle, color: '#dc2626', label: 'Risky' },
};

const COUNTERFEIT_COLORS: Record<string, string> = {
  None: 'var(--color-accent-emerald)',
  Low: 'var(--color-accent-amber)',
  Medium: '#f97316',
  High: 'var(--color-accent-red)',
};

function DealScoreRing({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 14;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 70 ? '#10B981' : score >= 40 ? '#F59E0B' : '#EF4444';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="w-8 h-8 -rotate-90" viewBox="0 0 32 32">
        <circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" strokeWidth="2.5"
          style={{ color: 'var(--color-bg-elevated)' }}
        />
        <motion.circle
          cx="16" cy="16" r="14" fill="none" strokeWidth="2.5" strokeLinecap="round"
          initial={{ strokeDasharray: circumference, strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ color, filter: `drop-shadow(0 0 4px ${color}66)` }}
        />
      </svg>
      <span className="absolute text-[8px] font-mono font-bold" style={{ color }}>{score}</span>
    </div>
  );
}

export function CartProductCard({ listing }: { listing: CartListingEntry }) {
  const t = TRUST_MAP[listing.trust_level] ?? TRUST_MAP['YELLOW'];
  const { Icon } = t;

  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="rounded-2xl border p-4 space-y-3 transition-all hover:shadow-lg"
      style={{
        backgroundColor: 'var(--color-bg-surface)',
        borderColor: 'var(--color-border-default)',
      }}
    >
      <div className="flex items-center justify-between">
        <span className="font-bold text-sm" style={{ color: 'var(--color-text-primary)' }}>
          {listing.merchant}
        </span>
        <span
          className="flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full border"
          style={{ color: t.color, borderColor: `${t.color}44`, backgroundColor: `${t.color}11` }}
        >
          <Icon className="size-3" />
          {t.label}
        </span>
      </div>

      <p className="text-sm line-clamp-2" style={{ color: 'var(--color-text-secondary)' }}>
        {listing.title}
      </p>

      <div className="flex items-center justify-between">
        <p className="text-2xl font-black" style={{ color: 'var(--color-text-primary)' }}>
          ${listing.price?.toFixed(2)}
        </p>
        {listing.deal_score > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>Deal</span>
            <DealScoreRing score={listing.deal_score} />
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 text-xs">
        <span className="font-mono" style={{ color: COUNTERFEIT_COLORS[listing.counterfeit_risk] ?? 'var(--color-text-tertiary)' }}>
          Counterfeit: {listing.counterfeit_risk}
        </span>
        <span style={{ color: 'var(--color-text-tertiary)' }}>·</span>
        <span style={{ color: 'var(--color-text-tertiary)' }}>{listing.condition}</span>
        {!listing.in_stock && (
          <>
            <span style={{ color: 'var(--color-text-tertiary)' }}>·</span>
            <span className="font-semibold" style={{ color: 'var(--color-accent-red)' }}>Out of stock</span>
          </>
        )}
      </div>

      <p className="text-xs leading-relaxed" style={{ color: 'var(--color-text-tertiary)' }}>
        {listing.trust_reason}
      </p>

      <a
        href={listing.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-1.5 text-xs font-semibold transition-colors min-h-[48px] py-2"
        style={{ color: 'var(--color-accent-primary)' }}
      >
        <ExternalLink className="size-3" />
        Shop on {listing.merchant}
      </a>
    </motion.div>
  );
}
