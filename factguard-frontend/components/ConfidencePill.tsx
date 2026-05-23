import { Confidence } from '@/types';

const CONF_STYLE: Record<
  Confidence,
  string
> = {
  High:
    'bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-200 dark:border-green-700',
  Medium:
    'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-900 dark:text-amber-200 dark:border-amber-700',
  Low:
    'bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-200 dark:border-red-700',
};

export function ConfidencePill({
  confidence,
}: {
  confidence: Confidence;
}) {
  return (
    <span
      className={`text-xs font-semibold px-3 py-1 rounded border ${CONF_STYLE[confidence]}`}
    >
      {confidence === 'High'   ? 'High confidence' :
       confidence === 'Medium' ? 'Medium confidence' : 'Low confidence'}
    </span>
  );
}
