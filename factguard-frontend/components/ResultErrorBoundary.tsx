'use client';
import { Component, ReactNode } from 'react';

interface Props { children: ReactNode; fallback?: ReactNode; }
interface State { hasError: boolean; error?: Error; }

export class ResultErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] text-center px-6 space-y-4">
          <p className="text-5xl"> </p>
          <h2 className="text-xl font-bold text-[var(--foreground)]">
            Analysis Incomplete
          </h2>
          <p className="text-sm text-[var(--muted-foreground)] max-w-sm">
            The AI returned an unexpected response. This can happen with
            complex financial queries. Please try again.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 rounded-full bg-[var(--accent)] text-white text-sm font-semibold"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
