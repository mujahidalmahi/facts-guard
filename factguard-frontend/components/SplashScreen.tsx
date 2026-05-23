'use client';

import {
  useEffect,
  useState,
} from 'react';
import { motion } from 'framer-motion';

const WORD = 'FactGuard';
const CHARS =
  'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*';
const DURATION = 2000;

function randomChar(): string {
  return CHARS[
    Math.floor(
      Math.random() * CHARS.length
    )
  ];
}

function scrambleWord(
  word: string,
  charsRevealed: number
): string {
  let out = '';
  for (let i = 0; i < word.length; i++) {
    out +=
      i < charsRevealed
        ? word[i]
        : randomChar();
  }
  return out;
}

export default function SplashScreen({
  onDone,
}: {
  onDone: () => void;
}) {
  const [displayText, setDisplayText] =
    useState(() =>
      scrambleWord(WORD, 0)
    );
  const [progress, setProgress] =
    useState(0);
  const [showTagline, setShowTagline] =
    useState(false);
  const [exiting, setExiting] =
    useState(false);

  useEffect(() => {
    const stepMs = 60;
    const totalSteps = Math.ceil(
      DURATION / stepMs
    );
    let step = 0;

    const timer = setInterval(() => {
      step++;
      const p = Math.min(
        step / totalSteps,
        1
      );
      const charsRevealed = Math.floor(
        p * WORD.length
      );

      setDisplayText(
        scrambleWord(WORD, charsRevealed)
      );
      setProgress(p);

      if (p > 0.6)
        setShowTagline(true);

      if (p >= 1) {
        clearInterval(timer);
        setDisplayText(WORD);
        setProgress(1);
        setShowTagline(true);

        setTimeout(
          () => setExiting(true),
          1000
        );
      }
    }, stepMs);

    return () =>
      clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!exiting) return;
    const timer = setTimeout(
      onDone,
      800
    );
    return () =>
      clearTimeout(timer);
  }, [exiting, onDone]);

  return (
    <motion.div
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center"
      style={{ background: '#0f172a' }}
      animate={
        exiting
          ? {
              opacity: 0,
              y: '-100%',
            }
          : {
              opacity: 1,
              y: 0,
            }
      }
      transition={{
        duration: 0.8,
        ease: 'easeInOut',
      }}
    >
      <div className="flex flex-col items-center -mt-16">
        {/* Two-layer text */}
        <div className="relative flex items-center justify-center min-h-[1.3em] mb-2">
          <div
            className="absolute pointer-events-none select-none whitespace-nowrap"
            style={{
              fontSize:
                'clamp(5rem, 16vw, 10rem)',
              fontWeight: 800,
              letterSpacing: '0.04em',
              WebkitTextStroke:
                '2px rgba(241,245,249,0.25)',
              WebkitTextFillColor:
                'transparent',
              color: 'transparent',
              transform:
                'translateY(-0.15em)',
            }}
          >
            FactGuard
          </div>
          <h1
            suppressHydrationWarning
            className="relative z-10"
            style={{
              fontSize:
                'clamp(3rem, 8vw, 5.5rem)',
              fontWeight: 800,
              letterSpacing: '0.04em',
              color: '#f1f5f9',
              minHeight: '1.2em',
            }}
          >
            {displayText}
          </h1>
        </div>

        {/* Loading bar */}
        <div
          style={{
            width: 280,
            maxWidth: '70vw',
            height: 4,
            background: '#1e293b',
            borderRadius: 4,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${progress * 100}%`,
              borderRadius: 4,
              background: '#6366f1',
              transition:
                'width 0.1s linear',
            }}
          />
        </div>
      </div>

      {/* Tagline */}
      <p
        className="absolute"
        style={{
          bottom: '3rem',
          fontSize:
            'clamp(1rem, 2.5vw, 1.5rem)',
          color: '#94a3b8',
          opacity: showTagline ? 1 : 0,
          transition:
            'opacity 0.6s ease',
        }}
      >
        AI-powered trust verification
      </p>
    </motion.div>
  );
}
