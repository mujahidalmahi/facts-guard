'use client';

import {
  use,
  useEffect,
  useState,
} from 'react';

import {
  useSearchParams,
} from 'next/navigation';

import { motion } from 'framer-motion';
import { Download } from 'lucide-react';

import {
  VerdictBadge,
} from '@/components/VerdictBadge';

import {
  ConfidencePill,
} from '@/components/ConfidencePill';

import {
  AgreementMeter,
} from '@/components/AgreementMeter';

import {
  EvidenceTimeline,
} from '@/components/EvidenceTimeline';

import {
  ShareCard,
} from '@/components/ShareCard';

import {
  ResultSkeleton,
} from '@/components/Skeleton';

import {
  Source,
  Verdict,
  Confidence,
} from '@/types';

import {
  ResultErrorBoundary,
} from '@/components/ResultErrorBoundary';

import {
  FinancialResultView,
} from './FinancialResultView';

import {
  CartResultView,
} from './CartResultView';

const API_URL =
  process.env
    .NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

/**
 * Unified endpoint
 * Everything now uses:
 * /result/{jobId}?mode=...
 */
const ENDPOINT_MAP:
  Record<string, string> =
{
  verify:
    '/result',

  financial:
    '/result',

  cart:
    '/result',
};

type ResultData = {
  mode?: string;
  claim?: string;
  verdict?: Verdict;
  confidence?: Confidence;
  summary?: string;
  supports?: number;
  contradicts?: number;
  neutral?: number;
  sources?: Source[];
};

function downloadResult(
  data: ResultData
) {
  const blob =
    new Blob(
      [
        JSON.stringify(
          data,
          null,
          2
        ),
      ],
      {
        type:
          'application/json',
      }
    );

  const a =
    document.createElement(
      'a'
    );

  a.href =
    URL.createObjectURL(
      blob
    );

  a.download =
    'factguard-report.json';

  a.click();

  URL.revokeObjectURL(
    a.href
  );
}

export default function ResultPage({
  params,
}: {
  params: Promise<{
    jobId: string;
  }>;
}) {
  const {
    jobId,
  } = use(params);

  const searchParams =
    useSearchParams();

  const mode =
    searchParams.get(
      'mode'
    ) || 'verify';

  const endpoint =
    ENDPOINT_MAP[
      mode
    ] ??
    '/result';

  const [
    data,
    setData,
  ] = useState<any>(
    null
  );

  const [
    error,
    setError,
  ] = useState(false);

  useEffect(() => {
    let attempts =
      0;

    const MAX =
      40;

    const INTERVAL =
      1500;

    let timer:
      | ReturnType<
          typeof setTimeout
        >
      | undefined;

    async function poll() {
      attempts++;

      if (
        attempts >
        MAX
      ) {
        setError(
          true
        );

        return;
      }

      try {
        const res =
          await fetch(
            `${API_URL}${endpoint}/${jobId}?mode=${mode}`
          );

        if (
          !res.ok
        ) {
          throw new Error(
            String(
              res.status
            )
          );
        }

        const result =
          await res.json();

        if (
          result.status ===
          'processing'
        ) {
          timer =
            setTimeout(
              poll,
              INTERVAL
            );

          return;
        }

        setData(
          result
        );
      } catch (
        err
      ) {
        console.error(
          err
        );

        setError(
          true
        );
      }
    }

    poll();

    return () => {
      if (
        timer
      ) {
        clearTimeout(
          timer
        );
      }
    };
  }, [
    jobId,
    endpoint,
    mode,
  ]);

  if (error) {
    return (
      <main className='min-h-screen flex items-center justify-center'>
        Failed to load result
      </main>
    );
  }

  if (!data) {
    return (
      <ResultSkeleton />
    );
  }

  if (
    data.mode ===
    'financial'
  ) {
    return (
      <ResultErrorBoundary>
        <FinancialResultView
          data={data}
        />
      </ResultErrorBoundary>
    );
  }

  if (
    data.mode ===
    'cart'
  ) {
    return (
      <ResultErrorBoundary>
        <CartResultView
          data={data}
        />
      </ResultErrorBoundary>
    );
  }

  return (
    <main className='max-w-3xl mx-auto px-4 py-10 space-y-8'>
      <motion.div
        initial={{
          opacity: 0,
          y: -12,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        className='rounded-xl border border-[var(--card-border)] bg-[var(--card)] p-5 shadow-sm'
      >
        <p className='text-xs text-[var(--muted-foreground)] uppercase tracking-widest font-semibold mb-1'>
          Claim
        </p>

        <p className='text-lg font-medium'>
          "
          {
            data.claim
          }
          "
        </p>
      </motion.div>

      <div className='flex flex-wrap gap-3'>
        <VerdictBadge
          verdict={
            data.verdict ??
            'Unverified'
          }
        />

        <ConfidencePill
          confidence={
            data.confidence ??
            'Low'
          }
        />
      </div>

      <p>
        {
          data.summary
        }
      </p>

      <AgreementMeter
        supports={
          data.supports ??
          0
        }
        contradicts={
          data.contradicts ??
          0
        }
        neutral={
          data.neutral ??
          0
        }
      />

      <EvidenceTimeline
        sources={
          data.sources ??
          []
        }
      />

      <div className='flex gap-3'>
        <ShareCard
          jobId={
            jobId
          }
        />

        <button
          onClick={() =>
            downloadResult(
              data
            )
          }
        >
          <Download />
        </button>
      </div>
    </main>
  );
}