import type { ProductVariant } from '@/types';

export function ProductVariants({
  variants,
}: {
  variants: ProductVariant[];
}) {
  if (variants.length === 0) {
    return null;
  }

  return (
    <section>
      <h2 className="text-lg font-semibold text-[var(--foreground)] mb-3">
        Other Models
      </h2>

      <div className="space-y-2">
        {variants.map(
          (v, i) => (
            <div
              key={i}
              className="flex items-center justify-between rounded-xl border border-[var(--card-border)] px-4 py-3 hover:bg-[var(--muted)]/40 transition-colors"
            >
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-[var(--foreground)] truncate">
                  {v.model}
                </p>
                {v.specs && (
                  <p className="text-xs text-[var(--muted-foreground)] mt-0.5">
                    {v.specs}
                  </p>
                )}
              </div>
              <span className="shrink-0 ml-4 text-sm font-semibold text-[var(--accent)]">
                {v.priceRange}
              </span>
            </div>
          )
        )}
      </div>
    </section>
  );
}
