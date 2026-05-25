'use client';

import { motion } from 'framer-motion';
import { PriceChart } from '@/components/PriceChart';
import { SignalBadge } from '@/components/SignalBadge';

const RISK_COLOR: Record<string, string> = {
  Low: 'text-emerald-500',
  Medium: 'text-amber-500',
  High: 'text-red-500',
};

const TREND_COLOR: Record<string, string> = {
  Up: 'text-emerald-500',
  Down: 'text-red-500',
  Sideways: 'text-slate-400',
};

const FRESHNESS_COLOR: Record<string, string> = {
  'real-time': 'text-emerald-400',
  intraday: 'text-emerald-300',
  daily: 'text-amber-400',
  stale: 'text-red-400',
};

export function FinancialResultView({
  data,
}: {
  data: any;
}) {
  const a = data.analysis;

  return (
    <main className='max-w-3xl mx-auto px-4 py-10 space-y-8'>
      {/* Hero */}
      <motion.div
        className='flex flex-wrap items-center gap-3'
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      >
        <SignalBadge signal={a.signal} />

        {a.signal_strength != null && (
          <div className="relative inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20">
            <svg className="w-6 h-6 -rotate-90" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" strokeWidth="3" className="text-indigo-500/20" />
              <circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" strokeWidth="3"
                strokeDasharray={`${(a.signal_strength / 100) * 94.2} 94.2`}
                className="text-indigo-400" strokeLinecap="round" />
            </svg>
            <span className="text-xs font-bold font-mono text-indigo-300">{a.signal_strength}</span>
          </div>
        )}

        <span className={`text-sm font-semibold ${TREND_COLOR[a.price_trend] || 'text-slate-400'}`}>
          {a.price_trend} {a.trend_magnitude ? `(${a.trend_magnitude})` : ''}
        </span>

        <span className={`text-sm font-semibold ${RISK_COLOR[a.risk_level] || ''}`}>
          {a.risk_level} Risk
        </span>

        {a.data_freshness && (
          <span className={`text-[10px] font-mono font-semibold uppercase tracking-wider ${FRESHNESS_COLOR[a.data_freshness] || 'text-slate-400'}`}>
            <span className={`inline-block w-1.5 h-1.5 rounded-full mr-1 ${
              a.data_freshness === 'real-time' ? 'bg-emerald-400 pulse-ring' :
              a.data_freshness === 'stale' ? 'bg-red-400' : 'bg-amber-400'
            }`} />
            {a.data_freshness}
          </span>
        )}
      </motion.div>

      {/* Price Chart */}
      {data.graph_data?.data?.length > 0 && (
        <PriceChart data={data.graph_data} />
      )}

      {/* Summary */}
      <p className='text-[var(--foreground)] leading-relaxed text-base'>
        {a.summary}
      </p>

      {/* Key Factors */}
      {a.key_factors?.length > 0 && (
        <section>
          <h2 className='text-sm font-semibold uppercase tracking-wide text-[var(--muted-foreground)] mb-3'>
            Key Factors
          </h2>
          <div className='flex flex-wrap gap-2'>
            {a.key_factors.map((f: string, i: number) => (
              <span key={i} className='px-3 py-1 rounded-full text-sm bg-[var(--card)] border border-[var(--card-border)] text-[var(--foreground)]'>
                {f}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Risk Catalysts */}
      {a.risk_catalysts?.length > 0 && (
        <section>
          <h2 className='text-sm font-semibold uppercase tracking-wide text-red-400 mb-3'>
            Risk Catalysts
          </h2>
          <div className='space-y-2'>
            {a.risk_catalysts.map((r: string, i: number) => (
              <div key={i} className='flex items-start gap-2 p-3 rounded-xl bg-red-950/30 border border-red-800/40'>
                <span className='text-red-400 text-sm font-bold mt-0.5'>!</span>
                <p className='text-sm text-red-300'>{r}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 30-Day Prediction */}
      {a.prediction_30d && (
        <div className='grid grid-cols-1 sm:grid-cols-3 gap-3'>
          {['bull_case', 'base_case', 'bear_case'].map((key) => {
            const label = key === 'bull_case' ? 'Bull Case' : key === 'base_case' ? 'Base Case' : 'Bear Case';
            const color = key === 'bull_case' ? 'border-emerald-500/30 bg-emerald-950/20' :
              key === 'base_case' ? 'border-indigo-500/30 bg-indigo-950/20' :
              'border-red-500/30 bg-red-950/20';
            const textColor = key === 'bull_case' ? 'text-emerald-300' :
              key === 'base_case' ? 'text-indigo-300' :
              'text-red-300';
            return (
              <div key={key} className={`rounded-xl border ${color} p-4 backdrop-blur-sm`}>
                <p className={`text-xs font-bold uppercase tracking-wider ${textColor} mb-1`}>{label}</p>
                <p className='text-sm text-slate-300'>{a.prediction_30d[key] || 'N/A'}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Sources */}
      {a.sources?.length > 0 && (
        <section>
          <h2 className='text-lg font-semibold mb-3'>Market Sources</h2>
          <div className='space-y-3'>
            {a.sources.map((s: any, i: number) => (
              <a key={i} href={s.url} target='_blank' rel='noopener noreferrer'
                className='flex items-start gap-3 p-3 rounded-xl border border-[var(--card-border)] bg-[var(--card)] hover:bg-[var(--muted)] transition-colors group'
              >
                <div className='flex-1 min-w-0'>
                  <p className='text-sm font-medium group-hover:text-[var(--accent)] transition-colors truncate'>{s.title}</p>
                  {s.date && <p className='text-xs text-[var(--muted-foreground)] mt-0.5'>{s.date}</p>}
                </div>
              </a>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
