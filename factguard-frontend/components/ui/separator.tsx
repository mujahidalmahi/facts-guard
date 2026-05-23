function Separator({
  className,
  orientation = "horizontal",
  ...props
}: React.ComponentProps<"hr"> & { orientation?: "horizontal" | "vertical" }) {
  return (
    <hr
      className={`shrink-0 bg-slate-200 ${
        orientation === "vertical"
          ? "w-px self-stretch"
          : "h-px w-full"
      } ${className ?? ''}`}
      {...props}
    />
  )
}

export { Separator }
