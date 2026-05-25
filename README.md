# FactGuard

AI-powered misinformation detection, market intelligence, and price comparison. Submit a claim, financial query, or product — FactGuard gathers live evidence and returns a source-backed verdict.

## Architecture

```
news-guard/
├── factguard-backend/           # Python FastAPI server
│   ├── app/
│   │   ├── api/
│   │   │   ├── verify.py        # POST /verify, GET /result/{id}
│   │   │   ├── financial.py     # POST /financial, GET /financial-result/{id}
│   │   │   ├── pricing.py       # POST /cart, GET /cart-result/{id}
│   │   │   └── history.py       # GET /history
│   │   ├── services/
│   │   │   ├── gemini.py        # Gemini 2.5 Flash prompt + parsing
│   │   │   ├── deepseek.py      # DeepSeek fallback provider
│   │   │   ├── cache.py         # Redis claim dedup + progress tracking
│   │   │   ├── supabase_db.py   # Supabase persistence layer
│   │   │   ├── financial.py     # Financial analysis logic
│   │   │   └── pricing.py       # Cart/pricing analysis logic
│   │   ├── config.py            # Pydantic Settings (env vars)
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── exceptions.py        # Custom exception hierarchy
│   │   ├── middleware.py        # Error handlers
│   │   └── utils/
│   │       ├── search.py        # Web search (BrightData/DuckDuckGo)
│   │       ├── parsing.py       # AI JSON response parser
│   │       ├── pricing_parser.py
│   │       ├── validators.py    # SQL injection pattern detection
│   │       └── constants.py     # Shared constants
│   ├── scripts/
│   │   └── seed_demo.py         # Pre-seed Redis with demo fixtures
│   └── requirements.txt
├── factguard-frontend/          # Next.js 16 + Tailwind v4 + TypeScript
│   ├── app/
│   │   ├── page.tsx             # Splash screen + mode switcher + input
│   │   ├── loading/page.tsx     # Polling with real-time progress
│   │   ├── history/page.tsx     # Verification history
│   │   └── result/[jobId]/
│   │       ├── page.tsx         # Unified result view (verify/financial/cart)
│   │       ├── layout.tsx       # OG image metadata
│   │       ├── og-image/route.tsx  # Edge OG image generation
│   │       ├── FinancialResultView.tsx
│   │       └── CartResultView.tsx
│   ├── components/              # UI components
│   │   ├── ConfidencePill.tsx
│   │   ├── VerdictBadge.tsx
│   │   ├── SignalBadge.tsx
│   │   ├── AgreementMeter.tsx
│   │   ├── EvidenceTimeline.tsx
│   │   ├── PriceChart.tsx
│   │   ├── CartProductCard.tsx
│   │   ├── ResultErrorBoundary.tsx
│   │   ├── ModeSwitcher.tsx
│   │   ├── ShareCard.tsx
│   │   ├── Skeleton.tsx
│   │   └── ...
│   └── types/index.ts           # TypeScript type definitions
└── database/
    └── schema.sql               # Supabase Postgres schema
```

## Stack

