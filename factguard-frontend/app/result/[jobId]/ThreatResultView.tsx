'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, ShieldAlert, FileText, ExternalLink, Download } from 'lucide-react';
import type { ThreatResult } from '@/types';

const SEVERITY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  critical: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
  high: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/20' },
  medium: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
  low: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/20' },
};

const TYPE_LABELS: Record<string, string> = {
  brand: 'Brand Threat',
  regulatory: 'Regulatory Change',
  vendor: 'Vendor Risk',
  disinformation: 'Disinformation Campaign',
  general: 'General Alert',
};

interface ThreatViewData {
  threats?: ThreatResult[];
  report?: string;
}

function downloadReport(threats: ThreatResult[]) {
  const lines = [
    "=== FACTGUARD COMPLIANCE REPORT ===",
    `Generated: ${new Date().toISOString()}`,
    `Total threats: ${threats.length}`,
    "",
  ];
  threats.forEach((t, i) => {
    lines.push(`--- Threat #${i + 1} ---`);
    lines.push(`Type: ${t.threat_type ?? "unknown"}`);
    lines.push(`Severity: ${t.severity ?? "unknown"}`);
    lines.push(`Title: ${t.title ?? "N/A"}`);
    lines.push(`Source: ${t.source_url ?? "N/A"}`);
    lines.push(`Description: ${t.description ?? "N/A"}`);
    lines.push(`Confidence: ${t.confidence ?? 0}`);
    lines.push("");
  });
  const blob = new Blob([lines.join("\n")], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "factguard-compliance-report.txt";
  a.click();
  URL.revokeObjectURL(a.href);
}

export function ThreatResultView({ data }: { data: ThreatViewData }) {
  const threats = data.threats ?? [];
  const report = data.report;

  return (
    <main className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        <div className="flex items-center gap-3">
          <AlertTriangle className="size-6 text-red-400" />
          <h1 className="text-2xl font-black tracking-tight">Threat Scan Results</h1>
        </div>
        <p className="text-sm text-[var(--muted-foreground)]">
          {threats.length} potential threat{threats.length !== 1 ? 's' : ''} detected
        </p>
      </motion.div>

      {threats.length === 0 && (
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-6 text-center">
          <ShieldAlert className="size-8 text-emerald-400 mx-auto mb-2" />
          <p className="text-emerald-400 font-semibold">No threats detected</p>
          <p className="text-sm text-[var(--muted-foreground)]">Your scan returned zero risk signals.</p>
        </div>
      )}

      <div className="space-y-4">
        {threats.map((t: ThreatResult, i: number) => {
          const colors = SEVERITY_COLORS[t.severity ?? 'low'] ?? SEVERITY_COLORS.low;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`rounded-xl border ${colors.border} ${colors.bg} p-5 space-y-3`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold uppercase tracking-wider ${colors.text}`}>
                    {t.severity}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${colors.border} ${colors.text}`}>
                    {TYPE_LABELS[t.threat_type] ?? t.threat_type}
                  </span>
                </div>
                <span className="text-xs text-[var(--muted-foreground)] font-mono">
                  {(t.confidence * 100).toFixed(0)}% confidence
                </span>
              </div>

              <h3 className="font-semibold text-[var(--foreground)]">{t.title}</h3>

              {t.description && (
                <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">{t.description}</p>
              )}

              <div className="flex items-center gap-2 text-xs text-[var(--muted-foreground)]">
                {t.source_url && (
                  <a
                    href={t.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[var(--accent)] hover:underline"
                  >
                    <ExternalLink className="size-3" />
                    {t.source_domain ?? t.source_url}
                  </a>
                )}
              </div>

              <div className="w-full bg-[var(--card-border)] rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${t.severity === 'critical' ? 'bg-red-500' : t.severity === 'high' ? 'bg-orange-500' : t.severity === 'medium' ? 'bg-amber-500' : 'bg-yellow-400'}`}
                  style={{ width: `${(t.confidence ?? 0) * 100}%` }}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => downloadReport(threats)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-[var(--card-border)] bg-[var(--card)] hover:bg-[var(--card-hover)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
        >
          <Download className="size-3.5" />
          Download Report
        </button>
      </div>

      {report && (
        <div className="rounded-xl border border-[var(--card-border)] bg-[var(--card)] p-5 space-y-3">
          <div className="flex items-center gap-2">
            <FileText className="size-4 text-[var(--muted-foreground)]" />
            <h3 className="text-sm font-semibold text-[var(--muted-foreground)] uppercase tracking-wide">
              Compliance Report
            </h3>
          </div>
          <pre className="text-xs font-mono text-[var(--muted-foreground)] whitespace-pre-wrap max-h-96 overflow-y-auto">
            {report}
          </pre>
        </div>
      )}
    </main>
  );
}
