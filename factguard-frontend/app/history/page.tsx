'use client';

import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, TrendingUp, ShoppingCart, AlertTriangle, Clock, ChevronLeft, ChevronRight, Eye, Search, Trash2 } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { HistorySkeleton } from '@/components/Skeleton';

const MODE_ICONS: Record<string, LucideIcon> = {
  verify: Shield,
  financial: TrendingUp,
  cart: ShoppingCart,
  security: AlertTriangle,
};

const MODE_COLORS: Record<string, string> = {
  verify: '#4F46E5',
  financial: '#7C3AED',
  cart: '#06B6D4',
  security: '#F59E0B',
};

function relativeTime(iso: string): string {
  const ts = new Date(iso).getTime();
  if (isNaN(ts)) return '';
  const diff = (Date.now() - ts) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 86400 * 2) return 'yesterday';
  return `${Math.floor(diff / 86400)}d ago`;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const PAGE_SIZE = 20;

interface HistoryItem {
  jobId: string;
  claim: string;
  status: string;
  createdAt: string;
  mode?: 'verify' | 'financial' | 'cart' | 'security';
  display_text?: string;
  query?: string;
  verdict?: string;
  signal?: string;
  severity?: string;
}

export default function HistoryPage() {
  const [claims, setClaims] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  const [page, setPage] = useState(0);

  useEffect(() => {
    fetch(`${API_URL}/history`)
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        setClaims(data.claims ?? []);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (filter === 'all') return claims;
    return claims.filter((c) => c.mode === filter);
  }, [claims, filter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages - 1);
  const pageItems = filtered.slice(safePage * PAGE_SIZE, (safePage + 1) * PAGE_SIZE);

  const verdictConfig = (item: HistoryItem): { color: string; text: string } => {
    if (item.verdict === 'Verified') return { color: '#10B981', text: item.verdict };
    if (item.verdict === 'Likely True') return { color: '#4F46E5', text: item.verdict };
    if (item.verdict === 'Mixed Evidence') return { color: '#F59E0B', text: item.verdict };
    if (item.verdict === 'Likely Misleading') return { color: '#EF4444', text: item.verdict };
    if (item.signal === 'Bullish') return { color: '#10B981', text: item.signal };
    if (item.signal === 'Bearish') return { color: '#EF4444', text: item.signal };
    if (item.severity === 'critical') return { color: '#EF4444', text: item.severity };
    if (item.severity === 'high') return { color: '#F97316', text: item.severity };
    if (item.severity === 'medium') return { color: '#F59E0B', text: item.severity };
    if (item.mode === 'cart') return { color: '#06B6D4', text: 'Analysed' };
    return { color: '#4F46E5', text: 'Analysed' };
  };

  if (loading) return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <HistorySkeleton />
    </main>
  );

  if (error) return (
    <main className="max-w-4xl mx-auto px-4 py-10 text-center">
      <p style={{ color: 'var(--color-accent-red)' }}>Failed to load history</p>
    </main>
  );

  if (claims.length === 0) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-6">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center max-w-md">
          <div className="relative w-48 h-48 mx-auto mb-8">
            <div className="absolute inset-0 rounded-full border border-dashed" style={{ borderColor: 'var(--color-border-default)' }} />
            {[
              { icon: Shield, angle: 0, color: '#4F46E5' },
              { icon: TrendingUp, angle: 90, color: '#7C3AED' },
              { icon: AlertTriangle, angle: 180, color: '#F59E0B' },
              { icon: ShoppingCart, angle: 270, color: '#06B6D4' },
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={i}
                  className="absolute top-1/2 left-1/2 w-12 h-12 -ml-6 -mt-6 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)', boxShadow: `0 0 20px ${item.color}40` }}
                  animate={{
                    x: Math.cos((item.angle * Math.PI) / 180) * 80,
                    y: Math.sin((item.angle * Math.PI) / 180) * 80,
                  }}
                  transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: 'linear',
                    repeatType: 'loop',
                  }}
                >
                  <Icon className="w-5 h-5" style={{ color: item.color }} />
                </motion.div>
              );
            })}
            <div className="absolute inset-0 flex items-center justify-center">
              <Clock className="w-10 h-10" style={{ color: 'var(--color-text-tertiary)' }} />
            </div>
          </div>

          <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>No analysis history yet</h2>
          <p className="mb-6" style={{ color: 'var(--color-text-secondary)' }}>Submit your first claim to get started</p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition-all hover:scale-105"
            style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)', boxShadow: '0 0 20px rgba(79, 70, 229, 0.4)' }}
          >
            Start Analysing →
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="data-label mb-2">ANALYSIS HISTORY</div>
        <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>Analysis History</h1>
        <p className="data-label">Last {claims.length} queries across all tracks</p>
      </motion.div>

      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          {(['all', 'verify', 'financial', 'security', 'cart'] as const).map((f) => {
            const isActive = filter === f;
            const Icon = f !== 'all' ? MODE_ICONS[f] : Search;
            return (
              <button
                key={f}
                onClick={() => { setFilter(f); setPage(0); }}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${isActive ? 'text-white' : 'text-[var(--color-text-secondary)] border border-[var(--color-border-default)] hover:border-[var(--color-border-strong)]'}`}
                style={isActive ? { backgroundColor: f === 'all' ? '#4F46E5' : MODE_COLORS[f] } : {}}
              >
                <Icon className="w-3 h-3" />
                {f === 'all' ? 'ALL' : f.toUpperCase()}
              </button>
            );
          })}
        </div>
      </div>

      <div
        className="overflow-hidden rounded-2xl"
        style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: 'var(--color-border-subtle)' }}>
                <th className="data-label text-left py-3 px-4 font-medium">Mode</th>
                <th className="data-label text-left py-3 px-4 font-medium">Query</th>
                <th className="data-label text-left py-3 px-4 font-medium">Verdict / Signal</th>
                <th className="data-label text-left py-3 px-4 font-medium">Date</th>
                <th className="py-3 px-4"></th>
              </tr>
            </thead>
            <tbody>
              {pageItems.map((item, i) => {
                const Icon = MODE_ICONS[item.mode ?? 'verify'] ?? Shield;
                const color = MODE_COLORS[item.mode ?? 'verify'] ?? '#4F46E5';
                const vc = verdictConfig(item);
                const query = item.display_text ?? item.claim ?? item.query ?? '';
                return (
                  <motion.tr
                    key={item.jobId}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                    className="border-b border-[var(--color-border-subtle)] last:border-0 transition-colors"
                    style={{ backgroundColor: i % 2 === 0 ? 'transparent' : 'var(--color-bg-elevated)' }}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
                          <Icon className="w-3.5 h-3.5" style={{ color }} />
                        </div>
                        <span className="text-xs capitalize" style={{ color: 'var(--color-text-secondary)' }}>{item.mode}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 max-w-[300px]">
                      <div className="truncate" style={{ color: 'var(--color-text-primary)' }} title={query}>
                        {query.length > 60 ? query.slice(0, 60) + '...' : query}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider"
                        style={{ color: vc.color, backgroundColor: `${vc.color}15`, border: `1px solid ${vc.color}30` }}
                      >
                        <span className="w-1 h-1 rounded-full" style={{ backgroundColor: vc.color }} />
                        {vc.text}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="data-label font-mono" title={new Date(item.createdAt).toLocaleString()}>
                        {relativeTime(item.createdAt)}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <Link
                        href={item.status === 'done' ? `/result/${item.jobId}?mode=${item.mode || 'verify'}` : `/loading?job=${item.jobId}&mode=${item.mode || 'verify'}`}
                        className="flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors"
                        style={{ color: 'var(--color-accent-primary)' }}
                      >
                        <Eye className="w-3 h-3" /> View
                      </Link>
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between px-4 py-3 border-t" style={{ borderColor: 'var(--color-border-subtle)' }}>
          <div className="data-label">
            Page {safePage + 1} of {totalPages} · {filtered.length} total
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={safePage === 0}
              className="p-1.5 rounded border transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              style={{ borderColor: 'var(--color-border-default)', color: 'var(--color-text-secondary)' }}
              aria-label="Previous page"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={safePage >= totalPages - 1}
              className="p-1.5 rounded border transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              style={{ borderColor: 'var(--color-border-default)', color: 'var(--color-text-secondary)' }}
              aria-label="Next page"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
