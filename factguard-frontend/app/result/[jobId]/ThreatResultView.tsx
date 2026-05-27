'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, Building2, Scale, Link2, Radio, ShieldCheck, Download, CheckCircle, Clock, Eye } from 'lucide-react';
import type { ThreatResult, Severity } from '@/types';

const SEVERITY_CONFIG: Record<Severity, { color: string; label: string; bg: string }> = {
  critical: { color: '#EF4444', label: 'CRITICAL', bg: 'rgba(239, 68, 68, 0.1)' },
  high: { color: '#F97316', label: 'HIGH', bg: 'rgba(249, 115, 22, 0.1)' },
  medium: { color: '#F59E0B', label: 'MEDIUM', bg: 'rgba(245, 158, 11, 0.1)' },
  low: { color: '#FBBF24', label: 'LOW', bg: 'rgba(251, 191, 36, 0.1)' },
};

const THREAT_TYPE_META: Record<string, { icon: React.ElementType; label: string }> = {
  brand: { icon: Building2, label: 'Brand Threat' },
  regulatory: { icon: Scale, label: 'Regulatory' },
  vendor: { icon: Link2, label: 'Vendor Risk' },
  disinformation: { icon: Radio, label: 'Disinformation' },
  general: { icon: AlertTriangle, label: 'General Alert' },
};

const STATUS_META: Record<string, { color: string; label: string; pulse: boolean }> = {
  new: { color: '#EF4444', label: 'NEW', pulse: true },
  acknowledged: { color: '#F59E0B', label: 'ACKNOWLEDGED', pulse: false },
  investigating: { color: '#F59E0B', label: 'INVESTIGATING', pulse: true },
  resolved: { color: '#10B981', label: 'RESOLVED', pulse: false },
  dismissed: { color: '#64748B', label: 'DISMISSED', pulse: false },
};

