'use client';

import {
  Area, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, ComposedChart,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { GraphData } from '@/types';

function TrendIcon({ change }: { change: string }) {
  if (change?.startsWith('+')) return <TrendingUp className="size-4" style={{ color: 'var(--color-accent-emerald)' }} />;
  if (change?.startsWith('-')) return <TrendingDown className="size-4" style={{ color: 'var(--color-accent-red)' }} />;
  return <Minus className="size-4" style={{ color: 'var(--color-text-tertiary)' }} />;
}

export function PriceChart({ data }: { data: GraphData }) {

  const positive = data.change_24h?.startsWith('+');
  const lineColor = positive ? '#10B981' : '#EF4444';

  const avg = data.data.length
    ? data.data.reduce((s, d) => s + d.price, 0) / data.data.length
    : 0;

  const hasVolume = data.data.some((d) => d.volume != null);

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>{data.label}</h3>
          <p className="text-3xl font-mono font-semibold mt-1" style={{ color: lineColor }}>
            {data.unit === 'USD' ? '$' : ''}
            {data.current_price?.toLocaleString()}
            <span className="text-base ml-1" style={{ color: 'var(--color-text-tertiary)' }}>{data.unit}</span>
          </p>
        </div>
        <div className="text-right space-y-1">
          <div className="flex items-center justify-end gap-1.5">
            <TrendIcon change={data.change_24h} />
            <span className="text-sm font-medium">{data.change_24h} (24h)</span>
          </div>
          <div className="flex items-center justify-end gap-1.5">
            <TrendIcon change={data.change_7d} />
            <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>{data.change_7d} (7d)</span>
          </div>
        </div>
      </div>

      <div className="h-60 w-full min-w-0">
          <ResponsiveContainer width="100%" height={240}>
            <ComposedChart data={data.data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={lineColor} stopOpacity={0.25} />
                  <stop offset="100%" stopColor={lineColor} stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-subtle)" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11, fill: 'var(--color-text-tertiary)' }}
                tickFormatter={(v) => v.slice(5)}
              />
              <YAxis
                yAxisId="price"
                tick={{ fontSize: 11, fill: 'var(--color-text-tertiary)' }}
                domain={['auto', 'auto']}
                width={60}
              />
              {hasVolume && (
                <YAxis
                  yAxisId="volume"
                  orientation="right"
                  tick={false}
                  width={0}
                  domain={[0, 'auto']}
                />
              )}
              <Tooltip
                contentStyle={{
                  background: 'var(--color-bg-surface)',
                  border: '1px solid var(--color-border-default)',
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <ReferenceLine y={avg} stroke="var(--color-text-tertiary)" strokeDasharray="4 4" yAxisId="price" />
              {hasVolume && (
                <Bar yAxisId="volume" dataKey="volume" fill="var(--color-bg-elevated)" opacity={0.4} radius={[2, 2, 0, 0]} />
              )}
              <Area
                yAxisId="price"
                type="monotone"
                dataKey="price"
                stroke={lineColor}
                strokeWidth={2.5}
                fill="url(#priceGradient)"
                dot={false}
                activeDot={{ r: 5, fill: lineColor, strokeWidth: 2, stroke: 'var(--color-bg-surface)' }}
              />
            </ComposedChart>
          </ResponsiveContainer>
      </div>
    </div>
  );
}
