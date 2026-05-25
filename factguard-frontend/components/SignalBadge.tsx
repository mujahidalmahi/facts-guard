'use client';

// Trading signal badge — BUY / SELL / HOLD / WATCH

const CFG = {
  BUY: {
    bg: '#dcfce7',
    tx: '#15803d',
    bd: '#86efac',
    label: '↑ BUY',
  },

  SELL: {
    bg: '#fee2e2',
    tx: '#b91c1c',
    bd: '#fca5a5',
    label: '↓ SELL',
  },

  HOLD: {
    bg: '#fef9c3',
    tx: '#854d0e',
    bd: '#fde047',
    label: '◆ HOLD',
  },

  WATCH: {
    bg: '#e0f2fe',
    tx: '#0369a1',
    bd: '#7dd3fc',
    label: '■ WATCH',
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
    ] ?? CFG.WATCH;

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