function relativeTime(iso: string): string {
  const ts = new Date(iso).getTime();
  if (isNaN(ts)) return '';
  const diff = (Date.now() - ts) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

interface ThreatViewData {
  threats?: ThreatResult[];
  report?: string;
}

export function ThreatResultView({ data }: { data: ThreatViewData }) {
  const threats = data.threats ?? [];

  const severityCounts = threats.reduce(
    (acc, t) => { acc[t.severity as Severity]++; return acc; },
    { critical: 0, high: 0, medium: 0, low: 0 } as Record<Severity, number>
  );

  const typeCounts = threats.reduce(
    (acc, t) => { acc[t.threat_type] = (acc[t.threat_type] || 0) + 1; return acc; },
    {} as Record<string, number>
  );

  const handleDownload = () => {
    const report = `THREATGUARD COMPLIANCE REPORT
====================================
Generated: ${new Date().toISOString()}
Total Threats: ${threats.length}

Severity Breakdown:
- Critical: ${severityCounts.critical}
- High: ${severityCounts.high}
- Medium: ${severityCounts.medium}
- Low: ${severityCounts.low}

THREAT DETAILS:
====================================

${threats.map((t, i) => `${i + 1}. [${t.severity.toUpperCase()}] ${t.title}
   Type: ${t.threat_type}
   Status: ${t.alert_status}
   Confidence: ${t.confidence}%
   Source: ${t.source_domain}
   Detected: ${new Date(t.detected_at).toLocaleString()}

   ${t.description}
`).join('\n')}

COMPLIANCE NOTES:
====================================
${(typeCounts.regulatory ?? 0) > 0 ? '- Review GDPR compliance requirements\n' : ''}${severityCounts.critical > 0 ? '- URGENT: Address all critical threats immediately\n' : ''}- Document remediation timeline for each finding
- Schedule follow-up scan in 7 days

Powered by FactGuard ThreatGuard Engine
`;
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `threatguard-report-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const complianceNotes: string[] = [];
  if ((typeCounts.regulatory ?? 0) > 0) complianceNotes.push('Review GDPR / SOC 2 compliance requirements for regulatory findings.');
  if ((typeCounts.disinformation ?? 0) > 0) complianceNotes.push('Activate incident response for coordinated disinformation campaigns.');
  if ((typeCounts.vendor ?? 0) > 0) complianceNotes.push('Rotate credentials for affected vendor integrations.');
  if ((typeCounts.brand ?? 0) > 0) complianceNotes.push('Initiate brand protection takedown procedures.');
  if (complianceNotes.length === 0) complianceNotes.push('Standard threat monitoring protocols apply.');

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
          <div>
            <div className="data-label mb-2 flex items-center gap-2">
              <AlertTriangle className="w-3 h-3" style={{ color: 'var(--color-accent-amber)' }} />
              THREAT SURFACE SCAN · {threats.length} FINDINGS
            </div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>ThreatGuard Report</h1>
          </div>
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:scale-105"
            style={{ backgroundColor: '#4F46E5', boxShadow: '0 0 20px rgba(79, 70, 229, 0.3)' }}
          >
            <Download className="w-4 h-4" /> Download Report
          </button>
        </div>

        <div
          className="rounded-2xl p-4 flex items-center gap-6 flex-wrap"
          style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
        >
          <div>
            <div className="data-label">TOTAL</div>
            <div className={`font-mono text-3xl font-black ${threats.length > 0 ? 'text-[var(--color-accent-red)]' : 'text-[var(--color-accent-emerald)]'}`}>
              {threats.length}
            </div>
          </div>
          <div className="w-px h-10" style={{ backgroundColor: 'var(--color-border-subtle)' }} />
          {(Object.keys(SEVERITY_CONFIG) as Severity[]).map((sev) => (
            <div key={sev}>
              <div className="data-label">{sev.toUpperCase()}</div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-mono text-sm font-bold"
                style={{ color: SEVERITY_CONFIG[sev].color, backgroundColor: SEVERITY_CONFIG[sev].bg, border: `1px solid ${SEVERITY_CONFIG[sev].color}30` }}
              >
                {severityCounts[sev]}
              </div>
            </div>
          ))}
          <div className="ml-auto">
            <div className="data-label">SCAN TIME</div>
            <div className="font-mono text-xs" style={{ color: 'var(--color-text-secondary)' }}>{new Date().toLocaleTimeString()}</div>
          </div>
        </div>
      </motion.div>

      {threats.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="rounded-2xl p-12 text-center"
          style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
        >
          <ShieldCheck className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--color-accent-emerald)' }} />
          <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sora)' }}>No threats detected</h2>
          <p style={{ color: 'var(--color-text-secondary)' }}>Threat surface scan was clean. Continue monitoring.</p>
        </motion.div>
      ) : (
        <div className="grid lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3 space-y-4">
            {threats.map((threat, i) => {
              const sevConfig = SEVERITY_CONFIG[threat.severity as Severity] ?? SEVERITY_CONFIG.low;
              const typeMeta = THREAT_TYPE_META[threat.threat_type] ?? { icon: AlertTriangle, label: threat.threat_type };
              const statusMeta = STATUS_META[threat.alert_status] ?? { color: '#64748B', label: threat.alert_status, pulse: false };
              const TypeIcon = typeMeta.icon;
              return (
                <motion.div
                  key={threat.jobId || i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                  className="rounded-2xl p-5 relative overflow-hidden"
                  style={{
                    backgroundColor: 'var(--color-bg-surface)',
                    border: '1px solid var(--color-border-default)',
                    borderLeft: `4px solid ${sevConfig.color}`,
                  }}
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="data-label px-2 py-0.5 rounded font-bold"
                        style={{ color: sevConfig.color, backgroundColor: sevConfig.bg, border: `1px solid ${sevConfig.color}40` }}
                      >
                        {sevConfig.label}
                      </span>
                      <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full"
                        style={{ backgroundColor: 'var(--color-bg-elevated)', border: '1px solid var(--color-border-subtle)' }}
                      >
                        <TypeIcon className="w-3 h-3" />
                        <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{typeMeta.label}</span>
                      </span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <div className="data-label">CONFIDENCE</div>
                      <div className="w-20 h-1.5 overflow-hidden rounded-full" style={{ backgroundColor: 'var(--color-bg-elevated)' }}>
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${(threat.confidence ?? 0) * 100}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className="h-full rounded-full"
                          style={{ backgroundColor: sevConfig.color }}
                        />
                      </div>
                      <span className="data-label font-mono w-8 text-right">{Math.round((threat.confidence ?? 0) * 100)}%</span>
                    </div>
                  </div>

                  <h3 className="font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>{threat.title}</h3>
                  <p className="text-sm leading-relaxed mb-4" style={{ color: 'var(--color-text-secondary)' }}>{threat.description}</p>

                  <div className="flex items-center justify-between flex-wrap gap-3 pt-3 border-t" style={{ borderColor: 'var(--color-border-subtle)' }}>
                    {threat.source_url && (
                      <a href={threat.source_url} target="_blank" rel="noopener noreferrer"
                        className="text-xs flex items-center gap-1 transition-colors"
                        style={{ color: 'var(--color-accent-primary)' }}
                      >
                        <Link2 className="w-3 h-3" />
                        {threat.source_domain || threat.source_url}
                      </a>
                    )}
                    <div className="flex items-center gap-2">
                      <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider"
                        style={{ color: statusMeta.color, backgroundColor: `${statusMeta.color}15` }}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${statusMeta.pulse ? 'animate-pulse' : ''}`}
                          style={{ backgroundColor: statusMeta.color }}
                        />
                        {statusMeta.label}
                      </span>
                      <span className="data-label font-mono flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {relativeTime(threat.detected_at)}
                      </span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          <div className="space-y-4">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="rounded-2xl p-4"
              style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
            >
              <div className="data-label mb-3">THREAT BREAKDOWN</div>
              <div className="space-y-2">
                {Object.entries(typeCounts).map(([type, count]) => {
                  const meta = THREAT_TYPE_META[type] ?? { icon: AlertTriangle, label: type };
                  const TypeIcon = meta.icon;
                  const pct = (count / threats.length) * 100;
                  return (
                    <div key={type}>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                          <TypeIcon className="w-3 h-3" />
                          {meta.label}
                        </div>
                        <span className="data-label font-mono">{count}</span>
                      </div>
                      <div className="h-1 overflow-hidden rounded-full" style={{ backgroundColor: 'var(--color-bg-elevated)' }}>
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ duration: 0.6, ease: 'easeOut' }}
                          className="h-full rounded-full"
                          style={{ backgroundColor: 'var(--color-accent-primary)' }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="rounded-2xl p-4"
              style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
            >
              <div className="data-label mb-3">SEVERITY HISTOGRAM</div>
              <div className="flex items-end justify-between gap-2 h-24">
                {(Object.keys(SEVERITY_CONFIG) as Severity[]).map((sev) => {
                  const count = severityCounts[sev];
                  const maxCount = Math.max(...Object.values(severityCounts), 1);
                  const heightPct = (count / maxCount) * 100;
                  return (
                    <div key={sev} className="flex-1 flex flex-col items-center gap-1">
                      <div className="data-label font-mono">{count}</div>
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${Math.max(heightPct, 8)}%` }}
                        transition={{ duration: 0.6, ease: 'easeOut' }}
                        className="w-full rounded-t"
                        style={{ backgroundColor: SEVERITY_CONFIG[sev].color, minHeight: '4px' }}
                      />
                      <div className="data-label" style={{ fontSize: '9px' }}>{sev.slice(0, 3).toUpperCase()}</div>
                    </div>
                  );
                })}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="rounded-2xl p-4"
              style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
            >
              <div className="data-label mb-3">BRIGHT DATA SOURCES</div>
              <div className="space-y-2">
                {[
                  { label: 'SERP API', active: true },
                  { label: 'Web Unlocker', active: true },
                  { label: 'Residential Proxies', active: true },
                  { label: 'Browser API', active: true },
                ].map((src) => (
                  <div key={src.label} className="flex items-center gap-2 text-xs">
                    <span className={`w-1.5 h-1.5 rounded-full ${src.active ? 'bg-[var(--color-accent-emerald)] animate-pulse' : 'bg-[var(--color-accent-red)]'}`} />
                    <span style={{ color: 'var(--color-text-secondary)' }}>{src.label}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="rounded-2xl p-4"
              style={{ backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-default)' }}
            >
              <div className="data-label mb-3 flex items-center gap-2">
                <Eye className="w-3 h-3" />
                COMPLIANCE NOTES
              </div>
              <div className="space-y-2">
                {complianceNotes.map((note, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                    <CheckCircle className="w-3 h-3 shrink-0 mt-0.5" style={{ color: 'var(--color-accent-primary)' }} />
                    <span>{note}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      )}
    </div>
  );
}
