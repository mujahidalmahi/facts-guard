'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { useJobPolling } from '@/lib/useJobPolling';

const STEPS: Record<
  string,
  string[]
> = {
  verify: [
    'Checking cache...',
    'Searching via Bright Data...',
    'Analysing with AI...',
    'Saving results...',
  ],

  financial: [
    'Fetching market data...',
    'Scraping news via BrightData...',
    'Running AI analysis...',
    'Generating chart...',
  ],

  cart: [
    'Scanning platforms via BrightData...',
    'Comparing prices...',
    'Checking trust signals...',
    'Generating recommendation...',
  ],
};

const DESC_MAP: Record<
  string,
  string
> = {
  verify:
    'Scanning trusted sources for evidence...',

  financial:
    'Fetching live market data and running AI analysis...',

  cart:
    'Comparing prices across multiple platforms...',
};

const ROUTE_MAP: Record<
  string,
  string
> = {
  verify: 'result',
  financial: 'result',
  cart: 'result',
};

const STEP_ICONS: Record<
  string,
  string
> = {
  verify: '\uD83D\uDD0D',
  financial: '\uD83D\uDCC8',
  cart: '\uD83D\uDED2',
};

function LoadingContent() {
  const searchParams =
    useSearchParams();

  const jobId =
    searchParams.get(
      'job'
    ) || 'demo';

  const mode =
    searchParams.get(
      'mode'
    ) || 'verify';

  const steps =
    STEPS[mode] ??
    STEPS.verify;

  const route =
    ROUTE_MAP[mode] ??
    'result';

  const {
    progress,
    icon,
  } = useJobPolling(
    jobId,
    route,
    steps,
    mode
  );

  const stepIndex =
    steps.indexOf(
      progress
    );

  const pct =
    stepIndex >= 0
      ? (
          (stepIndex + 1) /
          steps.length
        ) * 100
      : 15;

  return (
    <main className='min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center bg-[var(--background)] px-6'>
      <div className='text-center max-w-md w-full flex-1 flex flex-col items-center justify-center'>
        <motion.div
          animate={{
            rotate: 360,
          }}
          transition={{
            repeat:
              Infinity,
            duration: 1.4,
            ease: 'linear',
          }}
          className='mx-auto h-16 w-16 rounded-full border-4 border-[var(--card-border)] border-t-[var(--accent)]'
        />

        <motion.h1
          key={progress}
          initial={{
            opacity: 0,
            y: 8,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          className='mt-8 text-2xl font-semibold text-[var(--foreground)]'
        >
          {icon}{' '}
          {progress}
        </motion.h1>

        <p className='mt-3 text-[var(--muted-foreground)]'>
          {DESC_MAP[
            mode
          ] ??
            DESC_MAP.verify}
        </p>

        <div className='mt-8 h-2 bg-[var(--muted)] rounded-full overflow-hidden w-full'>
          <motion.div
            initial={{
              width: '0%',
            }}
            animate={{
              width: `${pct}%`,
            }}
            className='h-full bg-[var(--accent)]'
          />
        </div>

        <div className='mt-8 space-y-3 w-full'>
          {steps.map(
            (
              step,
              i
            ) => (
              <div
                key={step}
                className='flex items-center gap-3 text-left'
              >
                <motion.div
                  initial={{
                    scale: 0,
                  }}
                  animate={{
                    scale:
                      i <=
                      stepIndex
                        ? 1
                        : 0.4,
                  }}
                  className={`w-2 h-2 rounded-full shrink-0 ${
                    i <
                    stepIndex
                      ? 'bg-emerald-500'
                      : i ===
                        stepIndex
                      ? 'bg-indigo-400 pulse-ring'
                      : 'bg-slate-600'
                  }`}
                />
                <span
                  className={`text-sm font-mono ${
                    i <=
                    stepIndex
                      ? 'text-[var(--foreground)]'
                      : 'text-[var(--muted-foreground)]'
                  }`}
                >
                  {step}
                </span>
              </div>
            )
          )}
        </div>
      </div>

      <footer className='w-full text-center py-4 border-t border-[var(--card-border)] mt-auto'>
        <p className='text-xs text-[var(--muted-foreground)]'>
          Powered by{' '}
          <span className='text-indigo-400 font-semibold'>
            BrightData
          </span>{' '}
          \u00B7 Real-time web intelligence
        </p>
      </footer>
    </main>
  );
}

export default function LoadingPage() {
  return (
    <Suspense fallback={null}>
      <LoadingContent />
    </Suspense>
  );
}
