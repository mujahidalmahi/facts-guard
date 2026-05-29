'use client';

import { useMemo } from 'react';
import { Source } from '@/types';

interface Node {
  id: string;
  label: string;
  stance: string;
  tier: number;
  radius: number;
  x: number;
  y: number;
}

export default function SourceGraph({ sources }: { sources: Source[] }) {
  const nodes: Node[] = useMemo(() => {
    if (!sources.length) return [];
    const cx = 180, cy = 120;
    const angleStep = (2 * Math.PI) / sources.length;
    return sources.map((s, i) => {
      const tier = s.tier ?? 4;
      const radius = 22 - (tier - 1) * 4;
      return {
        id: s.url,
        label: s.title,
        stance: s.stance,
        tier,
        radius: Math.max(radius, 8),
        x: cx + 90 * Math.cos(angleStep * i - Math.PI / 2),
        y: cy + 90 * Math.sin(angleStep * i - Math.PI / 2),
      };
    });
  }, [sources]);

  if (!nodes.length) return null;

  const getColor = (stance: string) => {
    switch (stance) {
      case 'supports': return '#10B981';
      case 'contradicts': return '#EF4444';
      default: return '#64748B';
    }
  };

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 backdrop-blur-md">
      <h3 className="text-xs font-mono uppercase tracking-widest text-slate-400 mb-3">
        Source Credibility Network
      </h3>
      <svg viewBox="0 0 360 240" className="w-full h-auto max-h-64">
        <defs>
          {nodes.map(n => (
            <radialGradient key={n.id} id={`glow-${n.id.replace(/[^a-zA-Z0-9]/g, '')}`}>
              <stop offset="0%" stopColor={getColor(n.stance)} stopOpacity="0.3" />
              <stop offset="100%" stopColor={getColor(n.stance)} stopOpacity="0" />
            </radialGradient>
          ))}
        </defs>
        {nodes.map((n, i) => (
          <g key={n.id}>
            <circle
              cx={n.x}
              cy={n.y}
              r={n.radius + 12}
              fill={`url(#glow-${n.id.replace(/[^a-zA-Z0-9]/g, '')})`}
            />
            <circle
              cx={n.x}
              cy={n.y}
              r={n.radius}
              fill={getColor(n.stance)}
              fillOpacity="0.85"
              stroke={getColor(n.stance)}
              strokeWidth="2"
              strokeOpacity="0.6"
            />
            <text
              x={n.x}
              y={n.y + n.radius + 14}
              textAnchor="middle"
              fill="#94A3B8"
              fontSize="9"
              fontFamily="monospace"
              className="select-none"
            >
              T{n.tier}
            </text>
          </g>
        ))}
      </svg>
      <div className="flex gap-4 mt-2 text-xs text-slate-500 justify-center">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> Supports
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500 inline-block" /> Contradicts
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-slate-500 inline-block" /> Neutral
        </span>
      </div>
    </div>
  );
}
