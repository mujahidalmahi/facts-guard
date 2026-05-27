'use client';

import { motion } from 'framer-motion';
import { Area, AreaChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, ArrowRight, AlertTriangle, CheckCircle2, ExternalLink, Activity } from 'lucide-react';
import type { FinancialResult, FinancialSource } from '@/types';

function formatDate(d: string) {
  const date = new Date(d);
  return `${date.getMonth() + 1}/${date.getDate()}`;
}

function formatPrice(p: number) {
  if (p >= 1000) return `$${(p / 1000).toFixed(1)}k`;
  return `$${p.toFixed(2)}`;
}

export function FinancialResultView({ data }: { data: FinancialResult }) {
  const { graph_data, analysis } = data;
  const isPositive = graph_data?.change_24h?.startsWith('+') ?? true;
  const lineColor = isPositive ? '#10B981' : '#EF4444';

  const avgPrice = graph_data?.data?.length
    ? graph_data.data.reduce((sum, d) => sum + d.price, 0) / graph_data.data.length
    : 0;

  const signalColor = analysis.signal === 'Bullish' ? '#10B981' : analysis.signal === 'Bearish' ? '#EF4444' : '#F59E0B';
  const SignalIcon = analysis.signal === 'Bullish' ? TrendingUp : analysis.signal === 'Bearish' ? TrendingDown : ArrowRight;
  const TrendIcon = analysis.price_trend === 'Up' ? ArrowUpRight : analysis.price_trend === 'Down' ? ArrowDownRight : ArrowRight;
  const trendColor = analysis.price_trend === 'Up' ? '#10B981' : analysis.price_trend === 'Down' ? '#EF4444' : '#F59E0B';
  const riskColor = analysis.risk_level === 'Low' ? '#10B981' : analysis.risk_level === 'Medium' ? '#F59E0B' : '#EF4444';
  const freshnessLive = analysis.data_freshness === 'real-time';

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="data-label mb-2">MARKET SIGNAL REPORT</div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>Financial Analysis</h1>
      </motion.div>

      <div className="grid lg:grid-cols-5 gap-6">
        {/* Chart area - 3 cols */}
        <div className="lg:col-span-3 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl p-6"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="flex items-start justify-between mb-6 flex-wrap gap-4">
              <div>
                <div className="data-label mb-1">{graph_data?.label} · {analysis.asset}</div>
                <div className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>
                  {graph_data?.label}
                </div>
                <div className="flex items-baseline gap-3 mt-1">
                  <div className="font-mono text-4xl font-black" style={{ color: 'var(--color-text-primary)' }}>
                    ${graph_data?.current_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '0.00'}
                  </div>
                  {graph_data?.change_24h && (
                    <div className={`flex items-center gap-1 px-2 py-1 rounded text-sm font-semibold ${isPositive ? 'bg-emerald-500/10 text-[var(--color-accent-emerald)]' : 'bg-red-500/10 text-[var(--color-accent-red)]'}`}>
                      {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                      {graph_data.change_24h}
                    </div>
                  )}
                </div>
                <div className="data-label mt-1 flex items-center gap-3">
                  {graph_data?.change_7d && <span>7d: <span className={graph_data.change_7d.startsWith('+') ? 'text-[var(--color-accent-emerald)]' : 'text-[var(--color-accent-red)]'}>{graph_data.change_7d}</span></span>}
                  {graph_data?.all_time_high && <span>ATH: <span className="font-mono">${graph_data.all_time_high.toLocaleString()}</span></span>}
                </div>
              </div>
              {analysis.data_freshness && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full"
                  style={{
                    backgroundColor: freshnessLive ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                    border: freshnessLive ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(245, 158, 11, 0.3)',
                  }}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${freshnessLive ? 'bg-[var(--color-accent-emerald)]' : 'bg-[var(--color-accent-amber)]'}`} />
                  <span className="data-label" style={{ color: freshnessLive ? '#10B981' : '#F59E0B' }}>
                    {freshnessLive ? 'LIVE' : analysis.data_freshness.toUpperCase()}
                  </span>
                </div>
              )}
            </div>

            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={graph_data?.data ?? []} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={lineColor} stopOpacity={0.3} />
                      <stop offset="100%" stopColor={lineColor} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(99, 102, 241, 0.08)" vertical={false} />
                  <XAxis dataKey="date" tickFormatter={formatDate} stroke="#3D4F6B" style={{ fontFamily: 'DM Mono', fontSize: 10 }} tickLine={false} axisLine={false} />
                  <YAxis domain={['dataMin - 500', 'dataMax + 500']} tickFormatter={(v: number) => formatPrice(v)} stroke="#3D4F6B" style={{ fontFamily: 'DM Mono', fontSize: 10 }} tickLine={false} axisLine={false} orientation="right" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 30, 53, 0.95)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: 8, fontFamily: 'DM Mono', fontSize: 12 }} labelStyle={{ color: '#7E8FAD', marginBottom: 4 }} formatter={(value) => [`$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2 })}`, 'Price']} />
                  <ReferenceLine y={avgPrice} stroke="#7E8FAD" strokeDasharray="4 4" label={{ value: 'AVG', position: 'left', style: { fontFamily: 'DM Mono', fontSize: 9, fill: '#7E8FAD' } }} />
                  <Area type="monotone" dataKey="price" stroke={lineColor} strokeWidth={2} fill="url(#priceGradient)" animationDuration={1500} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="rounded-2xl p-6"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3">MARKET INTELLIGENCE</div>
            <p className="leading-relaxed" style={{ color: 'var(--color-text-primary)' }}>{analysis.summary}</p>
          </motion.div>
        </div>

        {/* Signal panel - 2 cols */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="rounded-2xl p-5"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3">SIGNAL</div>
            <div className="flex items-center gap-4 mb-4">
              <div className="relative">
                <SignalIcon className="w-12 h-12" style={{ color: signalColor }} />
                <div className="absolute inset-0 w-12 h-12 blur-xl opacity-40" style={{ backgroundColor: signalColor }} />
              </div>
              <div>
                <div className="text-3xl font-black" style={{ color: signalColor, textShadow: `0 0 20px ${signalColor}60`, fontFamily: 'var(--font-sora)' }}>
                  {analysis.signal.toUpperCase()}
                </div>
                <div className="data-label mt-1">Strength: {analysis.signal_strength}/100</div>
              </div>
            </div>

            <div className="mb-4">
              <div className="h-1.5 overflow-hidden rounded-full" style={{ backgroundColor: 'var(--color-bg-elevated)' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${analysis.signal_strength}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: signalColor, boxShadow: `0 0 8px ${signalColor}` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="p-3 rounded-lg border" style={{ borderColor: 'var(--color-border-subtle)' }}>
                <div className="data-label mb-1">PRICE TREND</div>
                <div className="flex items-center gap-1">
                  <TrendIcon className="w-4 h-4" style={{ color: trendColor }} />
                  <span className="text-sm font-semibold" style={{ color: trendColor }}>
                    {analysis.price_trend === 'Up' ? 'Strong Up' : analysis.price_trend === 'Down' ? 'Moderate Down' : 'Sideways'}
                  </span>
                </div>
              </div>
              <div className="p-3 rounded-lg border" style={{ borderColor: 'var(--color-border-subtle)' }}>
                <div className="data-label mb-1">RISK LEVEL</div>
                <div className="flex items-center gap-1">
                  <AlertTriangle className="w-4 h-4" style={{ color: riskColor }} />
                  <span className="text-sm font-semibold" style={{ color: riskColor }}>{analysis.risk_level}</span>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="rounded-2xl p-5"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3 flex items-center gap-2">
              <Activity className="w-3 h-3" />
              30-DAY PREDICTION
            </div>
            <div className="space-y-3">
              {analysis.prediction_30d && (
                <>
                  <div className="border-l-[3px] pl-3 py-1" style={{ borderColor: '#10B981' }}>
                    <div className="data-label mb-1" style={{ color: 'var(--color-accent-emerald)' }}>BULL CASE</div>
                    <div className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>{analysis.prediction_30d.bull_case}</div>
                  </div>
                  <div className="border-l-[3px] pl-3 py-1" style={{ borderColor: '#4F46E5' }}>
                    <div className="data-label mb-1" style={{ color: 'var(--color-accent-primary)' }}>BASE CASE</div>
                    <div className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>{analysis.prediction_30d.base_case}</div>
                  </div>
                  <div className="border-l-[3px] pl-3 py-1" style={{ borderColor: '#EF4444' }}>
                    <div className="data-label mb-1" style={{ color: 'var(--color-accent-red)' }}>BEAR CASE</div>
                    <div className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>{analysis.prediction_30d.bear_case}</div>
                  </div>
                </>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="rounded-2xl p-5"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3">KEY FACTORS</div>
            <div className="space-y-2">
              {analysis.key_factors?.map((factor, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.05 }}
                  className="flex items-start gap-2 text-xs"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  <CheckCircle2 className="w-3.5 h-3.5 shrink-0 mt-0.5" style={{ color: 'var(--color-accent-primary)' }} />
                  <span className="leading-relaxed">{factor}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="rounded-2xl p-5"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3">RISK CATALYSTS</div>
            <div className="space-y-2">
              {analysis.risk_catalysts?.map((cat, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.05 }}
                  className="flex items-start gap-2 p-2 rounded text-xs leading-relaxed"
                  style={{ backgroundColor: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.1)', color: 'var(--color-text-secondary)' }}
                >
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" style={{ color: 'var(--color-accent-amber)' }} />
                  <span>{cat}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="rounded-2xl p-5"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <div className="data-label mb-3">SOURCES ({data.sources?.length ?? 0})</div>
            <div className="space-y-2">
              {data.sources?.map((source: FinancialSource, i: number) => (
                <a
                  key={i}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 py-1.5 transition-colors group"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  <div className="w-5 h-5 rounded flex items-center justify-center text-[9px] font-mono shrink-0"
                    style={{ backgroundColor: 'var(--color-bg-elevated)', color: 'var(--color-text-tertiary)' }}
                  >S</div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs truncate transition-colors group-hover:text-[var(--color-accent-primary)]" style={{ color: 'var(--color-text-primary)' }}>
                      {source.title}
                    </div>
                    {source.date && <div className="data-label font-mono mt-0.5">{source.date}</div>}
                  </div>
                  <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: 'var(--color-text-tertiary)' }} />
                </a>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
