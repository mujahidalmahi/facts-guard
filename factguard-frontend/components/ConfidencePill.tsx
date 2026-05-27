'use client';

import { motion } from 'framer-motion';

const CFG = {
  High: { bg: 'rgba(16,185,129,0.1)', text: 'var(--color-accent-emerald)', border: 'rgba(16,185,129,0.25)', dot: '#10B981' },
  Medium: { bg: 'rgba(245,158,11,0.1)', text: 'var(--color-accent-amber)', border: 'rgba(245,158,11,0.25)', dot: '#F59E0B' },
  Low: { bg: 'rgba(239,68,68,0.1)', text: 'var(--color-accent-red)', border: 'rgba(239,68,68,0.25)', dot: '#EF4444' },
};

export type Confidence = 'High' | 'Medium' | 'Low';

export function ConfidencePill({ confidence }: { confidence: Confidence }) {
  const c = CFG[confidence] ?? CFG.Medium;

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border"
      style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
    >
      <motion.span
        animate={{ scale: [1, 1.4, 1] }}
        transition={{ repeat: Infinity, duration: 2 }}
        className="size-1.5 rounded-full"
        style={{ backgroundColor: c.dot }}
      />
      {confidence} Confidence
    </motion.span>
  );
}
