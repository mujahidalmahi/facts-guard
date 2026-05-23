import { VERDICT_COLORS } from '@/lib/constants';
import { Verdict } from '@/types';

export function VerdictBadge({
  verdict,
}: {
  verdict: Verdict;
}) {
  return (
    <span
      className={`inline-block px-4 py-1.5 rounded text-sm font-bold uppercase tracking-widest ${VERDICT_COLORS[verdict]}`}
    >
      {verdict}
    </span>
  );
}