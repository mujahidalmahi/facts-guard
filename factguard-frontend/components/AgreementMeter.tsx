interface Props {
  supports: number;
  contradicts: number;
  neutral: number;
}

export function AgreementMeter({
  supports,
  contradicts,
  neutral,
}: Props) {
  const totalSources = supports + contradicts + neutral;

  if (totalSources === 0) {
    return (
      <div className="rounded-xl border bg-white p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
          Source Breakdown
        </h3>
        <p className="text-sm text-slate-400 mt-2">
          No trusted sources found for this claim.
        </p>
      </div>
    );
  }

  const total = totalSources;
  const suppPct = (supports / total) * 100;
  const contPct = (contradicts / total) * 100;
  const neutPct = (neutral / total) * 100;

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
        Source Breakdown
      </h3>

      <div className="flex h-3 w-full rounded-full overflow-hidden origin-left animate-scale-x">
        <div className="bg-emerald-500" style={{ width: `${suppPct}%` }} />
        <div className="bg-slate-200" style={{ width: `${neutPct}%` }} />
        <div className="bg-red-400" style={{ width: `${contPct}%` }} />
      </div>

      <div className="grid grid-cols-3 mt-4 divide-x divide-slate-100">
        <div className="pr-4">
          <p className="text-2xl font-black text-emerald-700">{supports}</p>
          <p className="text-xs text-slate-400 uppercase tracking-wide mt-0.5">Support</p>
        </div>
        <div className="px-4">
          <p className="text-2xl font-black text-slate-400">{neutral}</p>
          <p className="text-xs text-slate-400 uppercase tracking-wide mt-0.5">Neutral</p>
        </div>
        <div className="pl-4">
          <p className="text-2xl font-black text-red-600">{contradicts}</p>
          <p className="text-xs text-slate-400 uppercase tracking-wide mt-0.5">Contradict</p>
        </div>
      </div>

      <p className="text-xs text-slate-400 mt-4">
        Based on {totalSources} trusted source{totalSources !== 1 ? 's' : ''} analysed
      </p>
    </div>
  );
}
