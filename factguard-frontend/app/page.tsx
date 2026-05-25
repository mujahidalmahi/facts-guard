'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ModeSwitcher } from '@/components/ModeSwitcher';
import SplashScreen from '@/components/SplashScreen';
import type { AppMode } from '@/types';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

const MODE_CFG = {
  verify: {
    headline: 'FactGuard',
    sub: 'AI-powered trust verification in under 60 seconds',
    placeholder:
      'Enter a claim, headline, or statement to verify...',
    cta: 'Analyse Claim',
    endpoint: '/verify',
    field: 'claim',
    examples: [
      'The Earth is flat',
      'WHO confirmed ivermectin cures COVID-19',
      'Apple is acquiring Netflix',
    ],
  },

  financial: {
    headline: 'Market Intel',
    sub: 'Real-time price analysis, signals & market prediction',
    placeholder:
      'Dollar rate today | Oil price trend | TSLA stock outlook...',
    cta: 'Analyse Market',
    endpoint: '/financial',
    field: 'query',
    examples: [
      'Dollar to BDT rate',
      'Crude oil price trend',
      'Bitcoin 30-day',
    ],
  },

  cart: {
    headline: 'CartGuard',
    sub: 'Compare prices · Green = trusted · Red = risky',
    placeholder:
      'iPhone 16 Pro 256GB | Sony WH-1000XM5 | RTX 5090...',
    cta: 'Compare Prices',
    endpoint: '/cart',
    field: 'product',
    examples: [
      'iPhone 16 Pro',
      'Sony WH-1000XM5',
      'RTX 5090 GPU',
    ],
  },
} satisfies Record<AppMode, object>;

export default function HomePage() {
  const [mode, setMode] =
    useState<AppMode>('verify');

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSplash, setShowSplash] =
    useState(false);

  const router = useRouter();

  const cfg =
    MODE_CFG[mode] as typeof MODE_CFG['verify'];

  useEffect(() => {
    if (!sessionStorage.getItem('splashShown')) {
      setShowSplash(true);
    }
  }, []);

  async function handleSubmit() {
    if (!input.trim()) return;

    setLoading(true);

    try {
      const res = await fetch(
        `${API_URL}${cfg.endpoint}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            [cfg.field]: input,
          }),
        }
      );

      if (!res.ok)
        throw new Error('Request failed');

      const data = await res.json();

      router.push(
        `/loading?job=${data.jobId}&mode=${mode}`
      );
    } catch {
      alert('Failed — is the backend running?');
    } finally {
      setLoading(false);
    }
  }

  if (showSplash)
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

  return (
    <main
      className='min-h-[calc(100vh-3.5rem)]
      flex flex-col items-center justify-center
      px-6 bg-[var(--background)]'
    >
      <div className='max-w-3xl w-full text-center space-y-6'>
        <h1 className='text-6xl font-bold text-[var(--foreground)]'>
          {cfg.headline}
        </h1>

        <p className='text-[var(--muted-foreground)] text-lg'>
          {cfg.sub}
        </p>

        <div className='flex justify-center'>
          <ModeSwitcher
            current={mode}
            onChange={(m) => {
              setMode(m);
              setInput('');
            }}
          />
        </div>

        <textarea
          value={input}
          onChange={(e) =>
            setInput(e.target.value)
          }
          placeholder={cfg.placeholder}
          className='w-full mt-4 h-40 rounded-2xl
          border border-[var(--card-border)]
          p-5 text-lg outline-none
          focus:ring-2 focus:ring-[var(--accent)]
          resize-none bg-[var(--card)]
          text-[var(--foreground)]
          placeholder-[var(--muted-foreground)]'
        />

        <button
          onClick={handleSubmit}
          disabled={loading}
          className='w-full bg-[var(--accent)]
          hover:bg-[var(--accent-hover)]
          transition-colors text-white py-4
          rounded-2xl text-lg font-semibold
          disabled:opacity-60'
        >
          {loading
            ? 'Processing...'
            : cfg.cta}
        </button>

        <div className='flex flex-wrap justify-center gap-3'>
          {cfg.examples.map((ex) => (
            <button
              key={ex}
              onClick={() => setInput(ex)}
              className='px-4 py-2 rounded-full
              border border-[var(--card-border)]
              text-sm text-[var(--muted-foreground)]
              hover:bg-[var(--muted)]
              hover:text-[var(--foreground)]
              transition-colors'
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}