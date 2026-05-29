'use client';

import {
  useState,
} from 'react';

import {
  useSearchParams,
} from 'next/navigation';

interface ShareCardProps {
  jobId: string;
}

export function ShareCard({
  jobId,
}: ShareCardProps) {
  const [
    copied,
    setCopied,
  ] = useState(false);

  const searchParams =
    useSearchParams();

  const mode =
    searchParams.get(
      'mode'
    ) || 'verify';

  const url = `${window.location.origin}/result/${jobId}?mode=${mode}`;

  async function copy() {
    try {
      await navigator.clipboard.writeText(
        url
      );

      setCopied(
        true
      );

      setTimeout(
        () =>
          setCopied(
            false
          ),
        2000
      );
    } catch {
      const el =
        document.getElementById(
          'share-url-text'
        );

      if (el) {
        const range =
          document.createRange();

        range.selectNodeContents(
          el
        );

        window
          .getSelection()
          ?.removeAllRanges();

        window
          .getSelection()
          ?.addRange(
            range
          );

        document.execCommand(
          'copy'
        );

        setCopied(
          true
        );

        setTimeout(
          () =>
            setCopied(
              false
            ),
          2000
        );
      }
    }
  }

  return (
    <div className='flex-1 flex items-center gap-3 py-4 border-t border-[var(--card-border)]'>
      <div className='flex-1 min-w-0'>
        <p
          className='text-xs text-[var(--muted-foreground)] font-mono truncate'
          id='share-url-text'
        >
          {url || '—'}
        </p>
      </div>

      <button
        onClick={
          copy
        }
        disabled={
          !url
        }
        className='shrink-0 text-xs font-semibold text-[var(--accent)] hover:text-[var(--accent-hover)] disabled:opacity-40 transition-colors underline-offset-2 hover:underline'
      >
        {copied
          ? 'Copied ✓'
          : 'Copy link'}
      </button>
    </div>
  );
}