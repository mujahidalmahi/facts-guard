'use client';

import { motion } from 'framer-motion';
import { ShoppingCart, CheckCircle2, XCircle, AlertTriangle, ExternalLink, TrendingUp, TrendingDown, Minus, Star } from 'lucide-react';
import type { CartResult, CartListingEntry } from '@/types';
import { useMemo } from 'react';

const TRUST_CONFIG: Record<'GREEN' | 'YELLOW' | 'RED', { color: string; label: string; border: string; badgeBg: string }> = {
  GREEN: { color: '#10B981', label: 'TRUSTED', border: '4px solid #10B981', badgeBg: 'rgba(16, 185, 129, 0.15)' },
  YELLOW: { color: '#F59E0B', label: 'CAUTION', border: '4px solid #F59E0B', badgeBg: 'rgba(245, 158, 11, 0.15)' },
  RED: { color: '#EF4444', label: 'RISKY', border: '4px solid #EF4444', badgeBg: 'rgba(239, 68, 68, 0.15)' },
};

function DealScoreRing({ score, color }: { score: number; color: string }) {
  const circumference = 2 * Math.PI * 20;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div className="relative w-12 h-12">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 48 48">
        <circle cx="24" cy="24" r="20" stroke="rgba(99, 102, 241, 0.1)" strokeWidth="3" fill="none" />
        <motion.circle
          cx="24" cy="24" r="20" stroke={color} strokeWidth="3" fill="none" strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{ filter: `drop-shadow(0 0 3px ${color})` }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="font-mono text-xs font-bold" style={{ color }}>{score}</div>
      </div>
    </div>
  );
}

function ListingCard({ listing, index, isBest }: { listing: CartListingEntry; index: number; isBest: boolean }) {
  const trust = TRUST_CONFIG[listing.trust_level] ?? TRUST_CONFIG.YELLOW;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="relative overflow-hidden rounded-2xl"
      style={{
        backgroundColor: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border-default)',
        borderTop: trust.border,
        ...(isBest ? { boxShadow: '0 0 0 2px rgba(16,185,129,0.5)' } : {}),
      }}
    >
      {isBest && (
        <div className="absolute top-2 right-2 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1"
          style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10B981', border: '1px solid rgba(16, 185, 129, 0.4)' }}
        >
          <Star className="w-2.5 h-2.5 fill-current" /> Best Deal
        </div>
      )}

      <div className="p-5">
        <div className="flex gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="data-label px-2 py-0.5 rounded font-bold"
                style={{ color: trust.color, backgroundColor: trust.badgeBg, border: `1px solid ${trust.color}40` }}
              >
                {trust.label}
              </span>
              <span className="data-label px-2 py-0.5 rounded"
                style={{
                  color: listing.condition === 'New' ? '#10B981' : listing.condition === 'Refurbished' ? '#F59E0B' : '#7E8FAD',
                  backgroundColor: listing.condition === 'New' ? 'rgba(16, 185, 129, 0.1)' : listing.condition === 'Refurbished' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(126, 143, 173, 0.1)',
                }}
              >
                {listing.condition}
              </span>
            </div>

            <h3 className="text-sm font-semibold leading-tight line-clamp-2 mb-2" style={{ color: 'var(--color-text-primary)' }}>
              {listing.title}
            </h3>

            <div className="text-xs flex items-center gap-1" style={{ color: 'var(--color-text-secondary)' }}>
              <ShoppingCart className="w-3 h-3" />
              {listing.merchant}
            </div>

            {listing.rating && (
              <div className="text-xs mt-1 flex items-center gap-1" style={{ color: '#F59E0B' }}>
                <Star className="w-3 h-3 fill-current" /> {listing.rating}
              </div>
            )}
          </div>
          {listing.image && (
            <div className="shrink-0 w-20 h-20 rounded-lg overflow-hidden" style={{ backgroundColor: 'var(--color-bg-elevated)' }}>
              <img src={listing.image} alt="" className="w-full h-full object-contain" loading="lazy" />
            </div>
          )}
        </div>

        <div className="flex items-end justify-between mb-4">
          <div>
            <div className="data-label mb-1">PRICE</div>
            <div className="text-3xl font-black" style={{ color: trust.color, fontFamily: 'var(--font-sora)' }}>
              ${listing.price?.toLocaleString() ?? '0'}
            </div>
          </div>
          <div className="text-center">
            <DealScoreRing score={listing.deal_score ?? 0} color={trust.color} />
            <div className="data-label" style={{ fontSize: '9px', marginTop: '2px' }}>Deal Score</div>
          </div>
        </div>

        {listing.trust_reason && (
          <p className="text-xs italic leading-relaxed mb-3" style={{ color: 'var(--color-text-secondary)', minHeight: '32px' }}>
            &ldquo;{listing.trust_reason}&rdquo;
          </p>
        )}

        {(listing.counterfeit_risk === 'High' || listing.counterfeit_risk === 'Medium') && (
          <div className="flex items-center gap-2 px-2 py-1.5 rounded text-[10px] font-semibold mb-3" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444' }}>
            <AlertTriangle className="w-3 h-3" />
            Counterfeit Risk: {listing.counterfeit_risk.toUpperCase()}
          </div>
        )}

        <div className="flex items-center justify-between gap-2 pt-3 border-t" style={{ borderColor: 'var(--color-border-subtle)' }}>
          <div className="flex items-center gap-1.5 text-xs">
            {listing.in_stock ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" style={{ color: 'var(--color-accent-emerald)' }} />
                <span style={{ color: 'var(--color-accent-emerald)' }}>In Stock</span>
              </>
            ) : (
              <>
                <XCircle className="w-3.5 h-3.5" style={{ color: 'var(--color-accent-red)' }} />
                <span style={{ color: 'var(--color-accent-red)' }}>Out of Stock</span>
              </>
            )}
          </div>
          <a href={listing.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all hover:scale-105"
            style={{ color: trust.color, backgroundColor: trust.badgeBg, border: `1px solid ${trust.color}40` }}
          >
            View Deal <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </motion.div>
  );
}

