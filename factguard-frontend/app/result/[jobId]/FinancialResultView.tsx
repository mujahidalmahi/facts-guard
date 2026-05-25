'use client';

import { motion } from 'framer-motion';
import { PriceChart } from '@/components/PriceChart';
import { SignalBadge } from '@/components/SignalBadge';
import { ConfidencePill } from '@/components/ConfidencePill';

import type {
  FinancialResult,
  Confidence,
} from '@/types';

const RISK_COLOR = {
  Low: 'text-emerald-500',
  Medium: 'text-amber-500',
  High: 'text-red-500',
};

const TREND_COLOR = {
  Bullish: 'text-emerald-500',
  Bearish: 'text-red-500',
  Sideways: 'text-slate-400',
};

const CRED_COLOR = {
  High: 'bg-emerald-700',
  Medium: 'bg-amber-600',
  Low: 'bg-red-600',
};

export function FinancialResultView({
  data,
}: {
  data: FinancialResult;
}) {
  const a = data.analysis;

  return (
    <main className='max-w-3xl mx-auto px-4 py-10 space-y-8'>
      {/* Hero */}
      <motion.div
        className='flex flex-wrap items-center gap-3'
        initial={{
          opacity: 0,
          y: 16,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          type: 'spring',
          stiffness: 260,
          damping: 20,
        }}
      >
        <SignalBadge
          signal={a.signal}
        />

        <ConfidencePill
          confidence={
            a.confidence as Confidence
          }
        />

        <span
          className={`text-sm font-semibold ${
            TREND_COLOR[
              a.price_trend
            ]
          }`}
        >
          {a.price_trend}
        </span>

        <span
          className={`text-sm font-semibold ${
            RISK_COLOR[
              a.risk_level
            ]
          }`}
        >
          {a.risk_level} Risk
        </span>
      </motion.div>

      {/* Price Chart */}
      {data.graph_data?.data
        ?.length > 0 && (
        <PriceChart
          data={data.graph_data}
        />
      )}

      {/* Summary */}
      <p className='text-[var(--foreground)] leading-relaxed text-base'>
        {a.summary}
      </p>

      {/* Key Factors */}
      {a.key_factors?.length >
        0 && (
        <section>
          <h2
            className='text-sm font-semibold
            uppercase tracking-wide
            text-[var(--muted-foreground)]
            mb-3'
          >
            Key Factors
          </h2>

          <div className='flex flex-wrap gap-2'>
            {a.key_factors.map(
              (f, i) => (
                <span
                  key={i}
                  className='px-3 py-1 rounded-full
                  text-sm bg-[var(--card)]
                  border border-[var(--card-border)]
                  text-[var(--foreground)]'
                >
                  {f}
                </span>
              )
            )}
          </div>
        </section>
      )}

      {/* 30-Day Prediction */}
      <div
        className='rounded-xl border
        border-[var(--card-border)]
        bg-[var(--card)] p-4'
      >
        <p
          className='text-xs font-semibold
          uppercase tracking-wide
          text-[var(--muted-foreground)]
          mb-1'
        >
          30-Day Outlook
        </p>

        <p className='text-sm text-[var(--foreground)]'>
          {a.prediction_30d}
        </p>
      </div>

      {/* Sources */}
      <section>
        <h2 className='text-lg font-semibold mb-3'>
          Market Sources
        </h2>

        <div className='space-y-3'>
          {data.sources?.map(
            (s, i) => (
              <a
                key={i}
                href={s.url}
                target='_blank'
                rel='noopener noreferrer'
                className='flex items-start gap-3
                p-3 rounded-xl border
                border-[var(--card-border)]
                bg-[var(--card)]
                hover:bg-[var(--muted)]
                transition-colors group'
              >
                <span
                  className={`shrink-0 mt-0.5 px-2 py-0.5
                  rounded text-xs font-bold
                  text-white ${
                    CRED_COLOR[
                      s.credibility
                    ] ??
                    'bg-slate-600'
                  }`}
                >
                  {s.credibility}
                </span>

                <div className='flex-1 min-w-0'>
                  <p
                    className='text-sm font-medium
                    group-hover:text-[var(--accent)]
                    transition-colors truncate'
                  >
                    {s.title}
                  </p>

                  <p
                    className='text-xs
                    text-[var(--muted-foreground)]
                    mt-0.5'
                  >
                    {s.stance} · {s.date}
                  </p>

                  <p
                    className='text-xs
                    text-[var(--foreground)]
                    mt-1 line-clamp-2'
                  >
                    {s.summary}
                  </p>
                </div>
              </a>
            )
          )}
        </div>
      </section>
    </main>
  );
}