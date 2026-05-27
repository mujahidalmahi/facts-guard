'use client'

import { useEffect, useRef, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const MAX_POLL_MS = 90_000
const INITIAL_INTERVAL = 1000
const MAX_INTERVAL = 5000

const PROGRESS_ICONS: Record<string, string> = {
  'Checking cache...': '🔍',
  'Searching DuckDuckGo...': '🌐',
  'Searching via Bright Data...': '🌐',
  'Analyzing with AI...': '🤖',
  'Analysing with AI...': '🤖',
  'Saving results...': '💾',
  'Searching for prices...': '🔍',
  'Analyzing product data...': '📊',
  Failed: '❌',
}

const POLL_PATHS: Record<string, string> = {
  verify: '/result',
  financial: '/financial-result',
  cart: '/price-result',
  security: '/threats/result',
}

export function useJobPolling(jobId: string, resultPath: string, progressSteps: string[], mode: string = 'verify') {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const startedRef = useRef(Date.now())
  const intervalRef = useRef(INITIAL_INTERVAL)
  const [progress, setProgress] = useState('Processing...')
  const [status, setStatus] = useState<string>('processing')
  const pollPath = POLL_PATHS[mode] ?? '/result'

  useEffect(() => {
    startedRef.current = Date.now()
    intervalRef.current = INITIAL_INTERVAL

    async function poll() {
      if (Date.now() - startedRef.current > MAX_POLL_MS) {
        setProgress('timeout')
        setStatus('timeout')
        return
      }

      try {
        const res = await fetch(`${API_URL}${pollPath}/${jobId}?mode=${mode}`)
        if (!res.ok) return

        const data = await res.json()

        if (data.progress) {
          setProgress(data.progress)
        }

        if (data.status && data.status !== 'processing') {
          setStatus(data.status)
          return
        }
      } catch {
        // retry on next interval
      }

      intervalRef.current = Math.min(intervalRef.current * 1.5, MAX_INTERVAL)
      timerRef.current = setTimeout(poll, intervalRef.current)
    }

    timerRef.current = setTimeout(poll, INITIAL_INTERVAL)

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [jobId, mode, pollPath])

  const icon = PROGRESS_ICONS[progress] || '⏳'

  const stepIndex = progressSteps.indexOf(progress)
  const pct = stepIndex >= 0
    ? ((stepIndex + 1) / progressSteps.length) * 100
    : 50

  return { progress, icon, pct, status }
}