export function CartResultView({ data }: { data: CartResult }) {
  const listings = data.analysis?.listings ?? data.listings ?? [];

  const sorted = useMemo(() => {
    const order = { GREEN: 0, YELLOW: 1, RED: 2 };
    return [...listings].sort((a, b) => {
      if (order[a.trust_level] !== order[b.trust_level]) return order[a.trust_level] - order[b.trust_level];
      return (a.price ?? 0) - (b.price ?? 0);
    });
  }, [listings]);

  if (listings.length === 0) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <div className="data-label mb-2 flex items-center gap-2">
            <ShoppingCart className="w-3 h-3" style={{ color: '#06B6D4' }} />
            CARTGUARD ANALYSIS
          </div>
          <h1 className="text-3xl font-bold mb-4" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>
            {data.product || 'Product'}
          </h1>
          <div className="rounded-2xl p-8 text-center" style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}>
            <p style={{ color: 'var(--color-text-secondary)' }}>No listings found for this product.</p>
          </div>
        </motion.div>
      </div>
    );
  }

  const best = sorted.find((l) => l.trust_level !== 'RED') || sorted[0];
  const prices = listings.map((l) => l.price ?? 0);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length || 0;

  const priceSpread = minPrice > 0 ? (maxPrice - minPrice) / avgPrice : 0;
  const trend = priceSpread > 0.4 ? 'Dropping' : priceSpread > 0.2 ? 'Stable' : 'Rising';
  const TrendIcon = trend === 'Dropping' ? TrendingDown : trend === 'Rising' ? TrendingUp : Minus;
  const trendColor = trend === 'Dropping' ? '#10B981' : trend === 'Rising' ? '#EF4444' : '#F59E0B';

  const recommendation = sorted.filter((l) => l.trust_level === 'RED').length > listings.length / 2
    ? 'High number of suspicious listings detected. Exercise extreme caution — many prices are significantly below wholesale cost, indicating counterfeit risk.'
    : sorted.filter((l) => l.trust_level === 'GREEN').length >= 3
    ? 'Multiple trusted sources available. We recommend purchasing from the best-priced GREEN-rated merchant to ensure authenticity and warranty coverage.'
    : 'Consider waiting for additional inventory from authorized retailers. Current options show mixed trust levels.';

  const warnings: string[] = [];
  if (listings.some((l) => l.counterfeit_risk === 'High')) warnings.push('Some listings flagged with HIGH counterfeit risk. Avoid RED-rated merchants.');
  if (priceSpread > 0.5) warnings.push('Unusually wide price spread suggests fake/clone products in the market.');
  if (listings.some((l) => l.condition === 'Unknown')) warnings.push('Some sellers do not disclose product condition — verify before purchasing.');

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="data-label mb-2 flex items-center gap-2">
          <ShoppingCart className="w-3 h-3" style={{ color: '#06B6D4' }} />
          CARTGUARD ANALYSIS · {listings.length} LISTINGS SCANNED
        </div>
        <h1 className="text-3xl font-bold mb-4" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>
          {data.analysis?.product_name || data.product}
        </h1>

        <div
          className="rounded-2xl p-5 grid sm:grid-cols-4 gap-4"
          style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
        >
          <div>
            <div className="data-label mb-1">BEST PRICE</div>
            <div className="font-mono text-2xl font-black" style={{ color: 'var(--color-accent-emerald)' }}>${best.price?.toLocaleString() ?? 'N/A'}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>at {best.merchant}</div>
          </div>
          <div>
            <div className="data-label mb-1">MARKET RANGE</div>
            <div className="font-mono text-lg" style={{ color: 'var(--color-text-primary)' }}>${minPrice.toLocaleString()} – ${maxPrice.toLocaleString()}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>Avg: ${Math.round(avgPrice).toLocaleString()}</div>
          </div>
          <div>
            <div className="data-label mb-1">PRICE TREND</div>
            <div className="flex items-center gap-2 text-lg font-semibold" style={{ color: trendColor }}>
              <TrendIcon className="w-5 h-5" />
              {trend}
            </div>
          </div>
          <div>
            <div className="data-label mb-1">BEST TIME TO BUY</div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-bold"
              style={{
                color: trend === 'Dropping' ? '#10B981' : trend === 'Rising' ? '#EF4444' : '#F59E0B',
                backgroundColor: trend === 'Dropping' ? 'rgba(16, 185, 129, 0.1)' : trend === 'Rising' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
              }}
            >
              {trend === 'Dropping' ? 'BUY NOW' : trend === 'Rising' ? 'URGENT' : 'WAIT'}
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {sorted.map((listing, i) => (
          <ListingCard key={i} listing={listing} index={i} isBest={listing === best} />
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="rounded-2xl p-6 mb-6"
        style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)', borderLeft: '4px solid #4F46E5' }}
      >
        <div className="data-label mb-3" style={{ color: 'var(--color-accent-primary)' }}>FACTGUARD RECOMMENDATION</div>
        <p className="leading-relaxed" style={{ color: 'var(--color-text-primary)' }}>{recommendation}</p>
      </motion.div>

      {warnings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-2xl p-6"
          style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
        >
          <div className="data-label mb-3 flex items-center gap-2" style={{ color: 'var(--color-accent-amber)' }}>
            <AlertTriangle className="w-3 h-3" />
            PRICE WARNINGS
          </div>
          <div className="space-y-2">
            {warnings.map((w, i) => (
              <div key={i} className="flex items-start gap-2 p-3 rounded-lg" style={{ backgroundColor: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" style={{ color: 'var(--color-accent-amber)' }} />
                <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{w}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
