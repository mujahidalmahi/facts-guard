import { cn } from "@/lib/utils"

const VARIANT_CLASS: Record<string, string> = {
  default: "bg-indigo-600 text-white hover:bg-indigo-700",
  outline:
    "border border-slate-300 bg-white hover:bg-slate-50",
  secondary:
    "bg-slate-100 text-slate-900 hover:bg-slate-200",
  ghost: "text-slate-600 hover:bg-slate-100",
  destructive:
    "bg-red-100 text-red-700 hover:bg-red-200",
  link: "text-indigo-600 underline-offset-4 hover:underline",
}

const SIZE_CLASS: Record<string, string> = {
  default: "h-8 px-2.5 text-sm",
  xs: "h-6 px-2 text-xs",
  sm: "h-7 px-2.5 text-[0.8rem]",
  lg: "h-9 px-2.5 text-sm",
  icon: "size-8",
}

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: React.ComponentProps<"button"> & {
  variant?: string
  size?: string
}) {
  return (
    <button
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-lg font-medium whitespace-nowrap transition-all disabled:pointer-events-none disabled:opacity-50",
        VARIANT_CLASS[variant] || VARIANT_CLASS.default,
        SIZE_CLASS[size] || SIZE_CLASS.default,
        className
      )}
      {...props}
    />
  )
}

export { Button }
