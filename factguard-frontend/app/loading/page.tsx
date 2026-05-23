'use client';

import {
  useEffect,
  useState,
} from 'react';
import {
  useRouter,
  useSearchParams,
} from 'next/navigation';
import {
  motion,
} from 'framer-motion';

const steps = [
  'Analyzing claim...',
  'Checking sources...',
  'Evaluating evidence...',
  'Generating trust score...',
];

export default function LoadingPage() {
  const router =
    useRouter();

  const searchParams =
    useSearchParams();

  const jobId =
    searchParams.get('job') ||
    'demo';

  const [step, setStep] =
    useState(0);

  useEffect(() => {
    const interval =
      setInterval(() => {
        setStep((prev) => {
          if (
            prev <
            steps.length - 1
          ) {
            return prev + 1;
          }

          clearInterval(
            interval
          );

          setTimeout(() => {
            router.push(
              `/result/${jobId}`
            );
          }, 700);

          return prev;
        });
      }, 1000);

    return () =>
      clearInterval(
        interval
      );
  }, [router, jobId]);

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-6">
      <div className="text-center max-w-md w-full">
        <motion.div
          animate={{
            rotate: 360,
          }}
          transition={{
            repeat:
              Infinity,
            duration: 1.4,
            ease:
              'linear',
          }}
          className="mx-auto h-16 w-16 rounded-full border-4 border-slate-300 border-t-indigo-500"
        />

        <motion.h1
          key={step}
          initial={{
            opacity: 0,
            y: 8,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          className="mt-8 text-2xl font-semibold text-slate-900"
        >
          {steps[step]}
        </motion.h1>

        <p className="mt-3 text-slate-500">
          FactGuard is
          verifying the
          claim using AI
          evidence analysis
        </p>

        <div className="mt-8 h-2 bg-slate-200 rounded-full overflow-hidden">
          <motion.div
            initial={{
              width: '0%',
            }}
            animate={{
              width: `${
                ((step +
                  1) /
                  steps.length) *
                100
              }%`,
            }}
            className="h-full bg-indigo-500"
          />
        </div>
      </div>
    </main>
  );
}