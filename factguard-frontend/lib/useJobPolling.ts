'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const POLL_INTERVAL = 1500

const PROGRESS_ICONS: Record<string, string> = {
  'Checking cache...': '🔍',
  'Searching DuckDuckGo...': '🌐',
  'Analyzing with AI...': '🤖',
  'Saving results...': '💾',
  'Searching for prices...': '🔍',
  'Analyzing product data...': '📊',
  Failed: '❌',
}

export function useJobPolling(jobId: string, resultPath: string, progressSteps: string[]) {
  const router = useRouter()
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const [progress, setProgress] = useState('Processing...')

  useEffect(() => {
    async function poll() {
      try {
        const res = await fetch(`${API_URL}/${resultPath}/${jobId}`)
        if (!res.ok) return

        const data = await res.json()

        if (data.progress) {
          setProgress(data.progress)
        }

        if (data.status && data.status !== 'processing') {
          clearInterval(intervalRef.current!)
          router.push(`/${resultPath}/${jobId}`)
        }
      } catch {
        // retry on next interval
      }
    }

    intervalRef.current = setInterval(poll, POLL_INTERVAL)
    poll()

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [router, jobId, resultPath])

  const icon = PROGRESS_ICONS[progress] || '⏳'

  const stepIndex = progressSteps.indexOf(progress)
  const pct = stepIndex >= 0
    ? ((stepIndex + 1) / progressSteps.length) * 100
    : 50

  return { progress, icon, pct }
}
