'use client';

import { use, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';

import { PriceComparisonTable } from '@/components/PriceComparisonTable';
import { ProductVariants } from '@/components/ProductVariants';
import { PriceShareCard } from '@/components/PriceShareCard';
import type {
  ProductListing,
  ProductVariant,
} from '@/types';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

export default function PriceResultPage({
  params,
}: {
  params: Promise<{
    jobId: string;
  }>;
}) {
  const { jobId } = use(params);
  const router = useRouter();

  const [product, setProduct] =
    useState<string | null>(null);
  const [listings, setListings] =
    useState<ProductListing[]>([]);
  const [variants, setVariants] =
    useState<ProductVariant[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller =
      new AbortController();

    fetch(
      `${API_URL}/price-result/${jobId}`,
      {
        signal:
          controller.signal,
      }
    )
      .then((res) => {
        if (!res.ok)
          throw new Error(
            res.status === 404
              ? 'Result not found'
              : 'Server error'
          );
        return res.json();
      })
      .then((result) => {
        if (
          controller.signal
            .aborted
        )
          return;
        if (
          result.status &&
          result.status ===
            'processing'
        ) {
          router.push(
            `/price-loading?job=${jobId}`
          );
          return;
        }
        setProduct(
          result.product ??
            null
        );
        setListings(
          result.listings ??
            []
        );
        setVariants(
          result.variants ??
            []
        );
      })
      .catch((err) => {
        if (
          controller.signal
            .aborted
        )
          return;
        setError(true);
        console.error(err);
      });

    return () =>
      controller.abort();
  }, [jobId, router]);

  if (error) {
    return (
      <main className="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center gap-4 px-6">
        <p className="text-red-600 text-lg font-semibold">
          Failed to load price results
        </p>
        <p className="text-[var(--muted-foreground)] text-sm">
          The price comparison could not be loaded. Please try again.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm hover:bg-[var(--accent-hover)] transition-colors"
        >
          Retry
        </button>
      </main>
    );
  }

  if (!product) {
    return (
      <main className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center">
        <p className="text-[var(--muted-foreground)]">
          Loading price comparison...
        </p>
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <motion.div
        initial={{
          opacity: 0,
          y: -12,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
      >
        <p className="text-xs text-[var(--muted-foreground)] uppercase tracking-widest font-semibold">
          Price Comparison
        </p>
        <h1 className="text-3xl font-bold text-[var(--foreground)] mt-1">
          {product}
        </h1>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          {listings.length}{' '}
          listing
          {listings.length !== 1
            ? 's'
            : ''}{' '}
          found across top
          retailers
        </p>
      </motion.div>

      <PriceComparisonTable
        listings={listings}
      />

      <ProductVariants
        variants={variants}
      />

      <PriceShareCard
        jobId={jobId}
        product={product}
        listings={listings}
        variants={variants}
      />
    </main>
  );
}
