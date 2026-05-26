'use client';

import { motion } from 'framer-motion';
import { Shield, TrendingUp, ShoppingCart, AlertTriangle } from 'lucide-react';
import type { AppMode } from '@/types';

const MODES = [
  {
    id: 'verify' as AppMode,
    label: 'Verify',
    Icon: Shield,
    desc: 'Fact-check claims',
  },
  {
    id: 'financial' as AppMode,
    label: 'Financial',
    Icon: TrendingUp,
    desc: 'Market analysis',
  },
  {
    id: 'security' as AppMode,
    label: 'Security',
    Icon: AlertTriangle,
    desc: 'Threat monitoring',
  },
  {
    id: 'cart' as AppMode,
    label: 'Cart',
    Icon: ShoppingCart,
    desc: 'Price comparison',
  },
] as const;

export function ModeSwitcher({
  current,
  onChange,
}: {
  current: AppMode;
  onChange: (m: AppMode) => void;
}) {
  return (
    <div
      className='flex items-center gap-1 p-1 rounded-2xl
      bg-[var(--card)] border border-[var(--card-border)]
      w-full sm:w-auto'
    >
      {MODES.map(({ id, label, Icon, desc }) => (
        <button
          key={id}
          onClick={() => onChange(id)}
          title={desc}
          className='relative flex-1 sm:flex-none flex items-center
          justify-center gap-2 px-4 sm:px-5 py-3 sm:py-2.5
          rounded-xl text-sm font-medium transition-colors
          min-h-[48px]'
        >
          {current === id && (
            <motion.div
              layoutId='mode-pill'
              className='absolute inset-0 rounded-xl bg-[var(--accent)]'
              transition={{
                type: 'spring',
                stiffness: 400,
                damping: 30,
              }}
            />
          )}

          <span
            className='relative flex items-center gap-2 z-10'
            style={{
              color:
                current === id
                  ? 'white'
                  : 'var(--muted-foreground)',
            }}
          >
            <Icon className='size-4' />
            <span className='hidden sm:inline'>{label}</span>
          </span>
        </button>
      ))}
    </div>
  );
}
