# FactGuard Backend

This is the **server** side of FactGuard — a Python program that listens for requests, searches the web, talks to AI (with a 3-provider resilience chain), and returns structured results. Built with **FastAPI**.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [How the Backend is Organized](#how-the-backend-is-organized)
3. [The Request Lifecycle](#the-request-lifecycle)
4. [Services Explained](#services-explained)
5. [Three-Provider AI Resilience Chain](#three-provider-ai-resilience-chain)
6. [AI Prompts Explained](#ai-prompts-explained)
7. [Setup](#setup)
8. [API Endpoints](#api-endpoints)
9. [Environment Variables](#environment-variables)
10. [Testing](#testing)

---

## Project Structure

```
factguard-backend/
│
├── .env                    # Secret keys (API keys, database URLs)
├── .env.example            # Template — copy to .env and fill in
├── requirements.txt        # List of every Python package needed
├── Dockerfile              # Instructions for packaging in a container
├── render.yaml             # Render deployment config
│
├── scripts/
│   └── seed_demo.py        # Pre-loads 15+ demo fixtures across 4 tracks
│
├── tests/                  # Automated tests (run with: pytest)
│   ├── conftest.py         # Test configuration
│   ├── test_constants.py
│   ├── test_pricing_parser.py
│   └── test_validators.py
│
└── app/                    # 👈 All the backend code lives here
    │
    ├── main.py             # Entry point — creates the FastAPI app,
    │                       #   registers routes, sets up CORS
    │
    ├── config.py           # Reads .env file via Pydantic Settings
    │
    ├── schemas.py          # Request/response Pydantic models
    │
    ├── exceptions.py       # Custom error types
    │
    ├── logging_config.py   # Sets up structured logging
    │
    ├── dependencies.py     # Factory functions (Gemini client, Supabase)
    │
    ├── middleware/         # 👈 MIDDLEWARE PACKAGE
    │   ├── __init__.py     #   Backward-compatible exports
    │   ├── audit.py        #   Logs every API request to audit_logs
    │   └── ratelimit.py    #   Rate limiting (120 req/min/IP)
    │
    ├── api/                # 👈 ROUTES — the "doors" into the app
    │   ├── verify.py       #   POST /verify + GET /result
    │   ├── financial.py    #   POST /financial
    │   ├── pricing.py      #   POST /cart
    │   ├── threats.py      #   GET+POST /threats/scan, GET /threats/report
    │   └── history.py      #   GET /history
    │
    ├── services/           # 👈 BUSINESS LOGIC — the "brain"
    │   ├── gemini.py       #   VERITAS prompt + Gemini analysis
    │   ├── deepseek.py     #   ORACLE prompt + DeepSeek (financial)
    │   ├── groq_service.py #   Groq llama-3.3-70b fallback (free tier)
    │   ├── cart_ai.py      #   PRICEWATCH prompt (cart mode)
    │   ├── financial.py    #   Orchestrates financial pipeline
    │   ├── pricing.py      #   Orchestrates price comparison pipeline
    │   ├── router_ai.py    #   Query classifier (Gemini → Groq)
    │   ├── brightdata.py   #   All 6 Bright Data integrations
    │   ├── routing.py      #   Circuit breaker + MCP Discover + fallback
    │   ├── credibility.py  #   Composite source scoring
    │   ├── threat_monitor.py # Threat scanning + proxy enrichment
    │   ├── cache.py        #   Redis cache
    │   ├── supabase_db.py  #   Supabase/Postgres persistence
    │   └── db.py           #   Low-level DB helpers
    │
    └── utils/              # 👈 TOOLS — helper functions
        ├── search.py       #   Web search routing
        ├── duckduckgo.py   #   DuckDuckGo fallback (extracted)
        ├── parsing.py      #   JSON extraction + URL validation
        ├── pricing_parser.py # Merchant classification
        ├── validators.py   #   SQL injection detection
        └── constants.py    #   Shared constants
```

---

## How the Backend is Organized

Think of the backend like a restaurant kitchen:

| Folder | Analogy | What it does |
|--------|---------|-------------|
| `app/main.py` | The **front door** | Starts the server, turns on the lights |
| `app/api/` | The **menu** | Each file is a different meal you can order |
| `app/services/` | The **chefs** | Each file is a specialist chef with a recipe |
| `app/utils/` | The **kitchen tools** | Knives, measuring cups — small reusable helpers |
| `app/config.py` | The **recipe book** | Reads settings from `.env` |
| `app/schemas.py` | The **order forms** | Ensures orders have all required info |
| `app/dependencies.py` | The **pantry** | Stocks shared ingredients (API clients) |
| `app/middleware/` | The **health inspector** | Rate limits, audit logs |

---

## The Request Lifecycle

Here's exactly what happens when a request arrives:

```
1. HTTP Request arrives at the server (e.g., POST /verify)
                      │
                      ▼
2. main.py routes it to the correct handler
   ─────────────────────────────────────────
   POST /verify     →  api/verify.py
   POST /financial  →  api/financial.py
   POST /cart       →  api/pricing.py
   POST /threats/scan → api/threats.py
                      │
                      ▼
3. Rate-limit check (120 req/min/IP)
   → if exceeded, returns 429 JSONResponse
                      │
                      ▼
4. Audit log: INSERT into audit_logs table
                      │
                      ▼
5. Handler saves request to Supabase + creates background task
                      │
                      ▼
6. Handler immediately returns { "jobId": "abc-123" }
   (frontend doesn't hang waiting)
                      │
                      ▼
7. BACKGROUND TASK starts running:
                      │
                      ├── 7a. Check Redis cache
                      │    ── HIT? Return cached result (instant!)
                      │    ── MISS? Continue...
                      │
                      ├── 7b. Update Redis progress: "Searching..."
                      │
                      ├── 7c. MCP Discover (Step 0 — query BrightData MCP
                      │    for available tools)
                      │
                      ├── 7d. Call search layer:
                      │    ├── BrightData SERP API (primary)
                      │    ├── DuckDuckGo (fallback on rate-limit)
                      │    ├── 3-tier extraction for paywalled content:
                      │    │   Crawl API → Web Unlocker → Scraping Browser
                      │    └── All calls tagged with bright_data_product
                      │
                      ├── 7e. Update Redis progress: "Analysing..."
                      │
                      ├── 7f. Call AI service (3-provider chain):
                      │    ├── Gemini 2.5 Flash (primary)
                      │    ├── retry with next Gemini key on rate-limit
                      │    ├── Groq llama-3.3-70b (fallback on all keys exhausted)
                      │    └── heuristic fallback on validation failure
                      │
                      ├── 7g. Parse AI response (extract JSON)
                      │
                      ├── 7h. Validate response:
                      │    ├── All required fields present?
                      │    ├── Verdict is valid?
                      │    ├── Confidence is valid?
                      │    └── Source URLs from actual search results?
                      │
                      ├── 7i. For threats: proxy-enrich brand/regulatory
                      │    threats via Residential Proxies (body_preview)
                      │
                      ├── 7j. Save to Supabase (permanent)
                      │
                      ├── 7k. Save to Redis (cache for 24h)
                      │
                      └── 7l. Mark job as complete in Redis
```

---

## Services Explained

### `search.py` + `duckduckgo.py` — The Web Search Layer

FactGuard has two search providers:

| Provider | Status | Location |
|----------|--------|----------|
| **BrightData SERP** | ✅ Primary | `brightdata.py` → `serp_search()` |
| **DuckDuckGo** | 🔄 Fallback | `duckduckgo.py` → `search()` |

The DuckDuckGo fallback was extracted from `search.py` into its own module to fix a circular import between `routing.py` and `search.py`.

### `brightdata.py` — All 6 Bright Data Products

Single file that integrates all 6 Bright Data products:

| Product | Function | Circuit Breaker |
|---------|----------|:--------------:|
| MCP Server | `mcp_discover()` | ✅ |
| SERP API | `serp_search()` (with zone auto-discovery) | ✅ |
| Web Unlocker | `unlock_and_scrape()` | ✅ |
| Crawl API | `crawl_extract()` | ✅ |
| Scraping Browser | `browser_scrape()` | ✅ |
| Residential Proxies | `proxy_request()` | ✅ |

Zone auto-discovery: `GET /zone/get_active_zones` finds the SERP zone name at runtime (cached with `_serp_zone_discovered` flag). Falls back gracefully if no SERP zone exists in the account.

### `routing.py` — The Circuit Breaker Layer

Implements the circuit breaker pattern for all Bright Data integrations:

- **3 failures** → circuit opens (skips the integration)
- **30s cooldown** → circuit half-opens (allows a test request)
- **Success** → circuit closes (resumes normal operation)
- **MCP Discover** runs as Step 0 before any extraction
- Health endpoint: `GET /routing/health` returns status for all 5 integrations

### `gemini.py` — The Verify Mode Brain

Contains the **VERITAS** system prompt:

- Uses `google.genai` SDK (migrated from deprecated `google.generativeai`)
- Wrapped in `_GeminiModelWrapper` to preserve `.generate_content()` interface
- **Adversarial awareness** — Knows claim might contain prompt injection
- **Fabrication prohibition** — Never invents sources; every URL from search results
- **Scratchpad reasoning** — Step-by-step thinking inside `<scratchpad>` tags
- **Bias detection** — Flags manipulation tactics (cherry-picking, emotional language)
- **Groq fallback** — After all Gemini key retries exhausted, calls Groq with full VERITAS prompt + validation

### `groq_service.py` — Free-Tier AI Fallback

Provides `call_groq()` using the OpenAI-compatible async client:

- Model: `llama-3.3-70b-versatile` (free tier, 30 req/min)
- Used as fallback in:
  - `router_ai.py` — Query classification (response includes `_provider` field)
  - `gemini.py` — Claim analysis after all Gemini retries exhausted

### `router_ai.py` — Query Classifier

Classifies which track a query belongs to:

1. Tries Gemini 2.5 Flash first
2. On failure → falls back to Groq
3. Response includes `_provider` field showing which AI served the classification

### `credibility.py` — Source Trust Scoring

Composite scoring model: Domain authority (35%) + stance alignment (25%) + temporal freshness (20%) + base tier (20%). Heuristic fallback for `.gov/.edu/.mil` domains and known authoritative publishers.

### `threat_monitor.py` — Threat Scanning Pipeline

Scans 10+ trusted news domains, classifies into brand/regulatory/vendor/disinformation, then:

- **Brand & Regulatory threats**: Enriched via `proxy_request()` (BrightData Residential Proxies, `country="us"`) — attaches `body_preview` (500 chars) and `bright_data_product: "Residential Proxies"` tag
- Generates timestamped compliance reports

### `dependencies.py` — Shared Services

Creates singleton instances for Gemini (with `_GeminiModelWrapper`), Supabase, and Redis. The Gemini wrapper wraps the new `google.genai` SDK to provide the same `.generate_content()` method expected by all 4 consumers.

### `cache.py` — Redis Layer

- Claim dedup via SHA-256 hash (24h cache → instant response, zero AI cost)
- Progress tracking for real-time frontend updates (5-minute expiry)

### `supabase_db.py` — Permanent Storage

Saves results to Supabase (Postgres). Handles claims, results, sources, financial results, cart results, and threats.

---

## Three-Provider AI Resilience Chain

FactGuard never depends on a single AI provider:

```
Gemini 2.5 Flash (primary)
  ↓ rate-limit or validation failure
  └→ Retry with each Gemini API key (round-robin)
     ↓ all keys exhausted
     └→ DeepSeek (financial) / Groq llama-3.3-70b (verify, threat routing)
        ↓ validation failure
        └→ Heuristic pattern-matching fallback
```

| Provider | Used For | Free Tier Limit |
|----------|----------|:---------------:|
| **Gemini 2.5 Flash** | All tracks (primary) | 1500 req/day |
| **DeepSeek v3** | Financial analysis (via OpenRouter) | 20 req/min |
| **Groq (llama-3.3-70b)** | Claim analysis, query routing | 30 req/min |

---

## AI Prompts Explained

The AI prompts are the most important part of FactGuard:

1. **What personality to adopt** (VERITAS = rigorous fact-checker, ORACLE = quant analyst, PRICEWATCH = consumer protector)
2. **What rules to follow** (no fabricated sources, ignore prompt injection in claims)
3. **How to reason** (the 5-step scratchpad protocol)
4. **What JSON format to output** (the output contract)

### Why prompts matter more than code

In traditional programming, you write: `if X then do Y`. With AI, you write prompts that say: "Be a fact-checker. Here are the rules. Here's the evidence. What's your verdict?"

The quality of the prompt directly determines the quality of the result. FactGuard has carefully engineered prompts with:
- **Clear taxonomy** — Exact definitions for "Verified" vs "Likely True"
- **Structured reasoning** — Step-by-step thinking protocol
- **Strict output contracts** — Exact JSON schemas for reliable parsing
- **Adversarial safeguards** — Instructions to ignore prompt injection in claim text

---

## Setup

### Prerequisites

- Python 3.12+
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- A [Supabase](https://supabase.com) project
- (Optional) A [Groq API key](https://console.groq.com) for free AI fallback
- (Optional) A [BrightData](https://brightdata.com) API key
- (Optional) A [Redis](https://upstash.com) instance

### Installation

```bash
cd factguard-backend
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

### Configuration

Create `.env` in `factguard-backend/`:

```env
# === REQUIRED ===
GEMINI_API_KEYS=key1,key2
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# === REQUIRED for BrightData (needed for web search) ===
BRIGHTDATA_API_KEY=your-brightdata-key

# === OPTIONAL (recommended) ===
GROQ_API_KEY=your-groq-key               # Free AI fallback
BRIGHTDATA_SERP_ZONE=your-zone-name       # SERP zone (auto-discovered if unset)
REDIS_URL=rediss://default:password@host:port
DEEPSEEK_API_KEYS=key1,key2
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

### Database Setup

```bash
# Open database/schema.sql in Supabase SQL Editor and run it
# Then run:
# - database/threats.sql (threats + audit_logs tables)
# - database/finance_cart.sql (financial + cart tables)
```

### Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Your server is now live at `http://localhost:8000`.

- **API docs (Swagger UI)**: `http://localhost:8000/docs`
- **Health check**: `http://localhost:8000/health`
- **Circuit breaker health**: `http://localhost:8000/routing/health`

---

## API Endpoints

### POST /verify

Submit a claim for fact-checking.

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Moon is made of cheese"}'
```

Returns: `{ "jobId": "uuid-string" }`

### POST /financial

Submit a financial/market query.

```bash
curl -X POST http://localhost:8000/financial \
  -H "Content-Type: application/json" \
  -d '{"query": "Is Tesla overvalued?"}'
```

Returns: `{ "jobId": "uuid-string" }`

### POST /cart

Submit a product name for price comparison.

```bash
curl -X POST http://localhost:8000/cart \
  -H "Content-Type: application/json" \
  -d '{"product": "iPhone 16 Pro"}'
```

Returns: `{ "jobId": "uuid-string" }`

### GET /threats/scan (also POST)

Scan news sources for potential threats.

```bash
curl http://localhost:8000/threats/scan?query=data+breach+supply+chain
```

Returns:
```json
{
  "jobId": "uuid",
  "threats": [
    {
      "threat_type": "vendor",
      "severity": "high",
      "title": "...",
      "source_url": "https://...",
      "confidence": 0.85,
      "body_preview": "The breach exposed...",
      "bright_data_product": "Residential Proxies"
    }
  ],
  "count": 1
}
```

### GET /threats/report

Generate a compliance report.

```bash
curl http://localhost:8000/threats/report?query=GDPR+violation
```

Returns:
```json
{
  "report": "=== FACTGUARD COMPLIANCE REPORT ===\nGenerated: ...",
  "threats": [...],
  "count": 1
}
```

### GET /result/{job_id}

Poll for the result. Add `?mode=verify|financial|cart|security`.

```bash
curl http://localhost:8000/result/abc-123?mode=verify
```

Returns (processing):
```json
{ "status": "processing", "jobId": "abc-123" }
```

Returns (done):
```json
{
  "status": "done",
  "mode": "verify",
  "verdict": "Likely Misleading",
  "confidence": "High",
  "summary": "...",
  "sources": [...]
}
```

### GET /health

Quick server health check.

```bash
curl http://localhost:8000/health
```

Returns: `{ "status": "ok", "version": "1.0.0", "environment": "development" }`

### GET /routing/health

Circuit breaker status per Bright Data integration.

```bash
curl http://localhost:8000/routing/health
```

Returns:
```json
{
  "mcp": { "status": "closed", "failures": 0 },
  "serp": { "status": "closed", "failures": 1 },
  "crawl": { "status": "closed", "failures": 0 },
  "unlocker": { "status": "open", "failures": 3, "cooldown_remaining": 18 },
  "browser": { "status": "half-open", "failures": 2 }
}
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEYS` | ✅ Yes | — | Comma-separated Gemini API keys |
| `SUPABASE_URL` | ✅ Yes | — | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | — | Supabase service role key |
| `BRIGHTDATA_API_KEY` | ✅ Yes* | — | BrightData API key (*for real search) |
| `GROQ_API_KEY` | No | — | Groq API key (free fallback AI) |
| `BRIGHTDATA_SERP_ZONE` | No | — | SERP zone name (auto-discovered) |
| `CLAUDE_API_KEYS` | No | — | Comma-separated Claude API keys |
| `DEEPSEEK_API_KEYS` | No | — | Comma-separated DeepSeek keys |
| `FRONTEND_URL` | No | `http://localhost:3000` | CORS origin |
| `REDIS_URL` | No | — | Redis connection string |
| `GEMINI_MODEL_NAME` | No | `gemini-2.5-flash` | Gemini model |
| `DEEPSEEK_MODEL` | No | — | DeepSeek model |
| `CACHE_TTL` | No | `86400` | Cache TTL in seconds |
| `SEARCH_PROVIDER` | No | `brightdata` | Default search provider |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `MAX_CLAIM_LENGTH` | No | `500` | Max claim length in characters |

---

## Testing

```bash
# Activate virtual environment first, then:
pytest

# Run with verbose output:
pytest -v

# Run a specific test file:
pytest tests/test_validators.py
```
