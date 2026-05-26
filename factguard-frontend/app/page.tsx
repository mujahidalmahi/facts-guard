'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
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

  security: {
    headline: 'ThreatGuard',
    sub: 'Real-time brand, regulatory & vendor threat monitoring',
    placeholder:
      'Data breach | compliance update | disinformation campaign...',
    cta: 'Scan Threats',
    endpoint: '/threats/scan',
    field: 'query',
    examples: [
      'Data breach at key vendor',
      'New GDPR compliance requirement',
      'Disinformation campaign targeting financial sector',
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
        <div className='relative text-center space-y-4'>
          <motion.div
            key={mode}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className='inline-flex items-center gap-2 px-4 py-1.5 rounded-full
              border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs
              font-semibold tracking-widest uppercase'
          >
            <span className='w-1.5 h-1.5 rounded-full bg-indigo-400 pulse-ring' />
            {mode === 'verify'
              ? 'AI Fact Intelligence'
              : mode === 'financial'
              ? 'Live Market Oracle'
              : mode === 'security'
              ? 'Real-Time Threat Monitor'
              : 'Price Trust Engine'}
          </motion.div>

          <motion.h1
            key={`title-${mode}`}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className='text-5xl sm:text-7xl font-black tracking-tight'
          >
            <span className='gradient-text'>
              {cfg.headline}
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className='text-slate-400 text-base sm:text-lg max-w-xl mx-auto'
          >
            {cfg.sub}
          </motion.p>
        </div>

        <div className='flex justify-center'>
          <ModeSwitcher
            current={mode}
            onChange={(m) => {
              setMode(m);
              setInput('');
            }}
          />
        </div>

        <div className='glass-card p-2 mt-2'>
          <textarea
            value={input}
            onChange={(e) =>
              setInput(e.target.value)
            }
            placeholder={cfg.placeholder}
            className='w-full h-36 bg-transparent p-4 text-base
              text-slate-100 placeholder-slate-500
              outline-none resize-none'
          />
          <div className='flex items-center justify-between px-3 pb-2'>
            <span className='text-xs text-slate-600'>
              {input.length} chars
            </span>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className='btn-glow px-6 py-2.5 rounded-xl
                text-white font-semibold text-sm
                disabled:opacity-60'
            >
              {loading
                ? '■ Analysing...'
                : cfg.cta}
            </button>
          </div>
        </div>

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
