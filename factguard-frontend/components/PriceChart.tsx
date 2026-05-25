'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

import {
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';

import type { GraphData } from '@/types';

function TrendIcon({
  change,
}: {
  change: string;
}) {
  if (change?.startsWith('+')) {
    return (
      <TrendingUp className='size-4 text-emerald-500' />
    );
  }

  if (change?.startsWith('-')) {
    return (
      <TrendingDown className='size-4 text-red-500' />
    );
  }

  return (
    <Minus className='size-4 text-slate-400' />
  );
}

export function PriceChart({
  data,
}: {
  data: GraphData;
}) {
  const positive =
    data.change_24h?.startsWith('+');

  const lineColor = positive
    ? '#10b981'
    : '#ef4444';

  const avg = data.data.length
    ? data.data.reduce(
        (s, d) => s + d.price,
        0
      ) / data.data.length
    : 0;

  return (
    <div
      className='rounded-2xl border
      border-[var(--card-border)]
      bg-[var(--card)] p-5 space-y-4'
    >
      <div className='flex items-start justify-between'>
        <div>
          <h3 className='text-lg font-bold text-[var(--foreground)]'>
            {data.label}
          </h3>

          <p
            className='text-3xl font-mono
            font-semibold mt-1'
            style={{
              color: lineColor,
            }}
          >
            {data.unit === 'USD'
              ? '$'
              : ''}

            {data.current_price?.toLocaleString()}

            <span className='text-base ml-1 text-[var(--muted-foreground)]'>
              {data.unit}
            </span>
          </p>
        </div>

        <div className='text-right space-y-1'>
          <div className='flex items-center justify-end gap-1.5'>
            <TrendIcon
              change={data.change_24h}
            />

            <span className='text-sm font-medium'>
              {data.change_24h} (24h)
            </span>
          </div>

          <div className='flex items-center justify-end gap-1.5'>
            <TrendIcon
              change={data.change_7d}
            />

            <span className='text-sm text-[var(--muted-foreground)]'>
              {data.change_7d} (7d)
            </span>
          </div>
        </div>
      </div>

      <div className='h-52'>
        <ResponsiveContainer
          width='100%'
          height='100%'
        >
          <LineChart
            data={data.data}
            margin={{
              top: 4,
              right: 4,
              bottom: 0,
              left: 0,
            }}
          >
            <CartesianGrid
              strokeDasharray='3 3'
              stroke='var(--card-border)'
            />

            <XAxis
              dataKey='date'
              tick={{
                fontSize: 11,
                fill:
                  'var(--muted-foreground)',
              }}
              tickFormatter={(v) =>
                v.slice(5)
              }
            />

            <YAxis
              tick={{
                fontSize: 11,
                fill:
                  'var(--muted-foreground)',
              }}
              domain={[
                'auto',
                'auto',
              ]}
              width={60}
            />

            <Tooltip
              contentStyle={{
                background:
                  'var(--card)',
                border:
                  '1px solid var(--card-border)',
                borderRadius: 8,
                fontSize: 12,
              }}
            />

            <ReferenceLine
              y={avg}
              stroke='var(--muted-foreground)'
              strokeDasharray='4 4'
            />

            <Line
              type='monotone'
              dataKey='price'
              stroke={lineColor}
              strokeWidth={2.5}
              dot={false}
              activeDot={{
                r: 4,
                fill: lineColor,
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}