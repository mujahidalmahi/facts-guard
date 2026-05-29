function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={`flex flex-col gap-4 overflow-hidden rounded-xl border bg-white p-4 text-sm shadow-sm ${className ?? ''}`}
      {...props}
    />
  )
}

function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={`flex items-start justify-between gap-1 ${className ?? ''}`}
      {...props}
    />
  )
}

function CardTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={`text-base leading-snug font-medium ${className ?? ''}`}
      {...props}
    />
  )
}

function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={`text-sm text-slate-500 ${className ?? ''}`}
      {...props}
    />
  )
}

function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div className={className ?? ''} {...props} />
  )
}

function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={`flex items-center rounded-b-xl border-t bg-slate-50 p-4 ${className ?? ''}`}
      {...props}
    />
  )
}

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
}
