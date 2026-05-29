# Tech Stack & Build System

## Backend (`factguard-backend/`)

- **Language**: Python 3.12
- **Framework**: FastAPI 0.115 with Uvicorn 0.29
- **AI Providers**: Google Gemini 2.5 Flash (primary), DeepSeek via OpenRouter (financial fallback), Groq llama-3.3-70b (free-tier fallback)
- **Data scraping**: Bright Data (MCP, SERP API, Web Unlocker, Crawl API, Scraping Browser, Residential Proxies), DuckDuckGo (`ddgs`) as free fallback
- **Database**: Supabase (Postgres) via `supabase-py`
- **Cache**: Redis (Upstash) via `redis` 5.x
- **Validation**: Pydantic v2 with `pydantic-settings`
- **HTTP client**: `httpx` (async)
- **Browser automation**: Playwright
- **Financial data**: `yfinance`
- **Linting/formatting**: Ruff, Black (line length 100, target Python 3.11+)
- **Testing**: pytest with `asyncio_mode = auto`

## Frontend (`factguard-frontend/`)

- **Framework**: Next.js 16 (standalone output mode)
- **Language**: TypeScript 5
- **UI library**: React 19
- **Styling**: Tailwind CSS v4 with PostCSS
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **Charts**: Recharts
- **Package manager**: pnpm
- **Linting**: ESLint 9 with `eslint-config-next`

## Infrastructure

- **Containerization**: Docker + Docker Compose (backend on port 8000, frontend on port 3000)
- **Backend deployment**: Render (`render.yaml`)
- **Frontend deployment**: Vercel (`vercel.json`)
- **CI**: GitHub Actions (`.github/workflows/ci.yml`)

## Common Commands

### Backend

```bash
# Setup
cd factguard-backend
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate      # Mac/Linux
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload --port 8000

# Run tests
cd factguard-backend
pytest

# Run tests (single execution, no watch)
pytest --tb=short

# Lint
ruff check app/
ruff format app/

# Seed demo data
python scripts/seed_demo.py
```

### Frontend

```bash
# Setup
cd factguard-frontend
pnpm install

# Dev server (run manually in terminal)
pnpm dev

# Build
pnpm build

# Type check
pnpm typecheck

# Lint
pnpm lint
```

### Docker (full stack)

```bash
# Start both services
docker compose up --build

# Backend only
docker compose up backend
```

## Environment Variables

### Backend (`.env`)

| Variable | Required | Description |
|----------|:--------:|-------------|
| `GEMINI_API_KEYS` | ✅ | Comma-separated Gemini API keys (round-robin) |
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase admin key |
| `BRIGHTDATA_API_KEY` | ✅ | Bright Data API key |
| `GROQ_API_KEY` | — | Groq API key (free fallback) |
| `BRIGHTDATA_SERP_ZONE` | — | SERP zone name (auto-discovered if unset) |
| `DEEPSEEK_API_KEYS` | — | OpenRouter/DeepSeek keys |
| `REDIS_URL` | — | Redis connection string |
| `FRONTEND_URL` | — | CORS allowed origin (default: `http://localhost:3000`) |
| `GEMINI_MODEL_NAME` | — | Gemini model (default: `gemini-2.5-flash`) |
| `CACHE_TTL` | — | Cache TTL in seconds (default: `86400`) |

### Frontend (`.env.local`)

| Variable | Required | Description |
|----------|:--------:|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend URL (e.g. `http://localhost:8000`) |
