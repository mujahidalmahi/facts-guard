'use client';

import { use, useEffect, useState } from 'react';
import { motion } from 'framer-motion';

import { VerdictBadge } from '@/components/VerdictBadge';
import { ConfidencePill } from '@/components/ConfidencePill';
import { AgreementMeter } from '@/components/AgreementMeter';
import { EvidenceTimeline } from '@/components/EvidenceTimeline';
import { ShareCard } from '@/components/ShareCard';
import {
  Verdict,
  Confidence,
} from '@/types';

type ResultData = {
  verdict?: Verdict;
  confidence?: Confidence;
  summary?: string;
  supports?: number;
  contradicts?: number;
  neutral?: number;
  sources?: any[];
};

export default function ResultPage({
  params,
}: {
  params: Promise<{
    jobId: string;
  }>;
}) {
  const { jobId } = use(params);

  const [data, setData] =
    useState<ResultData | null>(
      null
    );

  useEffect(() => {
    const API_URL =
      process.env
        .NEXT_PUBLIC_API_URL ||
      'http://localhost:8000';

    fetch(
      `${API_URL}/result/${jobId}`
    )
      .then((res) => {
        if (!res.ok)
          throw Error();
        return res.json();
      })
      .then((result) => {
        setData({
          verdict:
            result.verdict ??
            'Unverified',
          confidence:
            result.confidence ??
            'Low',
          summary:
            result.summary,
          supports:
            result.supports,
          contradicts:
            result.contradicts,
          neutral:
            result.neutral,
          sources:
            result.sources ??
            [],
        });
      })
      .catch(() => {
        setData({
          verdict:
            'Unverified',
          confidence: 'Low',
          summary:
            'No result found.',
          supports: 0,
          contradicts: 0,
          neutral: 0,
          sources: [],
        });
      });
  }, [jobId]);

  if (!data) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-slate-500">
          Loading result...
        </p>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      {/* Verdict + Confidence */}
      <div className="flex flex-wrap items-center gap-3">
        <motion.div
          initial={{
            opacity: 0,
            scale: 0.8,
          }}
          animate={{
            opacity: 1,
            scale: 1,
          }}
          transition={{
            type: 'spring',
            stiffness: 260,
            damping: 20,
          }}
        >
          <VerdictBadge
            verdict={
              data.verdict ??
              'Unverified'
            }
          />
        </motion.div>

        <ConfidencePill
          confidence={
            data.confidence ??
            'Low'
          }
        />
      </div>

      {/* Summary */}
      <p className="text-slate-700 leading-relaxed text-base">
        {data.summary ||
          'No summary available.'}
      </p>

      {/* Agreement Meter */}
      <AgreementMeter
        supports={
          data.supports ?? 0
        }
        contradicts={
          data.contradicts ??
          0
        }
        neutral={
          data.neutral ?? 0
        }
      />

      {/* Evidence Timeline */}
      <section>
        <h2 className="text-lg font-semibold mb-3">
          Evidence Sources
        </h2>

        <EvidenceTimeline
          sources={
            data.sources ??
            []
          }
        />
      </section>

      {/* Share Card */}
      <ShareCard
        jobId={jobId}
      />
    </main>
  );
}