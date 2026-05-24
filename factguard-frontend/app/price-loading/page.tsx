'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { useJobPolling } from '@/lib/useJobPolling'

const PROGRESS_STEPS = [
  'Searching for prices...',
  'Analyzing product data...',
  'Saving results...',
]

function LoadingContent() {
  const searchParams = useSearchParams()
  const jobId = searchParams.get('job') || 'demo'
  const { progress, icon, pct } = useJobPolling(jobId, 'price-result', PROGRESS_STEPS)

  return (
    <main className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center bg-[var(--background)] px-6">
      <div className="text-center max-w-md w-full">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1.4, ease: 'linear' }}
          className="mx-auto h-16 w-16 rounded-full border-4 border-[var(--card-border)] border-t-[var(--accent)]"
        />

        <motion.h1
          key={progress}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 text-2xl font-semibold text-[var(--foreground)]"
        >
          {icon} {progress}
        </motion.h1>

        <p className="mt-3 text-[var(--muted-foreground)]">
          FactGuard is comparing prices across top retailers
        </p>

        <div className="mt-8 h-2 bg-[var(--muted)] rounded-full overflow-hidden">
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: `${pct}%` }}
            className="h-full bg-[var(--accent)]"
          />
        </div>
      </div>
    </main>
  )
}

export default function PriceLoadingPage() {
  return (
    <Suspense fallback={null}>
      <LoadingContent />
    </Suspense>
  )
}
