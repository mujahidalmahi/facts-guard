import { Source } from '@/types';

export function EvidenceTimeline({
  sources,
}: {
  sources: Source[];
}) {
  const sortedSources = [...sources].sort((a, b) => b.relevance - a.relevance);

  return (
    <div className="divide-y divide-slate-100">
      {sortedSources.map((s) => (
        <a
          key={s.url}
          href={s.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex gap-4 py-4 group transition-colors hover:bg-slate-50 -mx-4 px-4 animate-fade-in"
          style={{ animationDelay: `${sortedSources.indexOf(s) * 80}ms` }}
        >
          <div className={`w-0.5 shrink-0 self-stretch rounded-full mt-1
            ${s.stance === 'supports'    ? 'bg-emerald-500' :
              s.stance === 'contradicts' ? 'bg-red-500'     : 'bg-slate-300'}`}
          />

          <div className="flex-1 min-w-0">
            <div className="flex items-baseline gap-2 mb-0.5">
              <span className="text-sm font-semibold text-slate-800 group-hover:text-indigo-700 transition-colors line-clamp-1">
                {s.title}
              </span>
              <span className="text-xs text-slate-400 font-mono shrink-0">
                {s.relevance}/10
              </span>
            </div>

            <p className="text-xs text-slate-400 mb-1">
              {[s.author, s.date].filter(Boolean).join(' · ')}
            </p>

            <p className="text-sm text-slate-600 leading-relaxed">
              {s.summary}
            </p>

            {s.quote && (
              <p className="mt-1.5 text-xs text-slate-500 font-mono border-l-2 border-slate-200 pl-2">
                &ldquo;{s.quote}&rdquo;
              </p>
            )}
          </div>
        </a>
      ))}
    </div>
  );
}
