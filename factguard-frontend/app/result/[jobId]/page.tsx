'use client';

import { use, useEffect, useState, useMemo, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, AlertOctagon, HelpCircle, CheckCircle2, AlertTriangle, Copy, Share2, ChevronDown, ExternalLink, ArrowUpDown } from 'lucide-react';
import Link from 'next/link';
import { VerdictBadge } from '@/components/VerdictBadge';
import { ResultSkeleton } from '@/components/Skeleton';
import type { Source, Verdict, Confidence } from '@/types';
import { ResultErrorBoundary } from '@/components/ResultErrorBoundary';
import { FinancialResultView } from './FinancialResultView';
import { CartResultView } from './CartResultView';
import { ThreatResultView } from './ThreatResultView';
import { useToast } from '@/components/Toast';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const ENDPOINT_MAP: Record<string, string> = {
  verify: '/result',
  financial: '/financial-result',
  cart: '/price-result',
  security: '/threats/result',
};

type ResultData = {
  mode?: string;
  claim?: string;
  verdict?: Verdict;
  confidence?: Confidence;
  summary?: string;
  narrative_frame?: string;
  supports?: number;
  contradicts?: number;
  neutral?: number;
  bias_signals?: string[];
  source_diversity?: string;
  sources?: Source[];
};

function downloadResult(data: ResultData) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'factguard-report.json';
  a.click();
  URL.revokeObjectURL(a.href);
}

