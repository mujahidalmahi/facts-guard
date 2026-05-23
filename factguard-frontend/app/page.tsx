'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const [claim, setClaim] =
    useState('');

  const [loading, setLoading] =
    useState(false);

  const router =
    useRouter();

  async function handleAnalyse() {
    if (!claim.trim())
      return;

    try {
      setLoading(true);

      const res =
        await fetch(
          'http://localhost:8000/verify',
          {
            method:
              'POST',
            headers: {
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify(
              {
                claim,
              }
            ),
          }
        );

      if (!res.ok) {
        throw new Error(
          'Failed request'
        );
      }

      const data =
        await res.json();

      localStorage.setItem(
        'factguard-result',
        JSON.stringify(
          data
        )
      );

      // NEW FLOW:
      // Go to loading screen first
      router.push(
        '/loading'
      );
    } catch (error) {
      console.error(
        error
      );

      alert(
        'Failed to analyse claim'
      );
    } finally {
      setLoading(false);
    }
  }

  const examples = [
    'The Earth is flat',
    'WHO confirmed ivermectin cures COVID-19',
    'Apple is acquiring Netflix',
  ];

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 bg-slate-50">
      <div className="max-w-3xl w-full text-center">
        <h1 className="text-6xl font-bold text-slate-900">
          FactGuard
        </h1>

        <p className="text-slate-500 mt-4 text-lg">
          AI-powered trust
          verification in
          under 60 seconds
        </p>

        <textarea
          value={claim}
          onChange={(e) =>
            setClaim(
              e.target.value
            )
          }
          placeholder="Enter a claim to verify..."
          className="w-full mt-10 h-48 rounded-2xl border border-slate-300 p-5 text-lg outline-none focus:ring-2 focus:ring-indigo-500 resize-none bg-white"
        />

        <button
          onClick={
            handleAnalyse
          }
          disabled={
            loading
          }
          className="w-full mt-6 bg-indigo-500 hover:bg-indigo-600 transition-colors text-white py-4 rounded-2xl text-lg font-semibold disabled:opacity-60"
        >
          {loading
            ? 'Analysing...'
            : 'Analyse'}
        </button>

        <div className="flex flex-wrap justify-center gap-3 mt-8">
          {examples.map(
            (
              example
            ) => (
              <button
                key={
                  example
                }
                onClick={() =>
                  setClaim(
                    example
                  )
                }
                className="px-4 py-2 rounded-full border border-slate-300 text-sm hover:bg-slate-100 transition-colors"
              >
                {example}
              </button>
            )
          )}
        </div>
      </div>
    </main>
  );
}