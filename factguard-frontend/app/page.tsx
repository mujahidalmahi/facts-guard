'use client';

import { useRef, useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Shield, TrendingUp, AlertTriangle, ShoppingCart, Send, AlertCircle, X, Sparkles } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import SplashScreen from '@/components/SplashScreen';
import type { AppMode } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const MODE_CONFIG: Record<
  AppMode,
  {
    heading: string;
    subtitle: string;
    icon: LucideIcon;
    placeholder: string;
    buttonLabel: string;
    buttonColor: string;
    endpoint: string;
    field: string;
    maxLength: number;
    examples: string[];
  }
> = {
  verify: {
    heading: 'Intelligence Verification',
    subtitle: 'VERITAS reasoning engine · v5.1',
    icon: Shield,
    placeholder: 'Enter a claim, statement, or news headline to verify...',
    buttonLabel: 'Analyse Claim',
    buttonColor: '#4F46E5',
    endpoint: '/verify',
    field: 'claim',
    maxLength: 2000,
    examples: [
      'WHO confirmed ivermectin cures COVID-19',
      'Apple is acquiring Netflix at $95B',
      'mRNA vaccines alter human DNA permanently',
    ],
  },
  financial: {
    heading: 'Market Signal Analysis',
    subtitle: 'Real-time market telemetry · yFinance + BrightData',
    icon: TrendingUp,
    placeholder: 'Enter an asset, ticker, or market question...',
    buttonLabel: 'Analyse Market',
    buttonColor: '#7C3AED',
    endpoint: '/financial',
    field: 'query',
    maxLength: 500,
    examples: [
      'Bitcoin 30-day trend and outlook',
      'Crude oil price vs USD correlation',
      'TSLA Q4 earnings impact forecast',
    ],
  },
  security: {
    heading: 'Threat Surface Scan',
    subtitle: 'ThreatGuard engine · 10+ news domains monitored',
    icon: AlertTriangle,
    placeholder: 'Enter a company, brand, or sector to scan for threats...',
    buttonLabel: 'Scan Threats',
    buttonColor: '#F59E0B',
    endpoint: '/threats/scan',
    field: 'query',
    maxLength: 500,
    examples: [
      'Data breach at cloud storage vendor',
      'New SEC cybersecurity disclosure rule',
      'Disinformation targeting fintech sector',
    ],
  },
  cart: {
    heading: 'Price Trust Analysis',
    subtitle: 'CartGuard engine · counterfeit risk detection',
    icon: ShoppingCart,
    placeholder: 'Enter a product name or model number...',
    buttonLabel: 'Compare Prices',
    buttonColor: '#06B6D4',
    endpoint: '/cart',
    field: 'product',
    maxLength: 500,
    examples: [
      'iPhone 16 Pro 256GB',
      'Sony WH-1000XM5 headphones',
      'RTX 5090 GPU best price',
    ],
  },
};

