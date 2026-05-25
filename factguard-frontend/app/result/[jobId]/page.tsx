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

import BiasHeatmap from '@/components/BiasHeatmap';
import SourceGraph from '@/components/SourceGraph';

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
  narrative_frame?: string;
  supports?: number;
  contradicts?: number;
  neutral?: number;
  bias_signals?: string[];
  source_diversity?: string;
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

  const [
    showGraph,
    setShowGraph,
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

      <div className='flex flex-wrap items-center gap-3'>
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

        {data.source_diversity && (
          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold font-mono tracking-wide
            ${data.source_diversity === 'High' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
              data.source_diversity === 'Medium' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
              'bg-red-500/10 text-red-400 border border-red-500/20'}`}
          >
            {data.source_diversity} Diversity
          </span>
        )}
      </div>

      {data.narrative_frame && (
        <p className="text-sm italic text-slate-400 border-l-2 border-indigo-500/40 pl-4 py-2 bg-indigo-500/5 rounded-r-lg">
          Framing: &ldquo;{data.narrative_frame}&rdquo;
        </p>
      )}

      <p className="text-[var(--foreground)] leading-relaxed">
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

      {data.bias_signals && data.bias_signals.length > 0 && (
        <BiasHeatmap signals={data.bias_signals} />
      )}

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-[var(--muted-foreground)] uppercase tracking-wide">
            Sources
          </h3>
          <button
            onClick={() => setShowGraph(v => !v)}
            className="text-xs text-[var(--accent)] hover:text-[var(--accent-hover)] font-mono transition-colors"
          >
            {showGraph ? 'List View' : 'Graph View'}
          </button>
        </div>
        {showGraph ? (
          <SourceGraph sources={data.sources ?? []} />
        ) : (
          <EvidenceTimeline
            sources={data.sources ?? []}
          />
        )}
      </div>

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