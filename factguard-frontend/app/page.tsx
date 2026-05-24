'use client';

import {
  useState,
} from 'react';
import { useRouter } from 'next/navigation';
import SplashScreen from '@/components/SplashScreen';
import { PriceCheckSection } from '@/components/PriceCheckSection';

const API_URL =
  process.env
    .NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

export default function HomePage() {
  const [claim, setClaim] =
    useState('');

  const [loading, setLoading] =
    useState(false);
  const [showSplash, setShowSplash] =
    useState(() => {
      try {
        return !sessionStorage.getItem('splashShown');
      } catch {
        return false;
      }
    });

  const router =
    useRouter();

  async function handleAnalyse() {
    if (!claim.trim())
      return;
    if (claim.length > 2000) {
      alert('Claim is too long (max 2000 characters)');
      return;
    }

    try {
      setLoading(true);

      const res =
        await fetch(
          `${API_URL}/verify`,
          {
            method:
              'POST',
            headers: {
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify(
              {
                claim,
              }
            ),
          }
        );

      if (!res.ok) {
        throw new Error(
          'Failed request'
        );
      }

      const data =
        await res.json();

      const jobId =
        data.jobId ||
        'demo';

      router.push(
        `/loading?job=${jobId}`
      );
    } catch (error) {
      console.error(
        error
      );

      alert(
        'Failed to analyse claim'
      );
    } finally {
      setLoading(false);
    }
  }

  const examples = [
    'The Earth is flat',
    'WHO confirmed ivermectin cures COVID-19',
    'Apple is acquiring Netflix',
  ];

  if (showSplash) {
    return (
      <SplashScreen
        onDone={() => {
          sessionStorage.setItem(
            'splashShown',
            '1'
          );
          setShowSplash(false);
        }}
      />
    );
  }

  return (
    <main className="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center px-6 bg-[var(--background)]">
      <h1 className="text-6xl font-bold text-[var(--foreground)] mb-2">
        FactGuard
      </h1>

      <p className="text-[var(--muted-foreground)] mb-10 text-lg text-center">
        AI-powered trust verification &amp; price comparison
      </p>

      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-[var(--foreground)]">
            Analyse Claims
          </h2>

          <p className="text-[var(--muted-foreground)] mt-2 text-sm">
            Detect misinformation with AI evidence analysis
          </p>

          <textarea
            value={claim}
            onChange={(e) =>
              setClaim(
                e.target.value
              )
            }
            placeholder="Enter a claim to verify..."
            className="w-full mt-6 h-40 rounded-2xl border border-[var(--card-border)] p-4 text-base outline-none focus:ring-2 focus:ring-[var(--accent)] resize-none bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)]"
          />

          <button
            onClick={
              handleAnalyse
            }
            disabled={
              loading
            }
            className="w-full mt-4 bg-[var(--accent)] hover:bg-[var(--accent-hover)] transition-colors text-white py-4 rounded-2xl text-base font-semibold disabled:opacity-60"
          >
            {loading
              ? 'Analysing...'
              : 'Analyse'}
          </button>

          <div className="flex flex-wrap justify-center gap-2 mt-6">
            {examples.map(
              (
                example
              ) => (
                <button
                  key={
                    example
                  }
                  onClick={() =>
                    setClaim(
                      example
                    )
                  }
                  className="px-3 py-1.5 rounded-full border border-[var(--card-border)] text-xs text-[var(--muted-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                >
                  {example}
                </button>
              )
            )}
          </div>
        </div>

        <PriceCheckSection />
      </div>
    </main>
  );
}
