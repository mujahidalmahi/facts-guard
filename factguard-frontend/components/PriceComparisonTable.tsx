import type { ProductListing } from '@/types';

const TRUST_COLORS: Record<
  string,
  string
> = {
  High: 'text-green-500',
  Medium:
    'text-yellow-500',
  Low: 'text-red-500',
};

const TRUST_LABELS: Record<
  string,
  string
> = {
  High: '🟢',
  Medium: '🟡',
  Low: '🔴',
};

function formatPrice(
  price: number | null,
  currency: string
): string {
  if (price == null) return '—';

  const symbols: Record<
    string,
    string
  > = {
    USD: '$',
    EUR: '€',
    GBP: '£',
  };

  const sym =
    symbols[currency] ||
    currency + ' ';

  return `${sym}${price.toLocaleString(
    undefined,
    { minimumFractionDigits: 2 }
  )}`;
}

export function PriceComparisonTable({
  listings,
}: {
  listings: ProductListing[];
}) {
  if (listings.length === 0) {
    return (
      <p className="text-sm text-[var(--muted-foreground)]">
        No listings found.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-[var(--card-border)]">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-[var(--muted)] text-[var(--muted-foreground)]">
            <th className="text-left px-4 py-3 font-medium">
              Merchant
            </th>
            <th className="text-left px-4 py-3 font-medium">
              Product
            </th>
            <th className="text-right px-4 py-3 font-medium">
              Price
            </th>
            <th className="px-4 py-3 font-medium">
              Condition
            </th>
            <th className="px-4 py-3">
              Link
            </th>
          </tr>
        </thead>
        <tbody>
          {listings.map(
            (item, i) => (
              <tr
                key={i}
                className="border-t border-[var(--card-border)] hover:bg-[var(--muted)]/40 transition-colors"
              >
                <td className="px-4 py-3 font-medium text-[var(--foreground)] whitespace-nowrap">
                  <span className="mr-1.5">
                    {TRUST_LABELS[
                      item.trustLevel
                    ] || '⚪'}
                  </span>
                  {
                    item.merchant
                  }
                </td>
                <td className="px-4 py-3 text-[var(--foreground)] max-w-xs truncate">
                  {
                    item.title
                  }
                </td>
                <td className="px-4 py-3 text-right font-semibold text-[var(--foreground)] whitespace-nowrap">
                  {formatPrice(
                    item.price,
                    item.currency
                  )}
                </td>
                <td className="px-4 py-3 text-center text-[var(--muted-foreground)] capitalize">
                  {item.condition ??
                    'New'}
                </td>
                <td className="px-4 py-3 text-center">
                  <a
                    href={
                      item.url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--accent)] hover:text-[var(--accent-hover)] underline underline-offset-2 text-xs font-semibold"
                  >
                    View
                  </a>
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  );
}