| Layer | Technology |
|-------|-----------|
| API | Python 3.12, FastAPI 0.115, Uvicorn |
| AI | Google Gemini 2.5 Flash, DeepSeek (fallback) |
| Search | BrightData (primary), DuckDuckGo (fallback) |
| Database | Supabase (Postgres) |
| Cache | Redis (Upstash) — claim dedup + progress tracking |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind v4 |
| UI | Framer Motion, Lucide icons |

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- pnpm
- A Supabase project (free tier)
- Google Gemini API key(s) — [get one here](https://aistudio.google.com/apikey)
- Redis URL (Upstash or local) — app works without it

### Backend

```bash
cd factguard-backend
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

Create `.env` in `factguard-backend/.env`:

```
GEMINI_API_KEYS=key1,key2
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
REDIS_URL=rediss://default:password@host:port  # optional
FRONTEND_URL=http://localhost:3000
```

Optional: pre-seed Redis with demo fixtures:

```bash
python scripts/seed_demo.py
```

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

### Database

Run `database/schema.sql` in your Supabase SQL Editor. Safe to re-run.

### Frontend

```bash
cd factguard-frontend
pnpm install
```

Create `.env.local` in `factguard-frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run:

```bash
pnpm dev     # http://localhost:3000
```

## API

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/verify` | Submit a claim → returns `{ jobId }` |
| `POST` | `/financial` | Submit a financial query → returns `{ jobId }` |
| `POST` | `/cart` | Submit a product for price comparison → returns `{ jobId }` |
| `GET` | `/result/{job_id}?mode=verify\|financial\|cart` | Poll for result |
| `GET` | `/financial-result/{job_id}` | Legacy financial result endpoint |
| `GET` | `/history` | Recent claims from cache (includes mode + display_text) |
| `GET` | `/health` | Health check with version + environment |

### Response shape

All modes return via `GET /result/{job_id}?mode=...`:

```json
{
  "status": "done",
  "jobId": "uuid",
  "mode": "verify",
  "claim": "The Earth is flat",
  "verdict": "Likely Misleading",
  "confidence": "High",
  "summary": "Overwhelming scientific evidence...",
  "supports": 0,
  "contradicts": 4,
  "neutral": 1,
  "sources": [
    {
      "title": "Wikipedia: Earth",
      "url": "https://en.wikipedia.org/...",
      "stance": "contradicts",
      "credibility": "High",
      "relevance": 10,
      "summary": "...",
      "quote": "..."
    }
  ]
}
```

Financial mode also includes `graph_data` and `analysis` (signal, price_trend, risk_level, key_factors, prediction_30d). Cart mode includes `listings` and `analysis` (best_deal, price_range, warnings, recommendation).

### Processing response

While analysis is running:

```json
{
  "status": "processing",
  "jobId": "uuid"
}
```

## Data Flow

```
User submits input
  → POST /{mode} → backend creates Supabase record + spawns BackgroundTask
  → Frontend polls GET /result/{job_id}?mode={mode} every 1.5s
  → Backend checks Redis cache by job_id:
      HIT  → return cached raw_json immediately
      MISS → query Supabase results table raw_json column
              → return full payload with status: 'done'
  → If claim status is 'error' → return { status: 'error' }
  → Otherwise → return { status: 'processing' }
```

## Modes

| Mode | Input | What it does |
|------|-------|-------------|
| **Verify** | A claim statement | Searches the web, gathers evidence, returns verdict + sources |
| **Financial** | A market query (e.g. "Bitcoin price") | Fetches price data, returns analysis + chart + sources |
| **Cart** | A product name | Compares prices across retailers, returns best deal + warnings |

## Verdicts

| Verdict | Meaning |
|---------|---------|
| Verified | Strong evidence supports the claim |
| Likely True | Mostly supported with minor caveats |
| Mixed Evidence | Roughly equal supporting and contradicting evidence |
| Likely Misleading | Mostly contradicted by evidence |
| Unverified | Could not find sufficient evidence to evaluate |

## Environment Variables

### Backend (`factguard-backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEYS` | Yes | — | Comma-separated Gemini API keys |
| `SUPABASE_URL` | Yes | — | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | — | Supabase service role key |
| `REDIS_URL` | No | — | Redis connection string |
| `FRONTEND_URL` | No | `http://localhost:3000` | CORS origin |
| `GEMINI_MODEL_NAME` | No | `gemini-2.5-flash` | Gemini model |
| `CACHE_TTL` | No | `86400` | Claim cache TTL (seconds) |
| `DEEPSEEK_API_KEY` | No | — | DeepSeek fallback API key |
| `BRIGHTDATA_API_KEY` | No | — | BrightData search API key |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

### Frontend (`factguard-frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend URL (e.g. `http://localhost:8000`) |

## Key Design Decisions

- **Multi-mode architecture**: Single `GET /result/{job_id}?mode=` endpoint serves verify, financial, and cart results — frontend routes to the appropriate view component
- **Async + polling**: Background `BackgroundTasks` with frontend polling preserves UX without WebSockets
- **Redis dual use**: Claim dedup cache (24h TTL) + ephemeral progress tracking (300s TTL); also caches `raw_json` by `job_id`
- **Repeated claims skip Gemini**: Redis cache hit returns immediately — zero API cost
- **Key rotation**: Multiple Gemini API keys — rotates on 429/500/503, retries with 1s delay
- **Graceful degradation**: If Redis or a search provider is unavailable, the app falls back gracefully
- **OG images**: Edge-rendered Open Graph images for social sharing of results
- **WCAG compliant**: All interactive elements meet 48px minimum touch target
