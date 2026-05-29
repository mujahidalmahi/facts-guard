'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, TrendingUp, ShoppingCart, AlertTriangle,
  Sun, Moon, Menu, X, Command,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useTheme } from '@/components/ThemeProvider';
import type { AppMode } from '@/types';
import { MODE_META } from '@/types';

const MODE_ICONS: Record<AppMode, LucideIcon> = {
  verify: Shield,
  financial: TrendingUp,
  security: AlertTriangle,
  cart: ShoppingCart,
};

export function TopBar() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { theme, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);

  const currentMode: AppMode = (searchParams.get('mode') as AppMode) || 'verify';

  const navigateToMode = (mode: AppMode) => {
    setMenuOpen(false);
    router.push(`/?mode=${mode}`);
  };

  const triggerCommandPalette = () => {
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
  };

  return (
    <>
      <div className="lg:hidden fixed top-0 left-0 right-0 z-40 h-14 flex items-center justify-between px-4 border-b border-[var(--color-border-subtle)] backdrop-blur-xl"
        style={{ backgroundColor: 'rgba(10, 22, 40, 0.95)' }}
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}
          >
            <Shield className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="font-bold text-sm" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>FactGuard</div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={triggerCommandPalette}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
            aria-label="Open command palette"
          >
            <Command className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          </button>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} /> : <Moon className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />}
          </button>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
            aria-label="Toggle menu"
          >
            {menuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="lg:hidden fixed top-14 left-0 right-0 z-30 border-b border-[var(--color-border-subtle)] backdrop-blur-xl"
            style={{ backgroundColor: 'rgba(10, 22, 40, 0.98)' }}
          >
            <div className="p-4 space-y-2">
              <div className="data-label mb-2">MODE NAVIGATOR</div>
              {(Object.keys(MODE_META) as AppMode[]).map((mode) => {
                const Icon = MODE_ICONS[mode];
                const meta = MODE_META[mode];
                const isActive = currentMode === mode;
                return (
                  <button
                    key={mode}
                    onClick={() => navigateToMode(mode)}
                    className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-colors ${
                      isActive ? 'bg-[var(--color-accent-primary)]/10' : 'hover:bg-[var(--color-bg-elevated)]'
                    }`}
                  >
                    <Icon className="w-4 h-4" style={{ color: meta.color }} />
                    <div className="flex-1 text-left">
                      <div className="text-sm font-semibold" style={{ color: isActive ? meta.color : 'var(--color-text-primary)' }}>
                        {meta.label}
                      </div>
                      <div className="data-label">{meta.sublabel}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="lg:hidden h-14" />
    </>
  );
}
