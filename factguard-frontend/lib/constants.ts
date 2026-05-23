export const EXAMPLE_CLAIMS = [
  'WHO confirmed that ivermectin cures COVID-19.',
  'Apple is planning to acquire Netflix in Q3 2026.',
  'The 2024 US election was decided by mail-in ballot fraud.',
] as const;

export const STATUS_MESSAGES = [
  'Searching trusted sources...',
  'Reading 4 articles...',
  'Analysing evidence...',
  'Generating verdict...',
] as const;

export const VERDICT_COLORS: Record<string, string> = {
  Verified: 'bg-emerald-700 text-white',
  'Likely True': 'bg-teal-700 text-white',
  'Mixed Evidence': 'bg-amber-600 text-white',
  'Likely Misleading': 'bg-orange-700 text-white',
  Unverified: 'bg-slate-600 text-white',
};