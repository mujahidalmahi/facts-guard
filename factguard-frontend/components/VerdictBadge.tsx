'use client';

import { motion } from 'framer-motion';
import { ShieldCheck, AlertOctagon, HelpCircle, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const VERDICT_STYLES: Record<string, {
  glow: string; bg: string; border: string; icon: LucideIcon; text: string; label: string; verdictClass: string;
}> = {
  'Verified': {
    glow: '#10B981', bg: 'from-emerald-900/40 to-emerald-800/20', border: 'border-emerald-500/40',
    icon: CheckCircle2, text: 'text-emerald-300', label: 'Verified', verdictClass: 'verdict-verified',
  },
  'Likely True': {
    glow: '#6366F1', bg: 'from-indigo-900/40 to-indigo-800/20', border: 'border-indigo-500/40',
    icon: ShieldCheck, text: 'text-indigo-300', label: 'Likely True', verdictClass: 'verdict-likely-true',
  },
  'Mixed Evidence': {
    glow: '#F59E0B', bg: 'from-amber-900/40 to-amber-800/20', border: 'border-amber-500/40',
    icon: HelpCircle, text: 'text-amber-300', label: 'Mixed Evidence', verdictClass: 'verdict-mixed',
  },
  'Likely Misleading': {
    glow: '#EF4444', bg: 'from-red-900/40 to-red-800/20', border: 'border-red-500/40',
    icon: AlertOctagon, text: 'text-red-300', label: 'Likely Misleading', verdictClass: 'verdict-misleading',
  },
  'Unverified': {
    glow: '#64748B', bg: 'from-slate-900/40 to-slate-800/20', border: 'border-slate-500/40',
    icon: HelpCircle, text: 'text-slate-300', label: 'Unverified', verdictClass: 'verdict-unverified',
  },
};

export function VerdictBadge({ verdict }: { verdict: string }) {
  const s = VERDICT_STYLES[verdict] ?? VERDICT_STYLES['Unverified'];
  const Icon = s.icon;

  return (
    <motion.div
      initial={{ scale: 0.85, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className={`rounded-2xl bg-gradient-to-br ${s.bg} border ${s.border} ${s.verdictClass} p-5 backdrop-blur-xl flex items-center gap-4`}
      style={{ boxShadow: `0 0 40px ${s.glow}22` }}
    >
      <div
        className="size-12 rounded-xl flex items-center justify-center"
        style={{ backgroundColor: `${s.glow}22` }}
      >
        <Icon className="size-6" style={{ color: s.glow }} />
      </div>
      <div>
        <p className="data-label mb-0.5">VERDICT</p>
        <p className="text-xl font-bold" style={{ color: s.glow }}>{s.label}</p>
      </div>
    </motion.div>
  );
}
