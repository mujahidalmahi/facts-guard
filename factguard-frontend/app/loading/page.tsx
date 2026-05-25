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
    'Scraping news...',
    'Running AI analysis...',
    'Generating chart...',
  ],

  cart: [
    'Scanning platforms...',
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

/**
 * Unified result routing
 * Everything now goes through:
 * /result/{jobId}?mode=...
 */
const ROUTE_MAP: Record<
  string,
  string
> = {
  verify: 'result',
  financial: 'result',
  cart: 'result',
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
    <main className='min-h-[calc(100vh-3.5rem)] flex items-center justify-center bg-[var(--background)] px-6'>
      <div className='text-center max-w-md w-full'>
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

        <div className='mt-8 h-2 bg-[var(--muted)] rounded-full overflow-hidden'>
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
      </div>
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