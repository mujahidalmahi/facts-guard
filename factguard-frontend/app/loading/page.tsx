'use client';

import { Suspense, useEffect, useState, useRef, useMemo } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Hexagon, Activity } from 'lucide-react';
import { useJobPolling } from '@/lib/useJobPolling';

const MODE_LABELS: Record<string, string> = {
  verify: 'VERITAS ANALYSIS ENGINE',
  financial: 'MARKET SIGNAL ENGINE',
  security: 'THREATGUARD SCANNER',
  cart: 'CARTGUARD ENGINE',
};

const MODE_COLORS: Record<string, string> = {
  verify: '#4F46E5',
  financial: '#7C3AED',
  cart: '#06B6D4',
  security: '#F59E0B',
};

const FALLBACK_STEPS: Record<string, string[]> = {
  verify: [
    'Checking cache...',
    'Searching via Bright Data...',
    'Analysing with AI...',
    'Saving results...',
  ],
  financial: [
    'Searching Google, Bing & DuckDuckGo...',
    'Extracting articles via browser...',
    'Running AI analysis...',
  ],
  cart: [
    'Searching for prices...',
    'Analyzing product data...',
    'Saving results...',
  ],
  security: [
    'Scanning domains for threats...',
    'Generating compliance report...',
  ],
};

function LoadingContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const jobId = searchParams.get('job') || '';
  const mode = searchParams.get('mode') || 'verify';
  const accentColor = useMemo(() => MODE_COLORS[mode] ?? '#4F46E5', [mode]);
  const fallbackSteps = useMemo(() => FALLBACK_STEPS[mode] ?? FALLBACK_STEPS.verify, [mode]);

  const { progress, pct, status } = useJobPolling(jobId, 'result', fallbackSteps, mode);
  const done = status === 'done';
  const isError = status === 'error';
  const isTimeout = status === 'timeout';
  const isFinished = done || isError || isTimeout;

  const [logEntries, setLogEntries] = useState<string[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const terminalRef = useRef<HTMLDivElement>(null);
  const prevProgressRef = useRef<string>('');

  const hasLogs = logEntries.length > 0;
  const waiting = !hasLogs && !isFinished;

  useEffect(() => {
    if (!progress || progress === prevProgressRef.current) return;
    const prev = prevProgressRef.current;
    prevProgressRef.current = progress;

    if (prev === '') {
      if (progress === 'Processing...') return;
    }

    setLogEntries((prev) => [...prev, progress]);
  }, [progress]);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logEntries]);

  useEffect(() => {
    const start = Date.now();
    const ticker = setInterval(() => {
      setElapsed((Date.now() - start) / 1000);
    }, 100);
    return () => clearInterval(ticker);
  }, []);

  useEffect(() => {
    if (done) {
      const timer = setTimeout(() => {
        router.push(`/result/${jobId}?mode=${mode}`);
      }, 1200);
      return () => clearTimeout(timer);
    }
  }, [done, jobId, mode, router]);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <div className="relative flex-1 flex items-center justify-center p-6 overflow-hidden">
      <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full blur-[120px] opacity-20"
          style={{ backgroundColor: accentColor }}
        />
        <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full blur-[120px] opacity-15"
          style={{ backgroundColor: '#06B6D4' }}
        />
        <div className="absolute inset-0 animated-grid opacity-30" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="relative z-10 w-full max-w-[600px]"
      >
        <div className="dark relative overflow-hidden rounded-2xl scan-line"
          style={{
            backgroundColor: 'rgba(5,10,26,0.85)',
            border: '1px solid var(--color-border-default)',
            backdropFilter: 'blur(16px)',
          }}
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border-subtle)]"
            style={{ backgroundColor: 'rgba(5,10,26,0.6)' }}
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" style={{ color: accentColor }}
                xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              >
                <polyline points="4 17 10 11 4 5" /><line x1="12" y1="19" x2="20" y2="19" />
              </svg>
              <span className="data-label">{MODE_LABELS[mode]}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full"
                style={{
                  backgroundColor: done ? 'rgba(16,185,129,0.1)' : isTimeout ? 'rgba(245,158,11,0.1)' : isError ? 'rgba(239,68,68,0.1)' : `${accentColor}1A`,
                  border: `1px solid ${done ? 'rgba(16,185,129,0.3)' : isTimeout ? 'rgba(245,158,11,0.3)' : isError ? 'rgba(239,68,68,0.3)' : `${accentColor}4D`}`,
                }}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${!isFinished ? 'pulse-live' : ''}`}
                  style={{ backgroundColor: done ? '#10B981' : isTimeout ? '#F59E0B' : isError ? '#EF4444' : accentColor }}
                />
                <span className="data-label" style={{ color: done ? '#10B981' : isTimeout ? '#F59E0B' : isError ? '#EF4444' : accentColor }}>
                  {done ? 'COMPLETE' : isTimeout ? 'TIMEOUT' : isError ? 'ERROR' : 'PROCESSING'}
                </span>
              </div>
              {!isFinished && (
                <span className="w-1.5 h-3.5"
                  style={{ backgroundColor: 'var(--color-accent-emerald)', animation: 'blink 1s step-end infinite' }}
                />
              )}
            </div>
          </div>

          <div ref={terminalRef}
            className="p-4 font-mono text-xs min-h-[300px] max-h-[400px] overflow-y-auto"
            style={{ backgroundColor: 'rgba(5,10,26,0.8)' }}
          >
            {waiting && (
              <div className="flex items-start gap-3 mb-2">
                <span className="flex-shrink-0 text-[var(--color-accent-cyan)]">[ .. ]</span>
                <span className="text-[var(--color-text-primary)]">Waiting for backend...</span>
                <span className="inline-block w-1 h-3 ml-0.5"
                  style={{ backgroundColor: accentColor, animation: 'blink 0.8s step-end infinite' }}
                />
              </div>
            )}

            {logEntries.map((entry, i) => {
              const isError = entry.toLowerCase().includes('fail') || entry.toLowerCase().includes('error');
              const isWarning = entry.toLowerCase().includes('fallback');
              const isDone = entry.toLowerCase().includes('done') || entry.toLowerCase().includes('complete');
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-start gap-3 mb-2"
                >
                  <span className={`flex-shrink-0 ${
                    isError ? 'text-[var(--color-accent-red)]' :
                    isWarning ? 'text-[var(--color-accent-amber)]' :
                    isDone ? 'text-[var(--color-accent-emerald)]' :
                    'text-[var(--color-accent-cyan)]'
                  }`}>
                    {isError ? '[FAIL]' : isDone ? '[ OK ]' : '[ .. ]'}
                  </span>
                  <span className={`${
                    isError ? 'text-[var(--color-accent-red)]' :
                    isWarning ? 'text-[var(--color-accent-amber)]' :
                    isDone ? 'text-[var(--color-accent-emerald)]' :
                    'text-[var(--color-text-primary)]'
                  }`}>
                    {entry}
                  </span>
                </motion.div>
              );
            })}

            {hasLogs && !isFinished && (
              <motion.span
                animate={{ opacity: [0, 1, 0] }}
                transition={{ repeat: Infinity, duration: 1 }}
                className="inline-block"
                style={{ color: accentColor }}
              >
                _
              </motion.span>
            )}

            {done && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-start gap-3 mt-4"
              >
                <span className="flex-shrink-0 text-[var(--color-accent-emerald)]">[ ✓ ]</span>
                <span className="text-[var(--color-accent-emerald)] font-semibold">
                  Analysis complete. Rendering results...
                </span>
              </motion.div>
            )}

            {isTimeout && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-start gap-3 mt-4"
              >
                <span className="flex-shrink-0 text-[var(--color-accent-amber)]">[ !! ]</span>
                <div className="flex-1">
                  <span className="text-[var(--color-accent-amber)] font-semibold">
                    Analysis timed out.
                  </span>
                  <div className="data-label mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                    The backend took too long to respond. This may be due to high load or a network issue.
                  </div>
                  <button
                    onClick={() => router.push('/')}
                    className="mt-3 px-4 py-1.5 rounded-lg text-xs font-semibold text-white transition-colors"
                    style={{ backgroundColor: accentColor }}
                  >
                    Try Again
                  </button>
                </div>
              </motion.div>
            )}

            {isError && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-start gap-3 mt-4"
              >
                <span className="flex-shrink-0 text-[var(--color-accent-red)]">[FAIL]</span>
                <div className="flex-1">
                  <span className="text-[var(--color-accent-red)] font-semibold">
                    Analysis failed.
                  </span>
                  <div className="data-label mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                    The backend encountered an error processing this request.
                  </div>
                  <button
                    onClick={() => router.push('/')}
                    className="mt-3 px-4 py-1.5 rounded-lg text-xs font-semibold text-white transition-colors"
                    style={{ backgroundColor: accentColor }}
                  >
                    Try Again
                  </button>
                </div>
              </motion.div>
            )}
          </div>

          <div className="relative h-[3px] overflow-hidden" style={{ backgroundColor: 'var(--color-bg-elevated)' }}>
            <motion.div
              className={`h-full ${!isFinished || done ? 'progress-gradient' : ''}`}
              animate={{ width: `${isFinished ? (done ? 100 : pct) : Math.max(5, pct)}%` }}
              transition={{ ease: 'easeOut', duration: 0.3 }}
              style={isTimeout ? { backgroundColor: '#F59E0B' } : isError ? { backgroundColor: '#EF4444' } : undefined}
            />
          </div>

          <div className="flex items-center justify-between px-4 py-3 border-t border-[var(--color-border-subtle)]"
            style={{ backgroundColor: 'rgba(5,10,26,0.6)' }}
          >
            <div className="data-label flex items-center gap-1" style={{ color: 'var(--color-accent-amber)' }}>
              <Activity className="w-3 h-3" />
              Elapsed: {formatTime(elapsed)}
            </div>
            <div className="data-label" style={{ color: 'var(--color-text-tertiary)' }}>
              Logs streamed live from backend
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[var(--color-border-subtle)]">
            <Hexagon className="w-3 h-3" style={{ color: 'var(--color-text-tertiary)' }} />
            <span className="data-label" style={{ color: 'var(--color-text-tertiary)' }}>Powered by BrightData MCP</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function LoadingPage() {
  return (
    <Suspense fallback={null}>
      <LoadingContent />
    </Suspense>
  );
}
