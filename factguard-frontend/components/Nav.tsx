'use client';

import Link from 'next/link';
import { useTheme } from '@/components/ThemeProvider';
import { Shield, Sun, Moon } from 'lucide-react';

export function Nav() {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="sticky top-0 z-50 border-b border-[var(--card-border)] bg-[var(--card)]/80 backdrop-blur-md">
      <div className="max-w-5xl mx-auto flex items-center justify-between h-14 px-4">
        <Link
          href="/"
          className="flex items-center gap-2 font-bold text-lg text-[var(--foreground)] hover:text-[var(--accent)] transition-colors"
        >
          <Shield className="size-5 text-[var(--accent)]" />
          FactGuard
        </Link>

        <div className="flex items-center gap-4">
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
