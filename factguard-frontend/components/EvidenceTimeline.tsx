import { Source } from '@/types';

export function EvidenceTimeline({
  sources,
}: {
  sources: Source[];
}) {
  const sortedSources = [...sources].sort((a, b) => {
    const tierA = (a as any).tier ?? 4;
    const tierB = (b as any).tier ?? 4;
    if (tierA !== tierB) return tierA - tierB;
    return b.relevance - a.relevance;
  });

  return (
    <div className="divide-y divide-[var(--card-border)]">
      {sortedSources.map((s, idx) => (
        <a
          key={s.url}
          href={s.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex gap-4 py-4 group transition-colors hover:bg-[var(--muted)] -mx-4 px-4 animate-fade-in rounded-lg"
          style={{ animationDelay: `${idx * 80}ms` }}
        >
          <div className={`w-0.5 shrink-0 self-stretch rounded-full mt-1
            ${s.stance === 'supports'    ? 'bg-emerald-500' :
              s.stance === 'contradicts' ? 'bg-red-500'     : 'bg-slate-300 dark:bg-slate-600'}`}
          />

          <div className="flex-1 min-w-0">
            <div className="flex items-baseline gap-2 mb-0.5">
              <span className="text-sm font-semibold text-[var(--foreground)] group-hover:text-[var(--accent)] transition-colors line-clamp-1">
                {s.title}
              </span>
              <span className="text-xs text-[var(--muted-foreground)] font-mono shrink-0">
                {s.relevance}/10
              </span>
              {(s as any).tier && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono
                  ${(s as any).tier === 1 ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' :
                    (s as any).tier === 2 ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20' :
                    'bg-slate-500/10 text-slate-400 border border-slate-500/20'}`}
                >
                  T{(s as any).tier}
                </span>
              )}
            </div>

            <p className="text-xs text-[var(--muted-foreground)] mb-1">
              {[s.author, s.date].filter(Boolean).join(' · ')}
            </p>

            <p className="text-sm text-[var(--foreground)] leading-relaxed">
              {s.summary}
            </p>

            {s.quote && (
              <p className="mt-1.5 text-xs text-[var(--muted-foreground)] font-mono border-l-2 border-[var(--card-border)] pl-2">
                &ldquo;{s.quote}&rdquo;
              </p>
            )}
          </div>
        </a>
      ))}
    </div>
  );
}
