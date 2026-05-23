import { VerifyResult } from '@/types';

const BASE = process.env.NEXT_PUBLIC_API_URL;

export async function postVerify(
  claim: string
): Promise<{ jobId: string }> {
  const res = await fetch(`${BASE}/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ claim }),
  });

  if (!res.ok) {
    throw new Error('Verify failed');
  }

  return res.json();
}

export async function getResult(
  jobId: string
): Promise<VerifyResult | null> {
  const res = await fetch(`${BASE}/result/${jobId}`);

  if (res.status === 202) {
    return null;
  }

  if (!res.ok) {
    throw new Error('Result fetch failed');
  }

  return res.json();
}
