'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

const examples = [
  'iPhone 16',
  'ASUS ROG Zephyrus G14',
  'AirPods Pro 2',
];

export function PriceCheckSection() {
  const [product, setProduct] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleCompare() {
    if (!product.trim()) return;
    if (product.length > 500) {
      alert('Product name is too long (max 500 characters)');
      return;
    }

    try {
      setLoading(true);

      const res = await fetch(
        `${API_URL}/price-check`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ product }),
        }
      );

      if (!res.ok) {
        throw new Error('Failed request');
      }

      const data = await res.json();
      const jobId = data.jobId || 'demo';

      router.push(`/loading?mode=cart&job=${jobId}`);
    } catch (error) {
      console.error(error);
      alert('Failed to compare prices');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="text-center">
      <h2 className="text-2xl font-bold text-[var(--foreground)]">
        Compare Prices
      </h2>

      <p className="text-[var(--muted-foreground)] mt-2 text-sm">
        Find the best price across top retailers
      </p>

      <input
        value={product}
        onChange={(e) => setProduct(e.target.value)}
        placeholder="Enter a product..."
        maxLength={500}
        className="w-full mt-6 rounded-2xl border border-[var(--card-border)] p-4 text-base outline-none focus:ring-2 focus:ring-[var(--accent)] bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)]"
      />

      <button
        onClick={handleCompare}
        disabled={loading}
        className="w-full mt-4 bg-[var(--accent)] hover:bg-[var(--accent-hover)] transition-colors text-white py-4 rounded-2xl text-base font-semibold disabled:opacity-60"
      >
        {loading ? 'Searching...' : 'Compare Prices'}
      </button>

      <div className="flex flex-wrap justify-center gap-2 mt-6">
        {examples.map((example) => (
          <button
            key={example}
            onClick={() => setProduct(example)}
            className="px-3 py-1.5 rounded-full border border-[var(--card-border)] text-xs text-[var(--muted-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
