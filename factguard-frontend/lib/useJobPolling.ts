'use client'

import { useEffect, useRef, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const MAX_POLL_MS = 150_000
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
  // eslint-disable-next-line react-hooks/purity
  const startedRef = useRef(Date.now())
  const intervalRef = useRef(INITIAL_INTERVAL)
  const mountedRef = useRef(true)
  const [progress, setProgress] = useState('Processing...')
  const [status, setStatus] = useState<string>('processing')
  const pollPath = POLL_PATHS[mode] ?? '/result'

  useEffect(() => {
    mountedRef.current = true
    startedRef.current = Date.now()
    intervalRef.current = INITIAL_INTERVAL
    let abortController: AbortController | undefined

    async function poll() {
      if (!mountedRef.current) return
      if (Date.now() - startedRef.current > MAX_POLL_MS) {
        mountedRef.current && setProgress('timeout')
        mountedRef.current && setStatus('timeout')
        return
      }

      abortController?.abort()
      abortController = new AbortController()

      try {
        const res = await fetch(`${API_URL}${pollPath}/${jobId}?mode=${mode}`, {
          signal: abortController.signal,
        })
        if (!mountedRef.current) return
        if (!res.ok) throw new Error(`HTTP ${res.status}`)

        const data = await res.json()
        if (!mountedRef.current) return

        if (data.progress) {
          setProgress(data.progress)
        }

        if (data.status && data.status !== 'processing') {
          setStatus(data.status)
          return
        }
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return
      }

      intervalRef.current = Math.min(intervalRef.current * 1.5, MAX_INTERVAL)
      timerRef.current = setTimeout(poll, intervalRef.current)
    }

    timerRef.current = setTimeout(poll, INITIAL_INTERVAL)

    return () => {
      mountedRef.current = false
      abortController?.abort()
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
