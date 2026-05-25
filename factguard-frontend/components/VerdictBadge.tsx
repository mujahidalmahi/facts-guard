'use client';

import { motion } from 'framer-motion';

const VERDICT_STYLES: Record<string, { glow: string; bg: string; border: string; icon: string; text: string }> = {
  'Verified': { glow: '#10B981', bg: 'from-emerald-900/40 to-emerald-800/20', border: 'border-emerald-500/40', icon: '\u2713', text: 'text-emerald-300' },
  'Likely True': { glow: '#6366F1', bg: 'from-indigo-900/40 to-indigo-800/20', border: 'border-indigo-500/40', icon: '\u25C6', text: 'text-indigo-300' },
  'Mixed Evidence': { glow: '#F59E0B', bg: 'from-amber-900/40 to-amber-800/20', border: 'border-amber-500/40', icon: '\u25C6', text: 'text-amber-300' },
  'Likely Misleading': { glow: '#EF4444', bg: 'from-red-900/40 to-red-800/20', border: 'border-red-500/40', icon: '\u2717', text: 'text-red-300' },
  'Unverified': { glow: '#64748B', bg: 'from-slate-900/40 to-slate-800/20', border: 'border-slate-500/40', icon: '?', text: 'text-slate-300' },
};

export function VerdictBadge({ verdict }: { verdict: string }) {
  const s = VERDICT_STYLES[verdict] ?? VERDICT_STYLES['Unverified'];
  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300 }}
      className={`rounded-2xl bg-gradient-to-br ${s.bg} border ${s.border} p-6 backdrop-blur-xl flex items-center gap-4`}
      style={{ boxShadow: `0 0 40px ${s.glow}22` }}
    >
      <span className={`text-5xl font-black ${s.text}`}>{s.icon}</span>
      <div>
        <p className='text-xs text-slate-500 uppercase tracking-widest mb-1'>Verdict</p>
        <p className={`text-2xl font-bold ${s.text}`}>{verdict}</p>
      </div>
    </motion.div>
  );
}
