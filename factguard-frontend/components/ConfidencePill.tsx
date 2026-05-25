// Reusable confidence pill — used by Verify, Financial, Cart result views
const CFG = {
High: { bg: '#dcfce7', text: '#15803d', border: '#86efac', dot: '#16a34a' },
Medium: { bg: '#fef9c3', text: '#854d0e', border: '#fde047', dot: '#d97706' },
Low: { bg: '#fee2e2', text: '#b91c1c', border: '#fca5a5', dot: '#dc2626' },
};
export type Confidence = 'High' | 'Medium' | 'Low';
export function ConfidencePill({ confidence }: { confidence: Confidence }) {
const c = CFG[confidence] ?? CFG.Medium;
return (
<span
className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full
text-xs font-semibold border"
style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
>
<span
className="size-1.5 rounded-full"
style={{ backgroundColor: c.dot }}
/>
{confidence} Confidence
</span>
);
}
