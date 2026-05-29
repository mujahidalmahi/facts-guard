'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, TrendingUp, ShoppingCart, AlertTriangle,
  Sun, Moon, ChevronLeft, ChevronRight, Command, History, Clock, User,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useTheme } from '@/components/ThemeProvider';
import type { AppMode } from '@/types';
import { MODE_META } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const MODE_ICONS: Record<AppMode, LucideIcon> = {
  verify: Shield,
  financial: TrendingUp,
  security: AlertTriangle,
  cart: ShoppingCart,
};

interface HistoryEntry {
  jobId: string;
  claim?: string;
  display_text?: string;
  mode?: string;
  verdict?: string;
  signal?: string;
  createdAt?: string;
}

function relativeTime(iso: string): string {
  const ts = new Date(iso).getTime();
  if (isNaN(ts)) return '';
  const diff = (Date.now() - ts) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function verdictDotColor(verdict?: string, signal?: string): string {
  if (!verdict && !signal) return '#7E8FAD';
  if (verdict === 'Verified') return '#10B981';
  if (verdict === 'Likely True') return '#4F46E5';
  if (verdict === 'Mixed Evidence') return '#F59E0B';
  if (verdict === 'Likely Misleading') return '#EF4444';
  if (signal === 'Bullish') return '#10B981';
  if (signal === 'Bearish') return '#EF4444';
  return '#7E8FAD';
}

export function Sidebar() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { theme, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const [recentHistory, setRecentHistory] = useState<HistoryEntry[]>([]);

  const currentMode: AppMode = (searchParams.get('mode') as AppMode) || 'verify';

  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await fetch(`${API_URL}/history`);
        if (res.ok) {
          const data = await res.json();
          setRecentHistory((data.claims ?? []).slice(0, 5));
        }
      } catch { /* ignore */ }
    }
    fetchHistory();
  }, []);

  const navigateToMode = useCallback((mode: AppMode) => {
    router.push(`/?mode=${mode}`);
  }, [router]);

  const navigateToHistory = useCallback(() => {
    router.push('/history');
  }, [router]);

  const navigateToResult = useCallback((item: HistoryEntry) => {
    router.push(`/result/${item.jobId}?mode=${item.mode || 'verify'}`);
  }, [router]);

  const handleCollapse = useCallback(() => {
    setCollapsed((c) => !c);
  }, []);

  const triggerCommandPalette = useCallback(() => {
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
  }, []);

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 64 : 240 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      className="sticky top-0 h-screen z-30 flex flex-col border-r border-[var(--color-border-subtle)] backdrop-blur-xl relative"
      style={{ backgroundColor: 'rgba(10, 22, 40, 0.9)' }}
    >
      {/* Wordmark */}
      <div className="p-4 flex items-center gap-2 border-b border-[var(--color-border-subtle)] h-16">
        <div className="relative flex-shrink-0">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}>
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div
            className="absolute inset-0 rounded-lg"
            style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)', filter: 'blur(8px)', opacity: 0.5 }}
          />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="overflow-hidden">
              <div className="font-bold text-sm" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>FactGuard</div>
              <div className="data-label">v1.0 · Enterprise</div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Mode Navigator */}
      <div className="p-3">
        {!collapsed && <div className="data-label px-2 mb-2">Mode Navigator</div>}
        <nav className="space-y-1">
          {(Object.keys(MODE_META) as AppMode[]).map((mode) => {
            const Icon = MODE_ICONS[mode];
            const meta = MODE_META[mode];
            const isActive = currentMode === mode;
            return (
              <button
                key={mode}
                onClick={() => navigateToMode(mode)}
                aria-label={`Switch to ${meta.label} mode`}
                className={`w-full flex items-center ${collapsed ? 'justify-center' : ''} gap-3 px-2 py-2.5 rounded-lg transition-all group relative ${
                  isActive ? 'bg-[var(--color-accent-primary)]/5' : 'hover:bg-[var(--color-bg-elevated)]'
                }`}
                title={collapsed ? meta.label : undefined}
              >
                {isActive && (
                  <motion.div
                    layoutId="mode-indicator"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 rounded-r-full"
                    style={{ backgroundColor: meta.color, boxShadow: `0 0 8px ${meta.color}` }}
                  />
                )}
                <div className="relative flex-shrink-0">
                  <Icon
                    className="w-4 h-4 transition-colors"
                    style={{ color: isActive ? meta.color : '#7E8FAD' }}
                  />
                  {isActive && (
                    <div
                      className="absolute inset-0 w-4 h-4 rounded-full blur-md opacity-50"
                      style={{ backgroundColor: meta.color }}
                    />
                  )}
                </div>
                <AnimatePresence>
                  {!collapsed && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex-1 text-left overflow-hidden"
                    >
                      <div
                        className="text-sm font-medium truncate"
                        style={{ color: isActive ? meta.color : 'var(--color-text-primary)' }}
                      >
                        {meta.label}
                      </div>
                      <div className="data-label" style={{ fontSize: '9px' }}>
                        {meta.sublabel}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
                <AnimatePresence>
                  {!collapsed && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0 }}
                      className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: meta.color, boxShadow: `0 0 4px ${meta.color}` }}
                    />
                  )}
                </AnimatePresence>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Recent History */}
      <div className="px-3 mt-2 flex-1 overflow-hidden flex flex-col min-h-0">
        {!collapsed && (
          <div className="flex items-center justify-between px-2 mb-2">
            <div className="data-label">Recent History</div>
            <button
              onClick={navigateToHistory}
              className="data-label text-[var(--color-accent-primary)] hover:text-[var(--color-accent-secondary)] transition-colors flex items-center gap-1"
              aria-label="View all history"
            >
              <History className="w-3 h-3" />
            </button>
          </div>
        )}
        {!collapsed && (
          <div className="space-y-1 overflow-y-auto flex-1 min-h-0">
            {recentHistory.length === 0 ? (
              <div className="px-2 py-4 text-center">
                <Clock className="w-5 h-5 text-[var(--color-text-tertiary)] mx-auto mb-2" />
                <div className="text-xs text-[var(--color-text-tertiary)]">No queries yet</div>
              </div>
            ) : (
              recentHistory.map((item) => (
                <button
                  key={item.jobId}
                  onClick={() => navigateToResult(item)}
                  className="w-full text-left px-2 py-1.5 rounded hover:bg-[var(--color-bg-elevated)] transition-colors group"
                  aria-label={`Load query: ${item.display_text || item.claim}`}
                >
                  <div className="flex items-start gap-2">
                    <div
                      className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
                      style={{ backgroundColor: verdictDotColor(item.verdict, item.signal) }}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs text-[var(--color-text-primary)] truncate group-hover:text-[var(--color-accent-primary)]">
                        {(item.display_text || item.claim || '').length > 28
                          ? (item.display_text || item.claim || '').slice(0, 28) + '...'
                          : item.display_text || item.claim || 'Untitled'}
                      </div>
                      <div className="data-label mt-0.5">{item.createdAt ? relativeTime(item.createdAt) : ''}</div>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        )}
      </div>

      {/* Bottom controls */}
      <div className={`border-t border-[var(--color-border-subtle)] flex items-center ${collapsed ? 'p-1.5 justify-center gap-0.5' : 'p-3 gap-1'}`}>
        <button
          onClick={triggerCommandPalette}
          className={`flex items-center justify-center rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors ${
            collapsed ? 'p-1.5' : 'flex-1 px-2 py-2 gap-2'
          }`}
          aria-label="Open command palette"
          title={collapsed ? 'Command palette' : undefined}
        >
          <Command className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          {!collapsed && <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>⌘K</span>}
        </button>
        <button
          onClick={toggleTheme}
          className={`flex items-center justify-center rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors ${
            collapsed ? 'p-1.5' : 'flex-1 px-2 py-2 gap-2'
          }`}
          aria-label="Toggle theme"
          title={collapsed ? 'Toggle theme' : undefined}
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          ) : (
            <Moon className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          )}
        </button>
        {!collapsed && (
          <div className="flex-1 flex items-center justify-center px-2 py-2 rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors cursor-pointer">
            <User className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          </div>
        )}
      </div>

      {/* Collapse toggle */}
      <button
        onClick={handleCollapse}
        className="absolute -right-3 top-20 w-6 h-6 rounded-full flex items-center justify-center transition-all hover:scale-110"
        style={{
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border-default)',
          color: 'var(--color-text-secondary)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
        }}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
      </button>
    </motion.aside>
  );
}
