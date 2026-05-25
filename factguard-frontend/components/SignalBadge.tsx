'use client';

const CFG: Record<string, { bg: string; tx: string; bd: string; label: string }> = {
  Bullish: {
    bg: '#dcfce7',
    tx: '#15803d',
    bd: '#86efac',
    label: '\u2191 BULLISH',
  },

  Bearish: {
    bg: '#fee2e2',
    tx: '#b91c1c',
    bd: '#fca5a5',
    label: '\u2193 BEARISH',
  },

  Neutral: {
    bg: '#fef9c3',
    tx: '#854d0e',
    bd: '#fde047',
    label: '\u25C6 NEUTRAL',
  },
};

export function SignalBadge({
  signal,
}: {
  signal: string;
}) {
  const c =
    CFG[
      signal as keyof typeof CFG
    ] ?? CFG.Neutral;

  return (
    <span
      className='inline-flex items-center
      px-5 py-2 rounded-full
      text-lg font-black border'
      style={{
        backgroundColor: c.bg,
        color: c.tx,
        borderColor: c.bd,
      }}
    >
      {c.label}
    </span>
  );
}
