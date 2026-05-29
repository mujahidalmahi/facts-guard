'use client';

import { motion } from 'framer-motion';

const BIAS_DESCRIPTIONS: Record<string, string> = {
  cherry_picking: 'Selectively displaying data points while excluding contradictory segments.',
  false_equivalence: 'Presenting two sides as equal when evidence overwhelmingly supports one.',
  appeal_to_authority: 'Relying heavily on perceived status rather than empirical context.',
  omission: 'Leaving out critical structural components necessary for absolute verification.',
  misleading_statistics: 'Presenting mathematical scaling factors out of native context.',
  emotional_language: 'Using charged wording to provoke an emotional response over rational analysis.',
  unverified_anecdote: 'Elevating a single personal story to the level of statistical evidence.',
};

export default function BiasHeatmap({ signals = [] }: { signals: string[] }) {
  if (signals.length === 0) {
    return (
      <div className="glass-card p-5 text-center text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
        No cognitive bias signals detected in the claim framing.
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <h3 className="data-label mb-4">Cognitive Bias Fingerprint</h3>
      <div className="space-y-3">
        {signals.map((signal, i) => (
          <motion.div
            key={signal}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className="flex items-start gap-3 pb-3 border-b last:border-none last:pb-0"
            style={{ borderColor: 'var(--color-border-subtle)' }}
          >
            <div
              className="mt-0.5 size-2 rounded-full shrink-0"
              style={{ backgroundColor: 'var(--color-accent-amber)' }}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-sm font-semibold font-mono" style={{ color: 'var(--color-accent-amber)' }}>
                  {signal.replace(/_/g, ' ')}
                </span>
                <span
                  className="text-[10px] px-1.5 py-0.5 rounded font-mono border"
                  style={{
                    backgroundColor: 'rgba(245,158,11,0.1)',
                    borderColor: 'rgba(245,158,11,0.2)',
                    color: 'var(--color-accent-amber)',
                  }}
                >
                  Signal Detected
                </span>
              </div>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                {BIAS_DESCRIPTIONS[signal] || 'Rhetorical framing strategy leveraged to influence response.'}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
