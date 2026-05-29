export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-md bg-[var(--muted)] ${className ?? ''}`}
    />
  )
}

export function ResultSkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      <Skeleton className="h-20 w-full rounded-xl" />
      <div className="flex gap-3">
        <Skeleton className="h-8 w-32 rounded" />
        <Skeleton className="h-8 w-20 rounded" />
      </div>
      <Skeleton className="h-12 w-full rounded-lg" />
      <Skeleton className="h-32 w-full rounded-xl" />
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-lg" />
        ))}
      </div>
    </div>
  )
}

export function HistorySkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-4">
      <Skeleton className="h-8 w-56 rounded-lg" />
      <Skeleton className="h-4 w-40 rounded" />
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-16 w-full rounded-lg" />
      ))}
    </div>
  )
}
