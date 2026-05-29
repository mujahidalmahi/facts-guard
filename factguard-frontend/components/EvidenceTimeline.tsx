'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import type { Source } from '@/types';

type SortKey = 'tier' | 'relevance' | 'date';
type SortDir = 'asc' | 'desc';

export function EvidenceTimeline({ sources }: { sources: Source[] }) {
  const [sortKey, setSortKey] = useState<SortKey>('tier');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir(key === 'relevance' ? 'desc' : 'asc');
    }
  };

  const sortedSources = [...sources].sort((a, b) => {
    const dir = sortDir === 'asc' ? 1 : -1;
    if (sortKey === 'tier') return (a.tier ?? 4) > (b.tier ?? 4) ? dir : -dir;
    if (sortKey === 'relevance') return (a.relevance ?? 0) > (b.relevance ?? 0) ? dir : -dir;
    if (sortKey === 'date') {
      const da = a.date ? new Date(a.date).getTime() : 0;
      const db = b.date ? new Date(b.date).getTime() : 0;
      return da > db ? dir : -dir;
    }
    return 0;
  });

  const toggleExpand = (idx: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  return (
    <div className="glass-card overflow-hidden">
      {/* Sort controls */}
      <div className="flex items-center gap-2 px-4 py-2 border-b" style={{ borderColor: 'var(--color-border-subtle)' }}>
        <span className="data-label mr-2">SORT BY</span>
        {(['tier', 'relevance', 'date'] as SortKey[]).map((key) => (
          <button
            key={key}
            onClick={() => toggleSort(key)}
            className="text-[10px] font-mono px-2 py-1 rounded transition-colors"
            style={{
              backgroundColor: sortKey === key ? 'var(--color-border-subtle)' : 'transparent',
              color: sortKey === key ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
            }}
          >
            {key.charAt(0).toUpperCase() + key.slice(1)}
            {sortKey === key && (sortDir === 'asc' ? ' ↑' : ' ↓')}
          </button>
        ))}
      </div>

      {/* Source list */}
      <div className="divide-y" style={{ borderColor: 'var(--color-border-subtle)' }}>
        {sortedSources.map((s, idx) => {
          const isExpanded = expanded.has(idx);
          const tier = s.tier ?? 4;
          return (
            <motion.div
              key={s.url}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: idx * 0.04 }}
            >
              <button
                onClick={() => toggleExpand(idx)}
                className="flex items-start gap-3 w-full text-left px-4 py-3 transition-colors hover:bg-[var(--color-border-subtle)]"
              >
                <div
                  className="w-0.5 shrink-0 self-stretch rounded-full mt-1"
                  style={{
                    backgroundColor: s.stance === 'supports' ? 'var(--color-accent-emerald)' :
                      s.stance === 'contradicts' ? 'var(--color-accent-red)' : 'var(--color-text-tertiary)',
                  }}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2 mb-0.5">
                    <span className="text-sm font-semibold truncate transition-colors group-hover:text-[var(--color-accent-primary)]"
                      style={{ color: 'var(--color-text-primary)' }}
                    >
                      {s.title}
                    </span>
                    <span className="text-xs font-mono shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
                      {s.relevance}/10
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                    <span
                      className="text-[10px] px-1.5 py-0.5 rounded font-mono border"
                      style={{
                        backgroundColor: tier <= 2 ? 'rgba(99,102,241,0.1)' : 'rgba(100,116,139,0.1)',
                        borderColor: tier <= 2 ? 'rgba(99,102,241,0.2)' : 'rgba(100,116,139,0.2)',
                        color: tier <= 2 ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)',
                      }}
                    >
                      T{tier}
                    </span>
                    {s.author && <span>{s.author}</span>}
                    {s.date && <span>{s.date}</span>}
                  </div>
                </div>
                {isExpanded ? <ChevronUp className="size-3.5 shrink-0" style={{ color: 'var(--color-text-tertiary)' }} /> :
                  <ChevronDown className="size-3.5 shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />}
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-3 pl-8 space-y-2">
                      <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                        {s.summary}
                      </p>
                      {s.quote && (
                        <p className="text-xs font-mono border-l-2 pl-2 italic"
                          style={{
                            color: 'var(--color-text-tertiary)',
                            borderColor: 'var(--color-border-default)',
                          }}
                        >
                          &ldquo;{s.quote}&rdquo;
                        </p>
                      )}
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs font-semibold transition-colors"
                        style={{ color: 'var(--color-accent-primary)' }}
                      >
                        <ExternalLink className="size-3" />
                        View source
                      </a>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
