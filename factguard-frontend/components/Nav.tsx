'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useTheme } from '@/components/ThemeProvider';
import { Shield, Sun, Moon } from 'lucide-react';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

const BD_LABELS: Record<string, string> = {
  mcp_discover: 'MCP',
  serp_api: 'SERP',
  crawl_api: 'Crawl',
  unlocker: 'Unlock',
  browser: 'Browser',
};

export function Nav() {
  const { theme, toggleTheme } = useTheme();
  const [cbHealth, setCbHealth] = useState<Record<string, { is_open: boolean }> | null>(null);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const res = await fetch(`${API_URL}/routing/health`);
        if (res.ok) {
          setCbHealth(await res.json());
        }
      } catch {
        // ignore
      }
    }

    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="sticky top-0 z-50 border-b border-[var(--glass-border)] bg-[var(--glass)] backdrop-blur-2xl saturate-[160%]">
      <div className="max-w-5xl mx-auto flex items-center justify-between h-14 px-4">
        <Link
          href="/"
          className="flex items-center gap-2 font-bold text-lg text-[var(--foreground)] hover:text-[var(--accent)] transition-colors"
        >
          <Shield className="size-5 text-[var(--accent)] drop-shadow-[0_0_6px_var(--accent-glow)]" />
          FactGuard
        </Link>

        <div className="flex items-center gap-4">
          {cbHealth && (
            <div className="flex items-center gap-1.5 mr-2" title="Circuit breaker status">
              {Object.entries(BD_LABELS).map(([key, label]) => {
                const state = cbHealth[key];
                const healthy = !state?.is_open;
                return (
                  <span
                    key={key}
                    className={`inline-block w-2 h-2 rounded-full ${
                      healthy ? 'bg-emerald-400' : 'bg-red-400'
                    }`}
                    title={`${label}: ${healthy ? 'healthy' : 'open'}`}
                  />
                );
              })}
            </div>
          )}

          <Link
            href="/"
            className="text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
          >
            Home
          </Link>
          <Link
            href="/history"
            className="text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
          >
            History
          </Link>

          <button
            onClick={toggleTheme}
            className="ml-2 p-2 rounded-lg text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)] transition-colors"
            aria-label="Toggle dark mode"
          >
            {theme === 'dark' ? (
              <Sun className="size-4" />
            ) : (
              <Moon className="size-4" />
            )}
          </button>
        </div>
      </div>
    </nav>
  );
}
