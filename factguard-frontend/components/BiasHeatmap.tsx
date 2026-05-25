'use client';

const BIAS_DESCRIPTIONS: Record<string, string> = {
  cherry_picking: 'Selectively displaying data points while excluding contradictory segments.',
  false_equivalence: 'Presenting two sides as equal when evidence overwhelmingly supports one.',
  appeal_to_authority: 'Relying heavily on perceived status rather than empirical context.',
  omission: 'Leaving out critical structural components necessary for absolute verification.',
  misleading_statistics: 'Presenting mathematical scaling factors out of native context.',
  emotional_language: 'Using charged or煽动性 wording to provoke an emotional response over rational analysis.',
  unverified_anecdote: 'Elevating a single personal story to the level of statistical evidence.',
};

export default function BiasHeatmap({ signals = [] }: { signals: string[] }) {
  if (signals.length === 0) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 text-center text-sm text-slate-500">
        No immediate logical manipulation signals detected in statement text.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-md">
      <h3 className="text-xs font-mono uppercase tracking-widest text-slate-400 mb-4">
        Cognitive Bias Fingerprint
      </h3>
      <div className="space-y-3">
        {signals.map(signal => (
          <div key={signal} className="border-b border-slate-800/60 pb-2.5 last:border-none last:pb-0">
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-semibold font-mono text-amber-400">
                {signal.replace(/_/g, ' ')}
              </span>
              <span className="text-[10px] bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded text-amber-300 font-mono">
                Signal Detected
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {BIAS_DESCRIPTIONS[signal] || 'Rhetorical framing strategy leveraged to tilt user response.'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
