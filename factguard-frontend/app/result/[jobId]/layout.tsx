import type { Metadata } from 'next';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ jobId: string }>;
}): Promise<Metadata> {
  const { jobId } = await params;

  const title = 'FactGuard - Analysis Result';
  const desc = 'AI-powered fact verification & market analysis';

  return {
    title,
    description: desc,
    openGraph: {
      title,
      description: desc,
      images: [`/result/${jobId}/og-image`],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description: desc,
      images: [`/result/${jobId}/og-image`],
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
