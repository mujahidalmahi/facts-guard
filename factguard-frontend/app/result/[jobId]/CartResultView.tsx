'use client';

import { motion } from 'framer-motion';
import {
  Star,
  AlertTriangle,
} from 'lucide-react';

import { CartProductCard } from '@/components/CartProductCard';

import type {
  CartResult,
} from '@/types';

export function CartResultView({
  data,
}: {
  data: CartResult;
}) {
  const a = data.analysis;

  return (
    <main className='max-w-3xl mx-auto px-4 py-10 space-y-8'>
      {/* Verdict headline */}
      <motion.div
        initial={{
          opacity: 0,
          y: 16,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          type: 'spring',
          stiffness: 260,
          damping: 20,
        }}
        className='space-y-2'
      >
        <h1 className='text-4xl font-black text-[var(--foreground)]'>
          {data.product}
        </h1>

        <p className='text-xl font-bold text-[var(--accent)]'>
          {a.verdict}
        </p>

        <p className='text-sm text-[var(--muted-foreground)]'>
          Price range:{' '}
          <span className='text-[var(--foreground)] font-semibold'>
            {a.price_range?.low} –{' '}
            {a.price_range?.high}
          </span>

          {a.market_average &&
            ` · Market avg: ${a.market_average}`}
        </p>
      </motion.div>

      {/* Best Deal */}
      {a.best_deal && (
        <div
          className='rounded-2xl border-2
          border-amber-400
          bg-amber-50
          dark:bg-amber-950
          dark:border-amber-600
          p-5'
        >
          <div className='flex items-center gap-2 mb-2'>
            <Star className='size-4 text-amber-500 fill-amber-500' />

            <span className='text-sm font-bold text-amber-700 dark:text-amber-300'>
              Best Deal
            </span>
          </div>

          <p className='font-bold text-[var(--foreground)]'>
            {a.best_deal.platform}
          </p>

          <p className='text-2xl font-black text-amber-600 dark:text-amber-400'>
            {a.best_deal.price}
          </p>

          <p className='text-sm text-[var(--muted-foreground)] mt-1'>
            {a.best_deal.why}
          </p>
        </div>
      )}

      {/* Recommendation */}
      <p className='text-[var(--foreground)] leading-relaxed'>
        {a.recommendation}
      </p>

      {/* Warnings */}
      {a.warnings?.length >
        0 && (
        <div className='space-y-2'>
          {a.warnings.map(
            (w, i) => (
              <div
                key={i}
                className='flex items-start gap-2
                p-3 rounded-xl
                bg-red-50
                dark:bg-red-950
                border border-red-200
                dark:border-red-800'
              >
                <AlertTriangle className='size-4 text-red-500 shrink-0 mt-0.5' />

                <p className='text-sm text-red-700 dark:text-red-300'>
                  {w}
                </p>
              </div>
            )
          )}
        </div>
      )}

      {/* Product Grid */}
      <section>
        <h2 className='text-lg font-semibold mb-4'>
          Listings Found (
          {data.listings
            ?.length ?? 0}
          )
        </h2>

        <div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
          {data.listings?.map(
            (l, i) => (
              <motion.div
                key={i}
                initial={{
                  opacity: 0,
                  y: 12,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay:
                    i * 0.06,
                }}
              >
                <CartProductCard
                  listing={l}
                />
              </motion.div>
            )
          )}
        </div>
      </section>
    </main>
  );
}