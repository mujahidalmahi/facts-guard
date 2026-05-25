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
  const an = a.analysis;

  return (
    <main className='max-w-3xl mx-auto px-4 py-10 space-y-8'>
      {/* Product headline */}
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
          {a.product_name || data.product}
        </h1>

        <p className='text-sm text-[var(--muted-foreground)]'>
          Fair market range:{' '}
          <span className='text-[var(--foreground)] font-semibold'>
            {a.fair_market_range?.min} –{' '}
            {a.fair_market_range?.max}
          </span>

          {a.msrp &&
            ` · MSRP: ${a.msrp}`}
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
            {a.best_deal.merchant}
          </p>

          <p className='text-2xl font-black text-amber-600 dark:text-amber-400'>
            {a.best_deal.price}
          </p>

          <p className='text-sm text-[var(--muted-foreground)] mt-1'>
            {a.best_deal.reason}
          </p>
        </div>
      )}

      {/* Recommendation */}
      <p className='text-[var(--foreground)] leading-relaxed'>
        {an?.recommendation}
      </p>

      {/* Warnings */}
      {an?.warnings?.length >
        0 && (
        <div className='space-y-2'>
          {an.warnings.map(
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

      {/* Price Trend & Best Time */}
      {an && (
        <div className="flex gap-4 text-sm">
          <span className="text-[var(--muted-foreground)]">
            Trend: <span className={`font-semibold ${
              an.price_trend === 'Rising' ? 'text-green-400' :
              an.price_trend === 'Dropping' ? 'text-red-400' :
              'text-amber-400'
            }`}>{an.price_trend}</span>
          </span>
          <span className="text-[var(--muted-foreground)]">
            Best time: <span className={`font-semibold ${
              an.best_time_to_buy === 'Now' ? 'text-green-400' :
              an.best_time_to_buy === 'Urgent' ? 'text-amber-400' :
              'text-slate-400'
            }`}>{an.best_time_to_buy}</span>
          </span>
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