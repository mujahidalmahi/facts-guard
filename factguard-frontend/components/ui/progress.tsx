function Progress({
  className,
  value = 0,
  ...props
}: React.ComponentProps<"div"> & { value?: number }) {
  return (
    <div
      className={`relative flex h-1 w-full items-center overflow-hidden rounded-full bg-slate-200 ${className ?? ''}`}
      {...props}
    >
      <div
        className="h-full bg-indigo-600 transition-all duration-500"
        style={{ width: `${Math.min(value, 100)}%` }}
      />
    </div>
  )
}

export { Progress }