export default function HomePage() {
  const searchParams = useSearchParams();
  const modeParam = searchParams.get('mode') as AppMode | null;
  const mode: AppMode = modeParam || 'verify';

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSplash, setShowSplash] = useState<boolean | null>(null);
  const [query, setQuery] = useState('');

  useEffect(() => {
    setShowSplash(!sessionStorage.getItem('splashShown'));
  }, []);

  const inputRef = useRef<HTMLTextAreaElement>(null);
  const router = useRouter();

  const config = MODE_CONFIG[mode];
  const Icon = config.icon;

  async function handleSubmit() {
    const value = query.trim();
    if (!value) {
      setError('Please enter a query to analyse.');
      return;
    }
    if (value.length > config.maxLength) {
      setError(`Query exceeds ${config.maxLength} character limit.`);
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const res = await fetch(
        `${API_URL}${config.endpoint}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            [config.field]: value,
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
      setError('Analysis failed — is the backend running?');
    } finally {
      setLoading(false);
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example);
    if (inputRef.current) {
      inputRef.current.value = example;
    }
    setError(null);
  };

  // Cmd+Enter to submit
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  if (showSplash === null) return null;

  if (showSplash)
    return (
      <SplashScreen
        onDone={() => {
          sessionStorage.setItem('splashShown', '1');
          setShowSplash(false);
        }}
      />
    );

  return (
    <div className="relative min-h-screen flex items-center justify-center p-6 overflow-hidden"
      style={{ backgroundColor: 'var(--color-bg-base)' }}
    >
      {/* Background orbs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
        <div
          className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full blur-[120px] opacity-30"
          style={{ backgroundColor: config.buttonColor }}
        />
        <div
          className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full blur-[120px] opacity-20"
          style={{ backgroundColor: '#06B6D4' }}
        />
        <div className="absolute inset-0 animated-grid opacity-40" />
      </div>

      <motion.div
        key={mode}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
        className="relative z-10 w-full max-w-[760px]"
      >
        {/* Mode Header */}
        <motion.div layoutId="mode-title" className="mb-10 text-center">
          <div className="inline-flex items-center gap-2 mb-4 px-3 py-1 rounded-full"
            style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
          >
            <Sparkles className="w-3.5 h-3.5" style={{ color: config.buttonColor }} />
            <span className="data-label" style={{ color: config.buttonColor }}>
              {mode.toUpperCase()} · MODE ACTIVE
            </span>
          </div>
          <h1
            className="text-4xl sm:text-5xl font-extrabold mb-3"
            style={{
              color: 'var(--color-text-primary)',
              fontFamily: 'var(--font-sora)',
              textShadow: `0 0 40px ${config.buttonColor}40`,
            }}
          >
            {config.heading}
          </h1>
          <p className="font-mono text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            {config.subtitle}
          </p>
        </motion.div>

        {/* Input Panel */}
        <div className="rounded-2xl overflow-hidden"
          style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
        >
          <div className="p-6" style={{ backgroundColor: 'rgba(15, 30, 53, 0.6)' }}>
            {/* Top bar */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${config.buttonColor}20`, color: config.buttonColor }}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>{config.heading}</div>
                  <div className="data-label flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-live" />
                    Engine Ready
                  </div>
                </div>
              </div>
            </div>

            {/* Textarea */}
            <textarea
              ref={inputRef}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setError(null);
              }}
              onKeyDown={handleKeyDown}
              placeholder={config.placeholder}
              className="w-full min-h-[160px] bg-transparent outline-none resize-none font-mono text-base leading-relaxed"
              style={{ color: 'var(--color-text-primary)', caretColor: config.buttonColor }}
              aria-label="Analysis query"
            />

            {/* Character counter + keyboard hint */}
            <div className="flex items-center justify-between mb-4">
              <div className="data-label">
                {query.length} / {config.maxLength}
              </div>
              <div className="data-label flex items-center gap-1">
                <kbd className="px-1 py-0.5 rounded border" style={{ borderColor: 'var(--color-border-default)' }}>⌘</kbd>
                <span>+</span>
                <kbd className="px-1 py-0.5 rounded border" style={{ borderColor: 'var(--color-border-default)' }}>↵</kbd>
                <span className="ml-1">to submit</span>
              </div>
            </div>

            {/* Bottom toolbar */}
            <div className="flex items-center justify-between gap-3 flex-wrap pt-4 border-t border-[var(--color-border-subtle)]">
              <div className="flex flex-wrap gap-2">
                {config.examples.map((ex) => (
                  <button
                    key={ex}
                    onClick={() => handleExampleClick(ex)}
                    className="px-3 py-1.5 rounded-full text-xs border transition-colors"
                    style={{
                      color: 'var(--color-text-secondary)',
                      borderColor: 'var(--color-border-subtle)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--color-border-default)';
                      e.currentTarget.style.color = 'var(--color-text-primary)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--color-border-subtle)';
                      e.currentTarget.style.color = 'var(--color-text-secondary)';
                    }}
                  >
                    {ex}
                  </button>
                ))}
              </div>

              <motion.button
                onClick={handleSubmit}
                disabled={loading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold text-sm text-white transition-all disabled:opacity-50"
                style={{
                  backgroundColor: config.buttonColor,
                  boxShadow: `0 0 20px ${config.buttonColor}40`,
                }}
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    {config.buttonLabel}
                  </>
                )}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Error state */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 flex items-start gap-3 p-4 rounded-lg"
            style={{ backgroundColor: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)' }}
            role="alert"
          >
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" style={{ color: 'var(--color-accent-red)' }} />
            <div className="flex-1 text-sm" style={{ color: 'var(--color-accent-red)' }}>{error}</div>
            <button
              onClick={() => setError(null)}
              style={{ color: 'var(--color-accent-red)' }}
              className="hover:opacity-70"
              aria-label="Dismiss error"
            >
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[var(--color-border-subtle)]">
            <div className="w-3 h-3 rounded-sm flex items-center justify-center" style={{ backgroundColor: '#4F46E520' }}>
              <div className="w-1.5 h-1.5 rounded-sm" style={{ backgroundColor: '#4F46E5' }} />
            </div>
            <span className="data-label" style={{ color: 'var(--color-text-tertiary)' }}>Powered by BrightData MCP · Multi-agent reasoning</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