function AnimatedNumber({ value, label, color }: { value: number; label: string; color: string }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (value === 0) return;
    const duration = 800;
    const steps = 30;
    const increment = value / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplay(value);
        clearInterval(timer);
      } else {
        setDisplay(Math.round(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [value]);

  return (
    <div className="text-center">
      <motion.p
        key={display}
        initial={{ scale: 1.2, opacity: 0.5 }}
        animate={{ scale: 1, opacity: 1 }}
        className="text-3xl font-black font-mono"
        style={{ color }}
      >
        {display}
      </motion.p>
      <p className="text-xs uppercase tracking-wider mt-0.5" style={{ color: 'var(--color-text-tertiary)' }}>
        {label}
      </p>
    </div>
  );
}

export default function ResultPage({ params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = use(params);
  const searchParams = useSearchParams();
  const mode = searchParams.get('mode') || 'verify';
  const endpoint = ENDPOINT_MAP[mode] ?? '/result';

  const toast = useToast();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API result shape varies by mode
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState(false);
  const [showGraph, setShowGraph] = useState(false);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<'credibility' | 'relevance'>('relevance');
  const [showAllSources, setShowAllSources] = useState(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    const startedAt = Date.now();
    const MAX_POLL_MS = 120_000;
    const INITIAL_INTERVAL = 1000;
    const MAX_INTERVAL = 5000;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let abortController: AbortController | undefined;
    let currentInterval = INITIAL_INTERVAL;

    mountedRef.current = true;

    async function poll() {
      if (!mountedRef.current) return;

      if (Date.now() - startedAt > MAX_POLL_MS) {
        mountedRef.current && setError(true);
        return;
      }

      abortController?.abort();
      abortController = new AbortController();

      try {
        const res = await fetch(`${API_URL}${endpoint}/${jobId}`, {
          signal: abortController.signal,
        });
        if (!mountedRef.current) return;
        if (!res.ok) throw new Error(String(res.status));
        const result = await res.json();
        if (!mountedRef.current) return;

        if (result.status === 'processing') {
          currentInterval = Math.min(currentInterval * 1.5, MAX_INTERVAL);
          timer = setTimeout(poll, currentInterval);
          return;
        }

        if (result.status === 'error') {
          mountedRef.current && setError(true);
          return;
        }

        mountedRef.current && setData(result);
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return;
        console.error(err);
        if (!mountedRef.current) return;
        currentInterval = Math.min(currentInterval * 1.5, MAX_INTERVAL);
        timer = setTimeout(poll, currentInterval);
      }
    }

    timer = setTimeout(poll, INITIAL_INTERVAL);

    return () => {
      mountedRef.current = false;
      abortController?.abort();
      if (timer) clearTimeout(timer);
    };
  }, [jobId, endpoint, mode]);

  // eslint-disable-next-line react-hooks/preserve-manual-memoization
  const sortedSources = useMemo(() => {
    if (!data?.sources) return [];
    const copy = [...data.sources];
    copy.sort((a: Source, b: Source) => {
      if (a._hallucinated && !b._hallucinated) return 1;
      if (!a._hallucinated && b._hallucinated) return -1;
      if (sortKey === 'credibility') {
        const order = { High: 3, Medium: 2, Low: 1 };
        return (order[b.credibility] ?? 0) - (order[a.credibility] ?? 0);
      }
      return b.relevance - a.relevance;
    });
    return copy;
  }, [data?.sources, sortKey]);

  if (error) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4 px-6"
        style={{ backgroundColor: 'var(--color-bg-base)' }}
      >
        <p style={{ color: 'var(--color-text-secondary)' }}>Failed to load result</p>
        <button
          onClick={() => { setError(false); setData(null); window.location.reload(); }}
          className="px-4 py-2 text-sm font-semibold rounded-lg text-white transition-colors"
          style={{ backgroundColor: 'var(--color-accent-primary)' }}
        >
          Retry
        </button>
      </main>
    );
  }

  if (!data) return <ResultSkeleton />;

  if (mode === 'security' || data.mode === 'security') {
    return (
      <ResultErrorBoundary>
        <ThreatResultView data={data} />
      </ResultErrorBoundary>
    );
  }

  if (data.mode === 'financial') {
    return (
      <ResultErrorBoundary>
        <FinancialResultView data={data} />
      </ResultErrorBoundary>
    );
  }

  if (data.mode === 'cart') {
    return (
      <ResultErrorBoundary>
        <CartResultView data={data} />
      </ResultErrorBoundary>
    );
  }

  const VERDICT_CONFIG: Record<string, { color: string; icon: React.ElementType }> = {
    Verified: { color: '#10B981', icon: CheckCircle2 },
    'Likely True': { color: '#4F46E5', icon: ShieldCheck },
    'Mixed Evidence': { color: '#F59E0B', icon: HelpCircle },
    'Likely Misleading': { color: '#EF4444', icon: AlertOctagon },
    Unverified: { color: '#64748B', icon: HelpCircle },
  };

  const BIAS_LABELS: Record<string, { emoji: string; label: string }> = {
    cherry_picking: { emoji: '🍒', label: 'Cherry Picking' },
    false_equivalence: { emoji: '⚖', label: 'False Equivalence' },
    appeal_to_authority: { emoji: '👤', label: 'Authority Appeal' },
    omission: { emoji: '👁', label: 'Selective Omission' },
    misleading_statistics: { emoji: '📊', label: 'Statistical Distortion' },
    emotional_language: { emoji: '🔥', label: 'Emotional Language' },
    unverified_anecdote: { emoji: '💬', label: 'Unverified Anecdote' },
  };

  const validSources = (data.sources ?? []).filter((s: Source) => !s._hallucinated);
  const hallucinatedSources = (data.sources ?? []).filter((s: Source) => s._hallucinated);
  const supports = validSources.filter((s: Source) => s.stance === 'supports').length;
  const contradicts = validSources.filter((s: Source) => s.stance === 'contradicts').length;
  const neutral = validSources.filter((s: Source) => s.stance === 'neutral').length;
  const verdictCfg = VERDICT_CONFIG[data.verdict] ?? VERDICT_CONFIG.Unverified;
  const VerdictIcon = verdictCfg.icon;

  const diversityPercent = data.source_diversity === 'High' ? 92 : data.source_diversity === 'Medium' ? 60 : 30;
  const diversityColor = data.source_diversity === 'High' ? '#4F46E5' : data.source_diversity === 'Medium' ? '#F59E0B' : '#EF4444';

  const visibleSources = showAllSources ? sortedSources : sortedSources.slice(0, 10);

  /* eslint-disable react-hooks/purity -- relativeDate is a display-only formatter */
  const relativeDate = (iso: string) => {
    const ts = new Date(iso).getTime();
    if (isNaN(ts)) return '';
    const diff = (Date.now() - ts) / 1000;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };
  /* eslint-enable react-hooks/purity */

  const handleCopySummary = () => {
    const text = `FactGuard Analysis\nVerdict: ${data.verdict} (${data.confidence} confidence)\n\n${data.summary}`;
    navigator.clipboard?.writeText(text).catch(() => {});
    toast.success('Copied to clipboard', 'Summary copied with verdict');
  };

  const handleShare = () => {
    navigator.clipboard?.writeText(window.location.href).catch(() => {});
    toast.info('Link copied', 'Share this analysis link');
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="data-label mb-2">INTELLIGENCE REPORT · {jobId.toUpperCase()}</div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>Verification Analysis</h1>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* LEFT COLUMN */}
        <div className="lg:col-span-2 space-y-6">
          {/* Verdict hero */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: 'spring', stiffness: 100 }}
            className="rounded-2xl p-6"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="flex flex-col md:flex-row gap-6">
              <div className="flex-1">
                <div className="data-label mb-3">VERDICT</div>
                <div className="flex items-center gap-4 mb-4">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring' }}
                    className="relative"
                  >
                    <VerdictIcon className="w-16 h-16" style={{ color: verdictCfg.color }} />
                    <div
                      className="absolute inset-0 w-16 h-16 blur-2xl opacity-40"
                      style={{ backgroundColor: verdictCfg.color }}
                    />
                  </motion.div>
                  <div className="text-4xl sm:text-5xl font-black"
                    style={{ color: verdictCfg.color, textShadow: `0 0 30px ${verdictCfg.color}40` }}
                  >
                    {data.verdict}
                  </div>
                </div>

                {data.narrative_frame && (
                  <div className="border-l-[3px] pl-4 py-3 rounded-r-lg"
                    style={{ borderColor: 'var(--color-accent-primary)', backgroundColor: 'rgba(99,102,241,0.05)' }}
                  >
                    <div className="font-mono text-sm italic" style={{ color: 'var(--color-text-secondary)' }}>
                      {data.narrative_frame}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-3 md:w-64">
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg border"
                  style={{ borderColor: 'var(--color-border-default)', backgroundColor: `${verdictCfg.color}10` }}
                >
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: verdictCfg.color }} />
                  <span className="data-label">CONFIDENCE · {(data.confidence ?? 'Low').toUpperCase()}</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="p-2 rounded-lg border border-[var(--color-border-subtle)] text-center">
                    <div className="font-mono text-2xl font-bold" style={{ color: 'var(--color-accent-emerald)' }}>
                      {supports}
                    </div>
                    <div className="data-label">SUPPORT</div>
                  </div>
                  <div className="p-2 rounded-lg border border-[var(--color-border-subtle)] text-center">
                    <div className="font-mono text-2xl font-bold" style={{ color: 'var(--color-text-secondary)' }}>
                      {neutral}
                    </div>
                    <div className="data-label">NEUTRAL</div>
                  </div>
                  <div className="p-2 rounded-lg border border-[var(--color-border-subtle)] text-center">
                    <div className="font-mono text-2xl font-bold" style={{ color: 'var(--color-accent-red)' }}>
                      {contradicts}
                    </div>
                    <div className="data-label">CONTRADICT</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Summary */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="data-label mb-3">INTELLIGENCE SUMMARY</div>
            <p className="leading-relaxed text-justify" style={{ color: 'var(--color-text-primary)' }}>
              {data.summary}
            </p>
          </motion.div>

          {/* Sources table */}
          {data.sources?.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="rounded-2xl overflow-hidden"
              style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
            >
              <div className="px-4 py-3 border-b border-[var(--color-border-subtle)] flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>Evidential Sources</div>
                  <div className="data-label mt-0.5">{validSources.length + hallucinatedSources.length} sources analysed</div>
                    {hallucinatedSources.length > 0 && (
                      <div className="data-label mt-0.5" style={{ color: 'var(--color-accent-red)' }}>
                        {hallucinatedSources.length} failed URL validation
                      </div>
                    )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="data-label">Sort by:</span>
                  <select
                    value={sortKey}
                    onChange={(e) => setSortKey(e.target.value as 'credibility' | 'relevance')}
                    className="bg-[var(--color-bg-elevated)] border border-[var(--color-border-default)] rounded px-2 py-1 text-xs outline-none"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    <option value="relevance">Relevance</option>
                    <option value="credibility">Credibility</option>
                  </select>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[var(--color-border-subtle)]">
                      <th className="data-label text-left py-2 px-4 font-medium">#</th>
                      <th className="data-label text-left py-2 px-4 font-medium">Source</th>
                      <th className="data-label text-left py-2 px-4 font-medium cursor-pointer" onClick={() => setSortKey('credibility')}>
                        Credibility <ArrowUpDown className="inline w-3 h-3 ml-1" />
                      </th>
                      <th className="data-label text-left py-2 px-4 font-medium">Stance</th>
                      <th className="data-label text-left py-2 px-4 font-medium cursor-pointer" onClick={() => setSortKey('relevance')}>
                        Relevance <ArrowUpDown className="inline w-3 h-3 ml-1" />
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleSources.map((source: Source, i: number) => {
                      const stanceColor = source.stance === 'supports'
                        ? 'text-emerald-400 bg-emerald-500/10'
                        : source.stance === 'contradicts'
                        ? 'text-red-400 bg-red-500/10'
                        : 'text-slate-400 bg-slate-500/10';
                      const credColor = source.credibility === 'High'
                        ? 'text-emerald-400'
                        : source.credibility === 'Medium'
                        ? 'text-amber-400'
                        : 'text-red-400';
                      const isExpanded = expandedRow === `${source.url}-${i}`;
                      return (
                        <motion.tr
                          key={`${source.url}-${i}`}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.04, duration: 0.3 }}
                          className="border-b border-[var(--color-border-subtle)] hover:bg-[var(--color-bg-elevated)]/50 transition-colors cursor-pointer"
                          onClick={() => setExpandedRow(isExpanded ? null : `${source.url}-${i}`)}
                        >
                          <td className="py-3 px-4 align-top">
                            <span className="data-label inline-block px-1.5 py-0.5 rounded border"
                              style={{
                                color: source.tier === 1 ? 'var(--color-accent-emerald)' : source.tier === 2 ? 'var(--color-accent-primary)' : source.tier === 3 ? 'var(--color-accent-amber)' : 'var(--color-text-tertiary)',
                                borderColor: source.tier === 1 ? 'rgba(16,185,129,0.3)' : source.tier === 2 ? 'rgba(79,70,229,0.3)' : source.tier === 3 ? 'rgba(245,158,11,0.3)' : 'rgba(126,143,173,0.3)',
                              }}
                            >TIER {source.tier}</span>
                          </td>
                          <td className="py-3 px-4 align-top max-w-[300px]">
                            <div className="flex items-start gap-2">
                              <div className="w-6 h-6 rounded flex items-center justify-center text-[10px] font-mono shrink-0"
                                style={{ backgroundColor: 'var(--color-bg-elevated)', color: 'var(--color-text-secondary)' }}
                              >
                                {(() => { try { return source.url ? new URL(source.url).hostname[0].toUpperCase() : 'S' } catch { return 'S' } })()}
                              </div>
                              <div className="min-w-0 flex-1">
                                <div className="text-sm line-clamp-1" style={{ color: 'var(--color-text-primary)' }}>
                                  {source.title}
                                  {source._hallucinated && (
                                    <span className="ml-2 inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase"
                                      style={{ backgroundColor: 'rgba(239,68,68,0.15)', color: '#EF4444' }}
                                    >
                                      FAILED
                                    </span>
                                  )}
                                </div>
                                <div className="data-label mt-0.5">
                                  {(() => { try { return source.url ? new URL(source.url).hostname : '' } catch { return '' } })()}
                                  {source.url && (
                                    <a
                                      href={source.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      onClick={(e) => e.stopPropagation()}
                                      className="ml-1.5 inline-flex items-center gap-0.5 hover:text-[var(--color-accent-primary)] transition-colors align-middle"
                                    >
                                      <ExternalLink className="w-2.5 h-2.5" />
                                    </a>
                                  )}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-4 align-top">
                            <span className={`text-xs font-semibold ${credColor}`}>{source.credibility}</span>
                          </td>
                          <td className="py-3 px-4 align-top">
                            <span className={`text-xs px-2 py-0.5 rounded-full uppercase tracking-wider ${stanceColor}`}>
                              {source.stance}
                            </span>
                          </td>
                          <td className="py-3 px-4 align-top">
                            <div className="flex items-center gap-2">
                              <div className="w-16 h-1 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-bg-elevated)' }}>
                                <div className="h-full" style={{ backgroundColor: 'var(--color-accent-primary)', width: `${source.relevance * 10}%` }} />
                              </div>
                              <span className="data-label font-mono">{source.relevance.toFixed(1)}</span>
                            </div>
                          </td>
                          {isExpanded && (
                            <td colSpan={5} className="py-4 px-4" style={{ backgroundColor: 'rgba(99,102,241,0.03)' }}>
                              <div className="text-sm mb-2" style={{ color: 'var(--color-text-secondary)' }}>{source.summary}</div>
                              {source.quote && (
                                <blockquote className="border-l-2 border-[var(--color-accent-primary)] pl-3 italic text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                                  &ldquo;{source.quote}&rdquo;
                                </blockquote>
                              )}
                            </td>
                          )}
                        </motion.tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {sortedSources.length > 10 && (
                <div className="p-3 border-t border-[var(--color-border-subtle)] text-center">
                  <button
                    onClick={() => setShowAllSources(!showAllSources)}
                    className="text-xs transition-colors"
                    style={{ color: 'var(--color-accent-primary)' }}
                  >
                    {showAllSources ? 'Show less' : `Show all ${sortedSources.length} sources →`}
                  </button>
                </div>
              )}
            </motion.div>
          )}
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-6">
          {/* Bias signals */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="rounded-2xl p-4"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3 flex items-center gap-2">
              <AlertTriangle className="w-3 h-3" />
              BIAS SIGNALS DETECTED
            </div>
            {!data.bias_signals || data.bias_signals.length === 0 ? (
              <div className="text-center py-4">
                <ShieldCheck className="w-8 h-8 mx-auto mb-2" style={{ color: 'var(--color-accent-emerald)' }} />
                <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>No manipulation tactics detected</div>
              </div>
            ) : (
              <div className="space-y-2">
                {data.bias_signals.map((signal: string, i: number) => {
                  const meta = BIAS_LABELS[signal] || { emoji: '⚠', label: signal };
                  return (
                    <motion.div
                      key={signal}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + i * 0.05 }}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg"
                      style={{ backgroundColor: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.2)' }}
                    >
                      <span className="text-base">{meta.emoji}</span>
                      <span className="text-xs font-medium" style={{ color: 'var(--color-accent-amber)' }}>{meta.label}</span>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </motion.div>

          {/* Source diversity */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="rounded-2xl p-4"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3">SOURCE ECOSYSTEM</div>
            <div className="flex items-center justify-center my-4">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" stroke="rgba(99, 102, 241, 0.1)" strokeWidth="6" fill="none" />
                  <motion.circle
                    cx="50" cy="50" r="45"
                    stroke={diversityColor}
                    strokeWidth="6" fill="none" strokeLinecap="round"
                    strokeDasharray={`${(diversityPercent / 100) * 283} 283`}
                    initial={{ strokeDashoffset: 283 }}
                    animate={{ strokeDashoffset: 0 }}
                    transition={{ duration: 1.5, ease: 'easeOut' }}
                    style={{ filter: `drop-shadow(0 0 4px ${diversityColor})` }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <div className="font-mono text-2xl font-bold" style={{ color: diversityColor }}>
                    {diversityPercent}%
                  </div>
                  <div className="data-label">{data.source_diversity}</div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Export */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="rounded-2xl p-4"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3">EXPORT INTELLIGENCE</div>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={handleCopySummary}
                className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg border text-xs transition-colors"
                style={{
                  borderColor: 'var(--color-border-default)',
                  color: 'var(--color-text-primary)',
                }}
              >
                <Copy className="w-3.5 h-3.5" /> Copy Summary
              </button>
              <button
                onClick={handleShare}
                className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg border text-xs transition-colors"
                style={{
                  borderColor: 'var(--color-border-default)',
                  color: 'var(--color-text-primary)',
                }}
              >
                <Share2 className="w-3.5 h-3.5" /> Share Link
              </button>
            </div>
          </motion.div>

          {/* Claim echo */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="rounded-2xl p-4"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-2">ANALYSED CLAIM</div>
            <blockquote className="border-l-2 border-[var(--color-accent-primary)] pl-3 italic text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              &ldquo;{data.claim}&rdquo;
            </blockquote>
            <div className="data-label mt-2 font-mono flex items-center gap-2">
              <ExternalLink className="w-3 h-3" />
              {data.createdAt ? relativeDate(data.createdAt) : ''}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
