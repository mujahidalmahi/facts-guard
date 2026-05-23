# FactGuard Frontend

AI-powered misinformation verification dashboard. Submit a claim, poll the pipeline, and get a source-backed verdict.

## Stack

**Next.js 16** · **Tailwind CSS v4** · **TypeScript** · **Supabase JS v2** · **lucide-react**

## Setup

```bash
pnpm install
cp .env.example .env.local   # fill in your env vars
pnpm dev                     # http://localhost:3000
```

### Required env vars

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend base URL (e.g. `http://localhost:8000`) |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon/public key |

## Pages

| Route | File | What it does |
|---|---|---|
| `/` | `app/page.tsx` | Landing — claim input + numbered example list |
| `/loading?job=:id` | `app/loading/page.tsx` | Polls backend every 2 s, pulsing dot indicator, bottom progress bar |
| `/result/:jobId` | `app/result/[jobId]/page.tsx` | Verdict, agreement meter, sources, share |
| `/history` | (not yet built) | Past verifications table |

## API contract

```
POST /verify   { claim: string }          → { jobId: string }
GET  /result/:jobId  200 → VerifyResult | 202 → null (still processing)
```

The loading page polls `GET /result/:jobId` until it gets a 200, then redirects to `/result/:jobId`.

## Project structure

```
app/                          # Next.js App Router pages
  page.tsx                    # Landing
  layout.tsx                  # Root layout (Geist fonts)
  globals.css                 # Tailwind + custom animations
  loading/page.tsx            # Queue/polling
  result/[jobId]/page.tsx     # Result page
components/
  AgreementMeter.tsx          # Stacked bar with numerical breakdown
  VerdictBadge.tsx            # Verdict stamp (uppercase, tracking-widest)
  ConfidencePill.tsx          # Confidence level
  EvidenceTimeline.tsx        # Sorted source list with stance stripes
  ShareCard.tsx               # Copy link to result
  ui/                         # Reusable primitives (card, progress, etc.)
lib/
  api.ts                      # postVerify(), getResult()
  constants.ts                # EXAMPLE_CLAIMS, STATUS_MESSAGES, VERDICT_COLORS
  utils.ts                    # cn() — clsx + tailwind-merge
  supabase.ts                 # Supabase client
types/index.ts                # Verdict, Confidence, Source, VerifyResult
```

## Commands

```bash
pnpm dev       # Start dev server
pnpm build     # Type check + production build
pnpm lint      # ESLint
pnpm start     # Start production server
```

## Design

Editorial, newsroom-inspired aesthetic. The UI avoids generic SaaS patterns in favour of restrained colour, deliberate whitespace, and information density suited to fact-checking work.
