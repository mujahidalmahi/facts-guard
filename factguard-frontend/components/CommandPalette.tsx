'use client';

import { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Command, Home, History, Shield, TrendingUp, ShoppingCart, AlertTriangle,
  Sun, Moon, Search, Trash2, Copy,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useTheme } from '@/components/ThemeProvider';
import type { AppMode } from '@/types';
import { MODE_META } from '@/types';
import { useToast } from '@/components/Toast';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CommandItem {
  id: string;
  label: string;
  icon: LucideIcon;
  hint?: string;
  action: () => void;
  keywords?: string[];
}

interface CommandGroup {
  label: string;
  items: CommandItem[];
}

interface HistoryEntry {
  jobId: string;
  display_text?: string;
  mode?: string;
  createdAt?: string;
}

function getModeIcon(mode: string): LucideIcon {
  switch (mode) {
    case 'verify': return Shield;
    case 'financial': return TrendingUp;
    case 'security': return AlertTriangle;
    case 'cart': return ShoppingCart;
    default: return Search;
  }
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const [recentHistory, setRecentHistory] = useState<HistoryEntry[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { theme, toggleTheme } = useTheme();
  const toast = useToast();
  const currentMode: AppMode = (searchParams.get('mode') as AppMode) || 'verify';

  const openPalette = useCallback(() => {
    setOpen(true);
    setQuery('');
    setActiveIndex(0);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
    setQuery('');
  }, []);

  // Global shortcut: Cmd/Ctrl+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (open) close();
        else openPalette();
      }
      if (e.key === 'Escape' && open) {
        e.preventDefault();
        close();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, openPalette, close]);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

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
    if (open) fetchHistory();
  }, [open]);

  const navigate = useCallback((path: string) => {
    router.push(path);
    close();
  }, [router, close]);

  const groups: CommandGroup[] = useMemo(() => {
    const navigateItems: CommandItem[] = [
      { id: 'home', label: 'Home', icon: Home, hint: '⌘H', action: () => { navigate('/'); }, keywords: ['home', 'start'] },
      { id: 'history', label: 'History', icon: History, hint: '⌘Y', action: () => { navigate('/history'); }, keywords: ['history', 'past'] },
      {
        id: 'mode-verify',
        label: 'Verify Track',
        icon: Shield,
        hint: '⌘1',
        action: () => { navigate('/?mode=verify'); },
        keywords: ['verify', 'fact'],
      },
      {
        id: 'mode-financial',
        label: 'Financial Track',
        icon: TrendingUp,
        hint: '⌘2',
        action: () => { navigate('/?mode=financial'); },
        keywords: ['financial', 'market'],
      },
      {
        id: 'mode-security',
        label: 'Security Track',
        icon: AlertTriangle,
        hint: '⌘3',
        action: () => { navigate('/?mode=security'); },
        keywords: ['security', 'threat'],
      },
      {
        id: 'mode-cart',
        label: 'Cart Track',
        icon: ShoppingCart,
        hint: '⌘4',
        action: () => { navigate('/?mode=cart'); },
        keywords: ['cart', 'price'],
      },
    ];

    const actionItems: CommandItem[] = [
      {
        id: 'theme',
        label: `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Theme`,
        icon: theme === 'dark' ? Sun : Moon,
        action: () => { toggleTheme(); close(); },
        keywords: ['theme', 'dark', 'light'],
      },
      {
        id: 'clear',
        label: 'Clear History',
        icon: Trash2,
        action: () => { close(); toast.info('History cleared'); },
        keywords: ['clear', 'history', 'delete'],
      },
      {
        id: 'copy',
        label: 'Copy Current Result',
        icon: Copy,
        action: () => { navigator.clipboard?.writeText('Result copied'); close(); toast.success('Copied to clipboard'); },
        keywords: ['copy', 'export'],
      },
    ];

    const recentItems: CommandItem[] = recentHistory.map((entry) => ({
      id: `hist-${entry.jobId}`,
      label: (entry.display_text || '').length > 50 ? (entry.display_text || '').slice(0, 50) + '...' : entry.display_text || 'Untitled',
      icon: getModeIcon(entry.mode || 'verify'),
      action: () => { navigate(`/result/${entry.jobId}?mode=${entry.mode || 'verify'}`); },
      keywords: [(entry.display_text || '').toLowerCase(), entry.mode || 'verify'],
    }));

    const filterGroup = (items: CommandItem[]): CommandItem[] =>
      items.filter(
        (item) =>
          !query ||
          item.label.toLowerCase().includes(query.toLowerCase()) ||
          item.keywords?.some((k) => k.toLowerCase().includes(query.toLowerCase()))
      );

    const groups: CommandGroup[] = [];

    const filteredNav = filterGroup(navigateItems);
    if (filteredNav.length > 0) groups.push({ label: 'Navigate', items: filteredNav });

    const filteredRecent = filterGroup(recentItems);
    if (filteredRecent.length > 0) groups.push({ label: 'Recent Queries', items: filteredRecent });

    const filteredActions = filterGroup(actionItems);
    if (filteredActions.length > 0) groups.push({ label: 'Actions', items: filteredActions });

    return groups;
  }, [query, recentHistory, theme, navigate, toggleTheme, close, toast]);

  const allItems = useMemo(() => groups.flatMap((g) => g.items), [groups]);

  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  // Scroll active item into view
  useEffect(() => {
    const active = listRef.current?.querySelector('[data-active="true"]');
    active?.scrollIntoView({ block: 'nearest' });
  }, [activeIndex]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => (i + 1) % Math.max(allItems.length, 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => (i - 1 + allItems.length) % Math.max(allItems.length, 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      allItems[activeIndex]?.action();
    }
  };

  const accentForMode = (id: string) => {
    if (id.includes('verify')) return MODE_META.verify.color;
    if (id.includes('financial')) return MODE_META.financial.color;
    if (id.includes('security')) return MODE_META.security.color;
    if (id.includes('cart')) return MODE_META.cart.color;
    return '#7E8FAD';
  };

  return (
    <>
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
              onClick={close}
            />
            <motion.div
              initial={{ opacity: 0, y: -20, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.96 }}
              transition={{ duration: 0.15, ease: 'easeOut' }}
              className="fixed left-1/2 top-[20%] z-50 -translate-x-1/2 w-[90vw] max-w-[600px]"
              role="dialog"
              aria-label="Command palette"
            >
              <div
                className="overflow-hidden rounded-2xl"
                style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)', boxShadow: '0 0 60px rgba(79, 70, 229, 0.2)' }}
              >
                {/* Search input */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--color-border-subtle)]">
                  <Search className="w-[18px] h-[18px] shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Search or type a command..."
                    className="flex-1 bg-transparent outline-none text-base"
                    style={{ color: 'var(--color-text-primary)' }}
                  />
                  <span className="data-label flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 rounded border" style={{ borderColor: 'var(--color-border-default)' }}>ESC</kbd>
                  </span>
                </div>

                {/* Results */}
                <div ref={listRef} className="max-h-[360px] overflow-y-auto py-2">
                  {groups.length === 0 ? (
                    <div className="px-4 py-8 text-center">
                      <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>No results found</div>
                      <div className="data-label mt-1">Try a different query</div>
                    </div>
                  ) : (
                    groups.map((group) => (
                      <div key={group.label}>
                        <div className="data-label px-4 py-2">{group.label}</div>
                        {group.items.map((item) => {
                          const idx = allItems.indexOf(item);
                          const isActive = idx === activeIndex;
                          const Icon = item.icon;
                          const accent = accentForMode(item.id);
                          return (
                            <button
                              key={item.id}
                              data-active={isActive}
                              onMouseEnter={() => setActiveIndex(idx)}
                              onClick={item.action}
                              className={`w-full flex items-center gap-3 px-4 h-10 text-left transition-colors ${
                                isActive
                                  ? 'border-l-2 border-[var(--color-accent-primary)]'
                                  : 'border-l-2 border-transparent hover:bg-white/5'
                              }`}
                              style={{
                                backgroundColor: isActive ? 'var(--color-accent-primary)/10' : 'transparent',
                              }}
                            >
                              <Icon className="w-4 h-4 shrink-0" style={{ color: item.id.startsWith('mode-') ? accent : '#7E8FAD' }} />
                              <span className="flex-1 text-sm truncate" style={{ color: 'var(--color-text-primary)' }}>{item.label}</span>
                              {item.hint && (
                                <span className="data-label flex items-center gap-1">
                                  {item.hint.split('').map((c, i) => (
                                    <kbd key={i} className="px-1 py-0.5 rounded border text-[9px]" style={{ borderColor: 'var(--color-border-default)' }}>
                                      {c}
                                    </kbd>
                                  ))}
                                </span>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    ))
                  )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-4 py-2 border-t border-[var(--color-border-subtle)]">
                  <div className="flex items-center gap-3 data-label">
                    <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded border" style={{ borderColor: 'var(--color-border-default)' }}>↑</kbd><kbd className="px-1 py-0.5 rounded border" style={{ borderColor: 'var(--color-border-default)' }}>↓</kbd> Navigate</span>
                    <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 rounded border" style={{ borderColor: 'var(--color-border-default)' }}>↵</kbd> Select</span>
                  </div>
                  <div className="flex items-center gap-1 data-label">
                    <span style={{ color: 'var(--color-accent-primary)' }}>FactGuard</span>
                    <span>v1.0</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Floating trigger hint */}
      {!open && currentMode && (
        <button
          onClick={openPalette}
          className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 px-3 py-2 flex items-center gap-2 text-xs transition-colors rounded-lg"
          style={{
            backgroundColor: 'var(--color-bg-surface)',
            border: '1px solid var(--color-border-default)',
            color: 'var(--color-text-secondary)',
          }}
          aria-label="Open command palette"
        >
          <Search className="w-3.5 h-3.5" />
          <span>Command palette</span>
          <kbd className="px-1.5 py-0.5 rounded border text-[9px] data-label" style={{ borderColor: 'var(--color-border-default)' }}>⌘K</kbd>
        </button>
      )}
    </>
  );
}
