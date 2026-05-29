import './globals.css';
import { Suspense } from 'react';
import { Sora, DM_Sans, DM_Mono } from 'next/font/google';
import { ThemeProvider } from '@/components/ThemeProvider';
import { ThemeScript } from '@/components/ThemeScript';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { ToastProvider } from '@/components/Toast';
import { CommandPalette } from '@/components/CommandPalette';
import type { Metadata } from 'next';

const sora = Sora({ subsets: ['latin'], variable: '--font-sora', display: 'swap' });
const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-dm-sans', display: 'swap' });
const dmMono = DM_Mono({ subsets: ['latin'], variable: '--font-dm-mono', display: 'swap', weight: ['400', '500'] });

export const metadata: Metadata = {
  title: 'FactGuard',
  description: 'AI-powered trust verification',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${sora.variable} ${dmSans.variable} ${dmMono.variable}`} suppressHydrationWarning>
      <body className="font-body">
        <ThemeScript />
        <ThemeProvider>
          <ToastProvider>
            <Suspense fallback={null}>
              <div className="flex min-h-screen" style={{ backgroundColor: 'var(--color-bg-base)' }}>
                <Suspense fallback={null}>
                  <div className="hidden lg:block shrink-0">
                    <Sidebar />
                  </div>
                </Suspense>
                <div className="flex flex-col flex-1 min-w-0">
                  <Suspense fallback={null}>
                    <TopBar />
                  </Suspense>
                  <main id="main-content" className="flex-1">
                    <ErrorBoundary>
                      {children}
                    </ErrorBoundary>
                  </main>
                  <footer className="w-full text-center py-3 border-t border-[var(--card-border)] bg-[var(--glass)] backdrop-blur-md">
                    <p className="text-xs text-[var(--muted-foreground)]">
                      Powered by{' '}
                      <span className="text-indigo-400 font-semibold">BrightData</span>
                      &middot; Real-time web intelligence
                    </p>
                  </footer>
                </div>
              </div>
              <Suspense fallback={null}>
                <CommandPalette />
              </Suspense>
            </Suspense>
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
