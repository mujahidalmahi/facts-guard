'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface Props {
  supports: number;
  contradicts: number;
  neutral: number;
}

function AnimatedStat({ value, label, color }: { value: number; label: string; color: string }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (value === 0) return;
    const duration = 600;
    const steps = 20;
    const increment = value / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplay(value);
        clearInterval(timer);
      } else {
        setDisplay(Math.round(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [value]);

  return (
    <div className="text-center">
      <p className="text-2xl font-black font-mono" style={{ color }}>{display}</p>
      <p className="text-xs uppercase tracking-wider mt-0.5" style={{ color: 'var(--color-text-tertiary)' }}>{label}</p>
    </div>
  );
}

export function AgreementMeter({ supports, contradicts, neutral }: Props) {
  const totalSources = supports + contradicts + neutral;

  if (totalSources === 0) {
    return (
      <div className="glass-card p-5">
        <h3 className="data-label mb-3">Source Breakdown</h3>
        <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>No trusted sources found for this claim.</p>
      </div>
    );
  }

  const total = totalSources;
  const suppPct = (supports / total) * 100;
  const contPct = (contradicts / total) * 100;
  const neutPct = (neutral / total) * 100;

  return (
    <div className="glass-card p-5">
      <h3 className="data-label mb-4">Source Breakdown</h3>

      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        className="flex h-3 w-full rounded-full overflow-hidden origin-left"
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${suppPct}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="h-full"
          style={{ backgroundColor: 'var(--color-accent-emerald)' }}
        />
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${neutPct}%` }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
          className="h-full"
          style={{ backgroundColor: 'var(--color-text-tertiary)' }}
        />
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${contPct}%` }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 0.2 }}
          className="h-full"
          style={{ backgroundColor: 'var(--color-accent-red)' }}
        />
      </motion.div>

      <div className="grid grid-cols-3 mt-4 divide-x" style={{ borderColor: 'var(--color-border-subtle)' }}>
        <div className="pr-4"><AnimatedStat value={supports} label="Support" color="var(--color-accent-emerald)" /></div>
        <div className="px-4"><AnimatedStat value={neutral} label="Neutral" color="var(--color-text-tertiary)" /></div>
        <div className="pl-4"><AnimatedStat value={contradicts} label="Contradict" color="var(--color-accent-red)" /></div>
      </div>

      <p className="text-xs mt-4" style={{ color: 'var(--color-text-tertiary)' }}>
        Based on {totalSources} trusted source{totalSources !== 1 ? 's' : ''} analysed
      </p>
    </div>
  );
}
