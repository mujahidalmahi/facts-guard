'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Shield, Clock, ArrowRight, AlertCircle } from 'lucide-react';
import { HistorySkeleton } from '@/components/Skeleton';

const MODE_BADGE: Record<string, { label: string; bg: string; text: string }> = {
  verify: { label: 'Verify', bg: '#e0f2fe', text: '#0369a1' },
  financial: { label: 'Financial', bg: '#f0fdf4', text: '#15803d' },
  cart: { label: 'Cart', bg: '#fef9c3', text: '#854d0e' },
  security: { label: 'Security', bg: '#fae8ff', text: '#86198f' },
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

interface HistoryItem {
  jobId: string;
  claim: string;
  status: string;
  createdAt: string;
  mode?: 'verify' | 'financial' | 'cart' | 'security';
  display_text?: string;
}

function formatDate(
  raw: string | undefined
): string {
  try {
    if (!raw) return '';
    const d = new Date(raw);
    if (isNaN(d.getTime()))
      return '';
    return d.toLocaleDateString(
      'en-US',
      {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }
    );
  } catch {
    return '';
  }
}

export default function HistoryPage() {
  const [claims, setClaims] =
    useState<HistoryItem[]>([]);
  const [loading, setLoading] =
    useState(true);
  const [error, setError] =
    useState(false);

  useEffect(() => {
    fetch(`${API_URL}/history`)
      .then((res) => {
        if (!res.ok)
          throw new Error();
        return res.json();
      })
      .then((data) => {
        setClaims(
          data.claims ?? []
        );
      })
      .catch(() => {
        setError(true);
      })
      .finally(() =>
        setLoading(false)
      );
  }, []);

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-[var(--foreground)] flex items-center gap-2">
        <Clock className="size-6 text-[var(--accent)]" />
        Verification History
      </h1>

      <p className="text-sm text-[var(--muted-foreground)] mt-1 mb-8">
        Previously analysed claims
      </p>

      {loading && <HistorySkeleton />}

      {error && (
        <div className="text-center py-20">
          <AlertCircle className="size-12 mx-auto text-red-500" />
          <p className="text-[var(--foreground)] mt-4 font-medium">
            Failed to load history
          </p>
          <button
            onClick={() =>
              window.location.reload()
            }
            className="mt-4 text-sm text-[var(--accent)] hover:underline"
          >
            Retry
          </button>
        </div>
      )}

      {!loading &&
        !error &&
        claims.length === 0 && (
          <div className="text-center py-20">
            <Shield className="size-12 mx-auto text-[var(--muted-foreground)] opacity-40" />
            <p className="text-[var(--muted-foreground)] mt-4">
              No claims verified yet
            </p>
            <Link
              href="/"
              className="inline-block mt-4 text-sm text-[var(--accent)] hover:underline"
            >
              Verify your first claim
            </Link>
          </div>
        )}

      {!loading &&
        !error &&
        claims.length > 0 && (
          <div className="divide-y divide-[var(--card-border)]">
            {claims.map((c) => (
              <Link
                key={c.jobId}
                href={
                  c.status ===
                  'done'
                    ? `/result/${c.jobId}`
                    : `/loading?job=${c.jobId}`
                }
                className="flex items-center gap-4 py-4 group transition-colors hover:bg-[var(--muted)] -mx-4 px-4 rounded-lg"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[var(--foreground)] truncate group-hover:text-[var(--accent)] transition-colors">
                    <span
                      style={{ background: (MODE_BADGE[c.mode ?? 'verify']).bg, color: (MODE_BADGE[c.mode ?? 'verify']).text }}
                      className="text-xs font-bold px-2 py-0.5 rounded-full mr-2"
                    >
                      {(MODE_BADGE[c.mode ?? 'verify']).label}
                    </span>
                    {c.display_text ?? c.claim}
                  </p>
                  <p className="text-xs text-[var(--muted-foreground)] mt-0.5">
                    {formatDate(
                      c.createdAt
                    )}
                    {c.status !==
                      'done' &&
                      ' · Processing'}
                  </p>
                </div>
                <ArrowRight className="size-4 text-[var(--muted-foreground)] group-hover:text-[var(--accent)] transition-colors shrink-0" />
              </Link>
            ))}
          </div>
        )}
    </main>
  );
}
