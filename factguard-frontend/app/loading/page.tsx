'use client';

import {
  Suspense,
  useEffect,
  useRef,
  useState,
} from 'react';
import {
  useRouter,
  useSearchParams,
} from 'next/navigation';
import {
  motion,
} from 'framer-motion';

const API_URL =
  process.env
    .NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

const POLL_INTERVAL = 1500;
const POLL_LIMIT = 30;

const PROGRESS_ICONS: Record<
  string,
  string
> = {
  'Checking cache...': '🔍',
  'Searching DuckDuckGo...':
    '🌐',
  'Analyzing with AI...': '🤖',
  'Saving results...': '💾',
  Failed: '❌',
};

function LoadingContent() {
  const router = useRouter();

  const searchParams =
    useSearchParams();

  const jobId =
    searchParams.get('job') ||
    'demo';

  const intervalRef =
    useRef<ReturnType<
      typeof setInterval
    > | null>(null);

  const attemptRef =
    useRef(0);

  const [progress, setProgress] =
    useState('Processing...');

  useEffect(() => {
    async function poll() {
      attemptRef.current++;
      if (
        attemptRef.current >
        POLL_LIMIT
      ) {
        clearInterval(
          intervalRef.current!
        );
        router.push(
          `/result/${jobId}`
        );
        return;
      }

      try {
        const res = await fetch(
          `${API_URL}/result/${jobId}`
        );
        if (!res.ok) return;

        const data =
          await res.json();

        if (
          data.progress
        ) {
          setProgress(
            data.progress
          );
        }

        if (
          data.status &&
          data.status !==
            'processing'
        ) {
          router.push(
            `/result/${jobId}`
          );
        }
      } catch {
        // retry on next interval
      }
    }

    intervalRef.current =
      setInterval(
        poll,
        POLL_INTERVAL
      );

    poll();

    return () => {
      if (
        intervalRef.current
      ) {
        clearInterval(
          intervalRef.current
        );
      }
    };
  }, [router, jobId]);

  const icon =
    PROGRESS_ICONS[
      progress
    ] || '⏳';

  const stepIndex = [
    'Checking cache...',
    'Searching DuckDuckGo...',
    'Analyzing with AI...',
    'Saving results...',
  ].indexOf(progress);

  const pct =
    stepIndex >= 0
      ? ((stepIndex + 1) /
          4) *
        100
      : 50;

  return (
    <main className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center bg-[var(--background)] px-6">
      <div className="text-center max-w-md w-full">
        <motion.div
          animate={{
            rotate: 360,
          }}
          transition={{
            repeat: Infinity,
            duration: 1.4,
            ease: 'linear',
          }}
          className="mx-auto h-16 w-16 rounded-full border-4 border-[var(--card-border)] border-t-[var(--accent)]"
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
          className="mt-8 text-2xl font-semibold text-[var(--foreground)]"
        >
          {icon} {progress}
        </motion.h1>

        <p className="mt-3 text-[var(--muted-foreground)]">
          FactGuard is
          verifying the claim
          using AI evidence
          analysis
        </p>

        <div className="mt-8 h-2 bg-[var(--muted)] rounded-full overflow-hidden">
          <motion.div
            initial={{
              width: '0%',
            }}
            animate={{
              width: `${pct}%`,
            }}
            className="h-full bg-[var(--accent)]"
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
