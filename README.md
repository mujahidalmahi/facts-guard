# FactGuard

AI-powered misinformation detection. Submit a claim — FactGuard gathers live web evidence via DuckDuckGo and analyzes it with Google Gemini 2.5 Flash to return a source-backed verdict.

## Architecture

```
news-guard/
├── factguard-backend/        # Python FastAPI server
│   └── app/
│       ├── api/verify.py     # POST /verify, GET /result/{id}
│       ├── api/history.py    # GET /history
│       ├── services/
│       │   ├── gemini.py     # Gemini 2.5 Flash + web search grounding
│       │   ├── cache.py      # Redis claim dedup + progress tracking
│       │   └── supabase_db.py
│       ├── config.py         # Pydantic Settings (env vars)
│       ├── dependencies.py   # GeminiService, SupabaseService (DI)
│       ├── schemas.py        # Pydantic request/response models
│       ├── exceptions.py     # Custom exception hierarchy
│       └── utils/
│           ├── search.py     # DuckDuckGo web search (ddgs)
│           └── validators.py # SQL injection pattern detection
├── factguard-frontend/       # Next.js 16 + Tailwind v4 + TypeScript
│   ├── app/
│   │   ├── page.tsx          # Splash screen + claim input
│   │   ├── loading/page.tsx  # Polling with real-time progress
│   │   └── result/[jobId]/   # Verdict, sources, download/share
│   ├── components/           # UI components
│   └── types/                # TypeScript type definitions
└── database/
    └── schema.sql            # Supabase Postgres schema
```

## Stack

| Layer | Technology |
|-------|-----------|
| API | Python 3.12, FastAPI 0.115, Uvicorn |
| AI | Google Gemini 2.5 Flash (`google-generativeai`) |
| Search | DuckDuckGo (`ddgs`) — free, no API key |
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
- Redis URL (Upstash or local) — optional, app works without it

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
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

Run:

```bash
pnpm dev     # http://localhost:3000
```

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/verify` | Submit a claim → returns `{ jobId }` |
| `GET` | `/result/{job_id}` | Poll for result (returns progress or full verdict) |
| `GET` | `/history` | Recent verifications from cache |
| `GET` | `/health` | Health check with version + environment |

### POST /verify

```json
{ "claim": "The Earth is flat" }
```

Returns immediately:

```json
{ "jobId": "uuid-here" }
```

Poll `GET /result/{job_id}` — while processing:

```json
{ "status": "processing", "jobId": "...", "progress": "Searching DuckDuckGo..." }
```

When complete:

```json
{
  "status": "done",
  "jobId": "...",
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
      "url": "https://en.wikipedia.org/wiki/Earth",
      "stance": "contradicts",
      "relevance": 10,
      "summary": "Comprehensive article on Earth's shape",
      "quote": "Earth is an oblate spheroid"
    }
  ]
}
```

## Data Flow

```
User submits claim
  → POST /verify → backend creates Supabase record + spawns async task
  → Frontend polls GET /result/{job_id} every 1.5s
  → Backend checks Redis cache for claim hash:
      HIT  → return cached result immediately (zero Gemini cost)
      MISS → search DuckDuckGo → inject results into Gemini prompt
             → validate response structure → save to Supabase → cache in Redis
  → Frontend receives "done" status → redirects to result page
```

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
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

### Frontend (`factguard-frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend URL (e.g. `http://localhost:8000`) |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anon key |

## Key Design Decisions

- **Async + polling**: Background `asyncio.create_task` with frontend polling preserves the existing UX without WebSockets
- **Redis dual use**: Claim dedup cache (24h TTL) + ephemeral progress tracking (300s TTL)
- **Repeated claims skip Gemini**: Redis cache hit returns immediately — zero API cost
- **DuckDuckGo every time**: Search runs even for cached claims (search results change); only Gemini call is cached
- **Key rotation**: Multiple Gemini API keys — rotates on 429/500/503, retries with 1s delay
- **No fallback caching**: Failed analyses (`_is_fallback`) are never cached — the user can always retry
- **Graceful degradation**: If Redis or DuckDuckGo is unavailable, the app falls back gracefully
