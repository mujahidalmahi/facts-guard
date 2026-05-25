import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export const contentType = 'image/png';

export const size = { width: 1200, height: 630 };

const VERDICT_COLOR: Record<string, string> = {
  Verified: '#16a34a',
  'Likely True': '#65a30d',
  'Mixed Evidence': '#d97706',
  'Likely Misleading': '#dc2626',
  Unverified: '#64748b',
  BUY: '#16a34a',
  SELL: '#dc2626',
  HOLD: '#d97706',
  WATCH: '#0369a1',
  'Buy Now': '#16a34a',
  'Great Deal': '#16a34a',
};

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  let verdict = 'FactGuard';
  let summary = 'AI-powered fact verification';
  let mode = 'verify';

  try {
    const modeParam = req.nextUrl.searchParams.get('mode') || 'verify';
    const res = await fetch(`${apiUrl}/result/${jobId}?mode=${modeParam}`);
    const data = await res.json();
    verdict = data.verdict ?? data.signal ?? verdict;
    summary = (data.summary ?? data.query ?? summary).slice(0, 120);
    mode = data.mode ?? modeParam;
  } catch {}

  const color = VERDICT_COLOR[verdict] ?? '#6366f1';
  const modeLabel: Record<string, string> = {
    verify: 'Fact Check',
    financial: 'Market Intel',
    cart: 'Cart Guard',
  };

  return new ImageResponse(
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        height: '100%',
        background: '#0f172a',
        padding: '60px',
        fontFamily: 'sans-serif',
        justifyContent: 'space-between',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div
          style={{
            background: '#6366f1',
            borderRadius: '8px',
            padding: '8px 16px',
            color: 'white',
            fontSize: '14px',
            fontWeight: 700,
          }}
        >
          FACTGUARD
        </div>
        <div style={{ color: '#64748b', fontSize: '14px' }}>
          {modeLabel[mode] ?? 'Analysis'}
        </div>
      </div>
      <div>
        <div style={{ color, fontSize: '52px', fontWeight: 900, marginBottom: '16px' }}>
          {verdict}
        </div>
        <div style={{ color: '#94a3b8', fontSize: '22px', lineHeight: 1.4 }}>
          {summary}
        </div>
      </div>
      <div style={{ color: '#475569', fontSize: '14px' }}>
        factguard.vercel.app
      </div>
    </div>,
    { ...size }
  );
}
