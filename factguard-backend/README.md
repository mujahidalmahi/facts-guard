# FactGuard Backend

This is the **server** side of FactGuard — a Python program that listens for requests, searches the web, talks to AI, and returns structured results. It's built with **FastAPI**, a modern Python web framework.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [How the Backend is Organized](#how-the-backend-is-organized)
3. [The Request Lifecycle (What happens when you click Submit)](#the-request-lifecycle)
4. [Services Explained](#services-explained)
5. [AI Prompts Explained](#ai-prompts-explained)
6. [Setup](#setup)
7. [API Endpoints](#api-endpoints)
8. [Environment Variables](#environment-variables)
9. [Testing](#testing)

---

## Project Structure

```
factguard-backend/
│
├── .env                    # Secret keys (API keys, database URLs)
├── .env.example            # Template — copy to .env and fill in
├── requirements.txt        # List of every Python package needed
├── Dockerfile              # Instructions for packaging in a container
│
├── scripts/
│   └── seed_demo.py        # Pre-loads demo claims into Redis for testing
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
    ├── config.py           # Reads .env file and makes values available
    │                       #   as Python objects (using Pydantic Settings)
    │
    ├── schemas.py          # Defines request/response data shapes
    │                       #   (e.g., "a verify request must have a 'claim' field")
    │
    ├── exceptions.py       # Custom error types (e.g., "ClaimTooLongError")
    │
    ├── middleware.py        # Global error handling — catches crashes
    │                       #   and returns friendly error messages
    │
    ├── logging_config.py   # Sets up logging (prints to console)
    │
    ├── dependencies.py     # Factory functions that create shared services
    │                       #   (Gemini client, Supabase client)
    │
    ├── api/                # 👈 ROUTES — the "doors" into the app
    │   ├── verify.py       #   POST /verify — submit a claim
    │   ├── financial.py    #   POST /financial — market query
    │   ├── pricing.py      #   POST /cart — product price check
    │   └── history.py      #   GET /history — past results
    │
    ├── services/           # 👈 BUSINESS LOGIC — the "brain"
    │   ├── gemini.py       #   Gemini AI prompt + response parsing (verify mode)
    │   ├── deepseek.py     #   DeepSeek AI prompt + response (financial mode)
    │   ├── cart_ai.py      #   Gemini AI prompt + response (cart mode)
    │   ├── financial.py    #   Orchestrates full financial analysis pipeline
    │   ├── pricing.py      #   Orchestrates full price comparison pipeline
    │   ├── router_ai.py    #   Classifies which mode a query belongs to
    │   ├── cache.py        #   Redis cache — fast storage for results + progress
    │   ├── supabase_db.py  #   Supabase/Postgres — permanent storage
    │   └── credibility.py  #   Rates how trustworthy a source is
    │
    └── utils/              # 👈 TOOLS — helper functions
        ├── search.py       #   Web search: BrightData (primary) → DuckDuckGo (fallback)
        ├── parsing.py      #   Extracts clean JSON from AI responses
        ├── pricing_parser.py  # Extracts prices from search snippets
        ├── validators.py   #   Detects malicious input (SQL injection)
        └── constants.py    #   Shared constants (verdicts, stances, etc.)
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

---

## The Request Lifecycle

Here's exactly what happens when a request arrives:

```
1. HTTP Request arrives at the server (e.g., POST /verify)
                      │
                      ▼
2. main.py routes it to the correct handler
   ─────────────────────────────────────────
   POST /verify  →  api/verify.py
   POST /financial → api/financial.py
   POST /cart    →  api/pricing.py
                      │
                      ▼
3. The handler saves the request to Supabase (database)
   and creates a background task
                      │
                      ▼
4. The handler immediately returns { "jobId": "abc-123" }
   (so the frontend doesn't hang waiting)
                      │
                      ▼
5. BACKGROUND TASK starts running:
                      │
                      ├── 5a. Check Redis cache
                      │    ── HIT? Return cached result (instant!)
                      │    ── MISS? Continue...
                      │
                      ├── 5b. Update Redis progress: "Searching..."
                      │
                      ├── 5c. Call search.py → BrightData SERP API
                      │    Returns: list of { title, url, snippet }
                      │
                      ├── 5d. Update Redis progress: "Analysing..."
                      │
                      ├── 5e. Call AI service:
                      │    ├── verify mode  → gemini.py (VERITAS prompt)
                      │    ├── financial    → deepseek.py (ORACLE prompt)
                      │    └── cart mode    → cart_ai.py (PRICEWATCH prompt)
                      │
                      ├── 5f. Parse AI response (extract JSON)
                      │
                      ├── 5g. Validate response:
                      │    ├── All required fields present?
                      │    ├── Verdict is one of the valid values?
                      │    ├── Confidence is valid?
                      │    └── Source URLs are from the search results?
                      │
                      ├── 5h. Save to Supabase (permanent storage)
                      │
                      ├── 5i. Save to Redis (cache for 24 hours)
                      │
                      └── 5j. Mark job as complete in Redis
```

---

## Services Explained

### `search.py` — The Web Search Layer

This file finds evidence on the internet. It has two search providers:

| Provider | Status | How it works |
|----------|--------|-------------|
| **BrightData** | ✅ Primary | Calls BrightData's SERP API with Bearer token auth. Returns real Google-quality results |
| **DuckDuckGo** | 🔄 Fallback | Used when BrightData API key is missing or the API call fails |

**Key functions:**
- `_brightdata_search(query, max_results)` — Calls BrightData SERP API, parses organic results
- `brightdata_scrape_product(product_url)` — Uses BrightData Web Unlocker to scrape e-commerce pages
- `_duckduckgo_search(query, max_results)` — DuckDuckGo fallback
- `search_claim(claim, max_results)` — Main async function, called by all three modes

### `gemini.py` — The Verify Mode Brain

This file contains the **VERITAS** system prompt — the instructions that tell Gemini how to be a fact-checker. Key components:

- **`VERIFY_SYSTEM_PROMPT`** — The "personality" and rules for the AI: how to reason, what verdicts to use, what JSON to output
- **`VERIFY_USER_PROMPT`** — Template that wraps the search results and claim into a message for the AI
- **`build_search_context()`** — Formats search results into a readable text block
- **`_validate_response()`** — Checks the AI's output has all required fields
- **`analyze_claim()`** — Main function: searches web, calls Gemini, validates, returns result

Key prompt design features:
- **Adversarial awareness** — The AI knows the claim text might contain prompt injection attacks
- **Fabrication prohibition** — The AI must never invent sources; every URL must come from search results
- **Scratchpad reasoning** — Before outputting JSON, the AI must think step-by-step inside `<scratchpad>` tags
- **Narrative framing** — The AI identifies how the claim is framed (alarmist, minimising, selective, etc.)
- **Bias detection** — The AI flags manipulation tactics like cherry-picking, emotional language, etc.

### `deepseek.py` — The Financial Mode Brain

Contains the **ORACLE** system prompt for market analysis. Unlike the verify prompt which focuses on truth/falsehood, this prompt focuses on:

- **Price context** — Current price vs 7d, 30d, 52w trends
- **Catalyst scan** — What events could move the price?
- **Risk matrix** — Top 3 specific risks
- **Scenario planning** — Bull/base/bear 30-day predictions with probability weights

### `cart_ai.py` — The Cart Mode Brain

Contains the **PRICEWATCH** system prompt for consumer protection. Key features:

- **Trust framework** — GREEN (verified) / YELLOW (unverified) / RED (risky)
- **Deal quality scoring** — Each listing gets a score from 0-100
- **Counterfeit risk detection** — Flags listings that look fake
- **Market price intelligence** — Determines the fair price range for any product

### `cache.py` — The Redis Layer

Redis is a fast in-memory database. This service uses it for two things:

| Feature | How it works | Benefit |
|---------|-------------|---------|
| **Claim dedup** | Computes a SHA-256 hash of the claim text, stores result for 24h | Same claim twice → instant response, zero AI cost |
| **Progress tracking** | Stores current progress message with 5-minute expiry | Frontend can show "Searching... Analysing..." in real-time |

### `supabase_db.py` — The Permanent Storage

Saves results to Supabase (Postgres) so they persist even if Redis restarts. Handles creating records for claims, results, sources, financial results, and cart results.

---

## AI Prompts Explained

The AI prompts are the most important part of FactGuard. They are the instructions that tell the AI:

1. **What personality to adopt** (VERITAS = rigorous fact-checker, ORACLE = quant analyst, PRICEWATCH = consumer protector)
2. **What rules to follow** (no fabricated sources, ignore prompt injection in claims)
3. **How to reason** (the 5-step scratchpad protocol)
4. **What JSON format to output** (the output contract)

### Why prompts matter more than code

In traditional programming, you write code that says: `if X then do Y`. With AI, you write prompts that say: "Be a fact-checker. Here are the rules. Here's the evidence. What's your verdict?"

The quality of the prompt directly determines the quality of the result. That's why FactGuard has carefully engineered prompts with:
- **Clear taxonomy** — Exact definitions for what "Verified" vs "Likely True" means
- **Structured reasoning** — Step-by-step thinking protocol to prevent the AI from jumping to conclusions
- **Strict output contracts** — Exact JSON schemas so the backend can parse the response reliably
- **Adversarial safeguards** — Instructions to ignore prompt injection attempts in the claim text

---

## Setup

### Prerequisites

- Python 3.12+
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- A [Supabase](https://supabase.com) project
- (Optional) A [BrightData](https://brightdata.com) API key
- (Optional) A [Redis](https://upstash.com) instance

### Installation

```bash
# Navigate to backend
cd factguard-backend

# Create virtual environment (isolates packages from other Python projects)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
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

# === OPTIONAL ===
REDIS_URL=rediss://default:password@host:port
DEEPSEEK_API_KEYS=key1,key2
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

### Database Setup

```bash
# Open database/schema.sql in Supabase SQL Editor and run it
# Or if you have psql installed:
psql $SUPABASE_CONNECTION_STRING -f ../database/schema.sql
```

### Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Your server is now live at `http://localhost:8000`.

- **API docs (Swagger UI)**: `http://localhost:8000/docs`
- **Health check**: `http://localhost:8000/health`

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

### GET /result/{job_id}

Poll for the result. Add `?mode=verify|financial|cart`.

```bash
curl http://localhost:8000/result/abc-123?mode=verify
```

Returns (while processing):
```json
{ "status": "processing", "jobId": "abc-123" }
```

Returns (when done):
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

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEYS` | ✅ Yes | — | Comma-separated Gemini API keys (rotation on rate-limit) |
| `SUPABASE_URL` | ✅ Yes | — | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | — | Supabase service role (admin) key |
| `BRIGHTDATA_API_KEY` | ✅ Yes* | — | BrightData API key (*required for real search) |
| `DEEPSEEK_API_KEYS` | No | — | Comma-separated DeepSeek/OpenRouter keys |
| `FRONTEND_URL` | No | `http://localhost:3000` | Allowed CORS origin |
| `REDIS_URL` | No | — | Redis connection string |
| `GEMINI_MODEL_NAME` | No | `gemini-2.5-flash` | Gemini model identifier |
| `DEEPSEEK_MODEL` | No | — | DeepSeek model identifier |
| `CACHE_TTL` | No | `86400` | Cache time-to-live in seconds |
| `SEARCH_PROVIDER` | No | `brightdata` | Default search provider |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_CLAIM_LENGTH` | No | `500` | Maximum claim length in characters |

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
