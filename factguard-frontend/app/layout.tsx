import './globals.css';
import { Geist, Geist_Mono } from 'next/font/google';
import { ThemeProvider } from '@/components/ThemeProvider';
import { ThemeScript } from '@/components/ThemeScript';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Nav } from '@/components/Nav';
import type { Metadata } from 'next';

const geistSans = Geist({ subsets: ['latin'], variable: '--font-geist-sans' });
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-geist-mono' });

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
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <body className="font-sans">
        <ThemeScript />
        <ThemeProvider>
          <Nav />
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
          <footer className='w-full text-center py-3 border-t border-[var(--card-border)] bg-[var(--glass)] backdrop-blur-md'>
            <p className='text-xs text-[var(--muted-foreground)]'>
              Powered by{' '}
              <span className='text-indigo-400 font-semibold'>
                BrightData
              </span>{' '}
              &middot; Real-time web intelligence
            </p>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
