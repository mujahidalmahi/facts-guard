import type { Metadata } from 'next';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ jobId: string }>;
}): Promise<Metadata> {
  const { jobId } = await params;

  let mode = 'verify';
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const res = await fetch(`${apiUrl}/result/${jobId}?mode=verify`, {
      signal: AbortSignal.timeout(3000),
    });
    const data = await res.json();
    if (data.mode) mode = data.mode;
  } catch {}

  const ogUrl = `/result/${jobId}/og-image?mode=${mode}`;
  const title = 'FactGuard - Analysis Result';
  const desc = 'AI-powered fact verification & market analysis';

  return {
    title,
    description: desc,
    openGraph: {
      title,
      description: desc,
      images: [ogUrl],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description: desc,
      images: [ogUrl],
    },
  };
}

export default function ResultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
