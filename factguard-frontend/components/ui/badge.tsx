import { cn } from "@/lib/utils"

const VARIANT_CLASS: Record<string, string> = {
  default: "bg-indigo-600 text-white",
  secondary: "bg-slate-100 text-slate-700",
  destructive: "bg-red-100 text-red-700",
  outline: "border border-slate-300 text-slate-700",
  ghost: "text-slate-500 hover:bg-slate-100",
  link: "text-indigo-600 underline-offset-4 hover:underline",
}

function Badge({
  className,
  variant = "default",
  ...props
}: React.ComponentProps<"span"> & { variant?: string }) {
  return (
    <span
      className={cn(
        "inline-flex h-5 w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap",
        VARIANT_CLASS[variant] || VARIANT_CLASS.default,
        className
      )}
      {...props}
    />
  )
}

export { Badge }
