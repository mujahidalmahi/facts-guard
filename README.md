# FactGuard — Enterprise Intelligence Platform

FactGuard is a **multi-track AI platform** that verifies claims, analyzes markets, monitors threats, and compares prices — powered by the full Bright Data ecosystem and a three-provider free AI resilience chain: **Gemini → DeepSeek → Groq + heuristic fallback**.

- **Verify Track (GTM Intelligence)** — Fact-check competitor claims, pricing intel, hiring signals
- **Financial Track (Finance & Risk)** — Verify earnings claims, M&A rumors, compliance alerts
- **Security Track (Security & Compliance)** — Monitor brand threats (with proxy enrichment), regulatory changes, data breaches
- **Cart Track** — Trust-scored price comparisons across retailers

Every answer comes with **live web evidence**, **source citations**, and **probabilistic credibility scoring**.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Four Tracks Explained](#four-tracks-explained)
3. [Bright Data Integration (6 Products)](#bright-data-integration-6-products)
4. [Intelligent Routing Layer](#intelligent-routing-layer)
5. [Three-Provider AI Resilience Chain](#three-provider-ai-resilience-chain)
6. [Advanced Credibility Engine](#advanced-credibility-engine)
7. [Threat Monitoring Pipeline](#threat-monitoring-pipeline)
8. [Tech Stack](#tech-stack)
9. [Project Structure](#project-structure)
10. [Setup Guide](#setup-guide)
11. [API Documentation](#api-documentation)
12. [Environment Variables](#environment-variables)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 16)                        │
│  ModeSwitcher: Verify · Financial · Security · Cart                  │
│  Nav: Bright Data circuit-breaker health dots (5 colored circles)    │
│  Components: VerdictBadge · ConfidencePill · AgreementMeter ·       │
│              EvidenceTimeline · SourceGraph · ThreatResultView       │
│              CartProductCard · PriceComparisonTable                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTP (REST)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                            │
│  /verify · /financial · /threats/scan · /cart · /history           │
│  /health · /routing/health                                          │
│  Middleware: RateLimit (120 req/min) · AuditLog · CORS              │
└──────────┬──────────┬──────────┬──────────┬─────────────────────────┘
           │          │          │          │
           ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ROUTING LAYER (Circuit Breaker)                    │
│                                                                      │
│  Step 0: BrightData MCP Discover (tool orchestration)                │
│  SERP Search:    BrightData SERP ──fallback──► DuckDuckGo (free)     │
│  Content Extract: Crawl API ──► Web Unlocker ──► Scraping Browser    │
│                                                                      │
│  Each integration has its own circuit breaker (3 failures → open     │
│  → 30s cooldown → auto-reset). Health: /routing/health              │
└─────────────────────────────────────────────────────────────────────┘
           │          │          │          │
           ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────────┐
│               AI ANALYSIS ENGINES (3-Provider Chain)                  │
│  Gemini 2.5 Flash (primary — all tracks)                             │
│    ↓ on rate-limit / validation failure                              │
│  DeepSeek (financial fallback via OpenRouter)                        │
│    ↓ on validation failure                                           │
│  Groq (llama-3.3-70b, free tier — claim analysis + query routing)   │
│    ↓                                                               │
│  Heuristic fallback (pattern-matching when all AI providers fail)    │
└─────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE & CACHE                                │
│  Supabase (Postgres): claims · results · sources · threats ·         │
│                       audit_logs · financial_results · cart_results   │
│  Redis (Upstash):     claim cache (24h) · progress tracking ·        │
│                       rate-limit counters · history                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Four Tracks Explained

### 1. Verify Track (GTM Intelligence)

**Use when:** You hear a competitor claim, see a suspicious headline, or need to verify market intelligence.

**What happens:**
1. Claim submitted → MCP Discover runs as Step 0 (tool orchestration discovery)
2. Source discovery via BrightData SERP API (falls back to DuckDuckGo)
3. Gemini analyzes with 5-step VERITAS reasoning protocol
4. On Gemini failure → retries with next API key → falls back to Groq llama-3.3-70b
5. Returns: verdict, confidence, narrative frame, bias signals, source diversity, evidence timeline

**Demo scenario:** *"Our competitor just raised Series C at $100M valuation."* → FactGuard verifies via Crunchbase, LinkedIn, press releases with credibility scoring.

### 2. Financial Track (Finance & Risk)

**Use when:** You want to verify earnings claims, M&A rumors, or analyze market trends.

**What happens:**
1. Query submitted → BrightData SERP searches news + yFinance fetches charts
2. 3-tier content extraction for paywalled analyst reports (Crawl → Unlocker → Browser)
3. All services tagged with `bright_data_product` field (e.g. `"Web Unlocker"`, `"Crawl API"`)
4. DeepSeek/Gemini returns: signal, 30-day prediction, risk catalysts

**Demo scenario:** *"A major cloud provider is entering at 40% cheaper."* → Cross-references pricing blog posts, analyst reports, earnings calls via Web Unlocker.

### 3. Security Track (Security & Compliance)

**Use when:** You need to monitor brand threats, regulatory changes, vendor risks, or disinformation campaigns.

**What happens:**
1. Scan triggered → BrightData SERP searches across 10+ trusted news domains
2. Keyword-based classification into: brand / regulatory / vendor / disinformation
3. Brand & regulatory threats get proxy enrichment: `proxy_request()` via BrightData Residential Proxies (`country="us"`), adding `body_preview` (500 chars) and `bright_data_product: "Residential Proxies"`
4. Severity scoring (low → critical) with confidence percentage
5. Threat list returned with source URLs, descriptions, severity bars
6. Compliance report generated — downloadable via **Download Report** button (`.txt`)

**Demo scenario:** *"A data breach affecting a key vendor has been reported."* → Crawls vendor security pages, checks regulatory databases via Residential Proxies, generates compliance alert.

**API endpoints:** `GET /threats/scan?query=...` · `GET /threats/report`

### 4. Cart Track (Price Comparison)

**Use when:** You're shopping and want the best deal with trust scoring.

**What happens:**
1. Product search → BrightData SERP scrapes major retailers
2. Web Unlocker bypasses paywalled/locked listing pages (tagged `bright_data_product: "Web Unlocker"`)
3. Gemini scores each listing with trust framework (GREEN/YELLOW/RED)
4. Returns: best deal, counterfeit risk, market average, recommendation

---

## Bright Data Integration (6 Products)

All 6 Bright Data products are integrated and demonstrably used in the demo. Every API call is tagged with the source product name:

| Product | Purpose | FactGuard Role | Circuit Breaker |
|---------|---------|----------------|:---:|
| **MCP Server** | 30 AI-native tools | Step 0 — Discover available tools before extraction | ✅ |
| **SERP API** | Real-time search results, organic rankings | Source discovery — find trusted coverage of claims | ✅ |
| **Web Unlocker** | Bypass bot detection, CAPTCHAs, JS rendering, paywalls | Access premium sources (NYT, WSJ, FT paywalls) | ✅ |
| **Crawl API** | Structured data extraction, metadata, sitemaps | Extract article structure, author, publish date, corrections | ✅ |
| **Scraping Browser** | Full browser automation for JS-heavy pages | Fallback for dynamic content; click & verify buttons | ✅ |
| **Residential Proxies** | 150M+ residential IPs, 195 countries, geo-targeting | Threat enrichment — proxy-enrich brand/regulatory threats | ✅ |

All integrations live in `app/services/brightdata.py`. Each has its own circuit breaker in `app/services/routing.py`.

---

## Intelligent Routing Layer

The routing layer implements a **circuit breaker pattern** with tiered fallbacks:

### MCP Discover — Step 0

Before any extraction, `mcp_discover()` queries the BrightData MCP Server for available tools. All discovered operations carry the tag `bright_data_product: "MCP Server — Discover"`.

### Content Extraction Pipeline — Three-Tier Fallback

| Tier | Method | Condition |
|:----:|--------|-----------|
| 1 | BrightData Crawl API (structured extraction) | Success — full metadata, title, author, date |
| 2 | Web Unlocker + scrape | Crawl API rate-limited or timeout |
| 3 | Scraping Browser (JS rendering) | JS-heavy pages; fallback from tiers 1 & 2 |

### Source Discovery — Dual SERP Strategy

| Source | Priority |
|--------|:--------:|
| BrightData SERP | Primary — real-time Google rankings (zone auto-discovered) |
| DuckDuckGo (free) | Fallback if BrightData rate-limited |

### Circuit Breaker Behaviour
- Each integration tracks failures independently
- 3 failures → circuit **opens** (skips that tier)
- 30-second cooldown → circuit **half-opens** (allows test request)
- Success → circuit **closes** (normal operation resumes)
- Monitor at `GET /routing/health` — frontend Nav shows green/red dots for each product

---

## Three-Provider AI Resilience Chain

FactGuard never depends on a single AI provider. Every analysis request follows this chain:

```
Gemini 2.5 Flash (primary)
  ↓ rate-limit or validation failure
  └→ Retry with each Gemini API key (round-robin)
     ↓ all keys exhausted
     └→ DeepSeek (financial) or Groq (verify/threat routing)
        ↓ validation failure
        └→ Heuristic pattern-matching fallback
```

| Provider | Used For | Free Tier Limit |
|----------|----------|:---------------:|
| **Gemini 2.5 Flash** | All tracks (primary) | 1500 req/day (free) |
| **DeepSeek v3** | Financial analysis (via OpenRouter) | 20 req/min (free) |
| **Groq (llama-3.3-70b)** | Claim analysis, query routing | 30 req/min (free) |

The Groq service (`app/services/groq_service.py`) provides `call_groq()` using an OpenAI-compatible async client with `llama-3.3-70b-versatile`. It serves as fallback in:
- `router_ai.py` — Query classification (Gemini → Groq, response includes `_provider` field)
- `gemini.py` — Claim analysis via VERITAS prompt after all Gemini key retries exhausted

---

## Advanced Credibility Engine

`app/services/credibility.py` uses a **composite scoring model**:

| Factor | Weight | Source |
|--------|:-----:|--------|
| Domain Authority | 35% | BrightData domain audit + static heuristic (.gov→1.0, blogs→0.2) |
| Stance Alignment | 25% | Gemini/Groq sentiment analysis |
| Temporal Freshness | 20% | publish_date metadata (recent = higher) |
| Base Tier | 20% | Gemini credibility tier (High/Medium/Low) |

**Heuristic fallback:** `.gov/.edu/.mil` → High · Reuters/BBC/NYT → High · Blogspot/Reddit → Low

---

## Threat Monitoring Pipeline

`app/services/threat_monitor.py` scans news sources for:

| Category | Keywords Monitored | Proxy Enrichment |
|----------|-------------------|:----------------:|
| **Brand Threat** | breach, vulnerability, ransomware, data leak, recall, lawsuit | ✅ Residential Proxies |
| **Regulatory** | compliance, fine, SEC, GDPR, CCPA, sanctions | ✅ Residential Proxies |
| **Vendor Risk** | insolvency, bankruptcy, layoff, credit downgrade | ❌ |
| **Disinformation** | misinformation, deepfake, coordinated, bot network | ❌ |

Brand and regulatory threats are automatically enriched by fetching the source article body via BrightData Residential Proxies (`proxy_request(country="us")`) and attaching a `body_preview` (first 500 chars) with the `bright_data_product: "Residential Proxies"` tag.

Output: Threat objects with `severity` (low/medium/high/critical), `confidence` (0-1), and `alert_status`.

---

## Tech Stack

### Backend
| Technology | Why |
|------------|-----|
| **Python 3.12** | Easy to read, huge AI/ML library ecosystem |
| **FastAPI 0.115** | Modern Python web framework — fast, automatic API docs |
| **Uvicorn** | Python server that handles many concurrent users |
| **Google Gemini 2.5 Flash** | Primary AI — fast, cheap, great at reasoning |
| **DeepSeek (via OpenRouter)** | Backup AI for financial analysis |
| **Groq (llama-3.3-70b)** | Free-tier fallback for claim analysis + query routing |
| **BrightData (6 products)** | MCP · SERP · Unlocker · Crawl · Browser · Proxies |
| **Supabase** | Postgres database — stores all results permanently |
| **Redis (Upstash)** | Fast in-memory cache — avoids re-processing |
| **Sentry** | Error tracking (free tier) |

### Frontend
| Technology | Why |
|------------|-----|
| **Next.js 16** | React framework — routing, building, server rendering |
| **React 19** | Library for building user interfaces |
| **TypeScript** | JavaScript with types — catches bugs early |
| **Tailwind CSS v4** | Fast, consistent styling |
| **Framer Motion** | Smooth animations |
| **Lucide React** | Open-source icons |

---

## Project Structure

```
news-guard/
│
├── database/                          # SQL schema files
│   ├── schema.sql                     # Core tables (claims, results, sources)
│   ├── schema2.sql                    # Migration
│   ├── finance_cart.sql               # Financial + cart tables
│   ├── market.sql                     # Market data tables
│   └── threats.sql                    # Threats + audit_logs tables
│
├── factguard-backend/                 # THE SERVER (Python)
│   ├── .env.example                   # Environment variable template
│   ├── requirements.txt               # Python packages
│   ├── Dockerfile                     # Container build
│   ├── render.yaml                    # Render deployment config
│   │
│   ├── app/
│   │   ├── main.py                    # Entry point — wires routes, middleware, CORS
│   │   ├── config.py                  # Reads .env into typed Python objects
│   │   ├── schemas.py                 # Request/response Pydantic models
│   │   ├── exceptions.py              # Custom error types
│   │   ├── logging_config.py          # Structured logging
│   │   ├── dependencies.py            # Gemini + Supabase service singletons
│   │   │
│   │   ├── middleware/                # Middleware package
│   │   │   ├── __init__.py            # Backward-compatible exports
│   │   │   ├── audit.py               # Audit logging middleware
│   │   │   └── ratelimit.py           # Rate limiting (120 req/min/IP)
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── verify.py              # POST /verify, GET /result
│   │   │   ├── financial.py           # POST /financial
│   │   │   ├── pricing.py             # POST /cart
│   │   │   ├── threats.py             # GET+POST /threats/scan, GET /threats/report
│   │   │   └── history.py             # GET /history
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── gemini.py              # VERITAS AI prompt + analysis
│   │   │   ├── deepseek.py            # DeepSeek financial analysis
│   │   │   ├── groq_service.py        # Groq (llama-3.3-70b) fallback
│   │   │   ├── cart_ai.py             # PRICEWATCH AI prompt
│   │   │   ├── financial.py           # Orchestrates financial analysis
│   │   │   ├── pricing.py             # Orchestrates price comparison
│   │   │   ├── router_ai.py           # Query classifier (Gemini → Groq)
│   │   │   ├── brightdata.py          # All 6 Bright Data integrations
│   │   │   ├── routing.py             # Circuit breaker + MCP Discover + 3-tier fallback
│   │   │   ├── credibility.py         # Composite source credibility scoring
│   │   │   ├── threat_monitor.py      # Threat scanning + proxy enrichment
│   │   │   ├── cache.py               # Redis operations
│   │   │   ├── supabase_db.py         # Supabase persistence
│   │   │   └── db.py                  # Low-level DB helpers
│   │   │
│   │   └── utils/
│   │       ├── search.py              # Web search routing
│   │       ├── duckduckgo.py          # DuckDuckGo fallback (extracted)
│   │       ├── parsing.py             # JSON extraction + URL validation
│   │       ├── pricing_parser.py      # Merchant classification
│   │       ├── validators.py          # SQL injection detection
│   │       └── constants.py           # Shared constants
│   │
│   ├── scripts/
│   │   └── seed_demo.py               # 15+ fixtures across 4 tracks
│   └── tests/
│       ├── conftest.py
│       ├── test_constants.py
│       ├── test_pricing_parser.py
│       └── test_validators.py
│
├── factguard-frontend/                # THE BROWSER APP (TypeScript)
│   ├── .env.example
│   ├── package.json
│   ├── Dockerfile
│   ├── vercel.json                    # Vercel deployment config
│   │
│   ├── app/
│   │   ├── layout.tsx                 # Root layout — Nav, footer, fonts
│   │   ├── globals.css                # Global styles
│   │   ├── page.tsx                   # Home — 4-mode switcher + input
│   │   ├── loading/page.tsx           # Animated loading with progress
│   │   ├── price-loading/page.tsx     # Legacy
│   │   ├── history/page.tsx           # Past results
│   │   └── result/[jobId]/
│   │       ├── page.tsx               # Unified result page
│   │       ├── layout.tsx             # OG image metadata
│   │       ├── FinancialResultView.tsx
│   │       ├── CartResultView.tsx
│   │       └── ThreatResultView.tsx   # Security track + compliance report download
│   │
│   ├── components/
│   │   ├── Nav.tsx                    # Health dots (MCP/SERP/Crawl/Unlock/Browser)
│   │   ├── ModeSwitcher.tsx           # 4-mode toggle (Verify/Financial/Security/Cart)
│   │   ├── VerdictBadge.tsx
│   │   ├── ConfidencePill.tsx
│   │   ├── AgreementMeter.tsx
│   │   ├── EvidenceTimeline.tsx
│   │   ├── SourceGraph.tsx
│   │   ├── BiasHeatmap.tsx
│   │   ├── ThreatResultView.tsx       # Security track results
│   │   ├── ... (22+ components)
│   │   └── ui/                        # Base UI components
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── progress.tsx
│   │       └── separator.tsx
│   │
│   ├── lib/                           # Shared utilities
│   │   ├── constants.ts
│   │   ├── utils.ts
│   │   └── useJobPolling.ts           # React hook — polls backend every 1.5s
│   │
│   ├── types/                         # TypeScript definitions
│   │   └── index.ts                   # ThreatResult, TrackType, etc.
│   │
│   └── public/                        # Static assets
│
├── docker-compose.yml                 # One-command local setup
├── splash-demo.html                   # Standalone demo page
└── README.md                          # This file!
```

---

## Setup Guide

### Prerequisites

- Python 3.12+
- Node.js 20+
- pnpm (latest)
- Supabase account (free)
- Google AI Studio key (free)
- Groq API key (free) — [console.groq.com](https://console.groq.com)
- BrightData account (hackathon — free credits)

### Step 1: Clone & Install Backend

```bash
cd factguard-backend
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `factguard-backend/.env`:

```env
GEMINI_API_KEYS=your-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-key
BRIGHTDATA_API_KEY=your-brightdata-key
GROQ_API_KEY=your-groq-key          # Free fallback AI
BRIGHTDATA_SERP_ZONE=your-zone       # SERP zone name from BrightData dashboard
REDIS_URL=rediss://default:password@host:port
```

### Step 3: Set Up Database

1. Go to [Supabase Dashboard](https://supabase.com) → SQL Editor
2. Run `database/schema.sql` (core tables)
3. Run `database/threats.sql` (threat monitoring + audit_logs tables)
4. Run `database/finance_cart.sql` (financial + cart tables)

### Step 4: Seed Demo Data

```bash
python scripts/seed_demo.py   # Seeds 15+ fixtures across all 4 tracks
```

### Step 5: Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`

### Step 6: Install & Start Frontend

```bash
cd factguard-frontend
pnpm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
pnpm dev
```

Open `http://localhost:3000`

---

## API Documentation

### All Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/verify` | Submit a claim to fact-check |
| `POST` | `/financial` | Submit a financial/market query |
| `GET` `/POST` | `/threats/scan` | Scan news for threats (`?query=...`) |
| `GET` | `/threats/report` | Generate compliance report |
| `POST` | `/cart` | Submit product name for price comparison |
| `GET` | `/result/{job_id}?mode=verify\|financial\|cart\|security` | Poll for result |
| `GET` | `/history` | Get recent results |
| `GET` | `/health` | Server health |
| `GET` | `/routing/health` | Circuit breaker status per integration |

### Full Verify Response

```json
{
  "status": "done",
  "jobId": "abc-123",
  "claim": "Is the Earth flat?",
  "verdict": "Likely Misleading",
  "confidence": "High",
  "narrative_frame": "Uses a false dichotomy to dismiss scientific consensus.",
  "summary": "Overwhelming evidence from NASA, NOAA confirms Earth is an oblate spheroid.",
  "supports": 0,
  "contradicts": 5,
  "neutral": 1,
  "bias_signals": ["cherry_picking", "false_equivalence"],
  "source_diversity": "High",
  "sources": [
    {
      "title": "NASA: Earth Fact Sheet",
      "url": "https://nssdc.gsfc.nasa.gov/...",
      "author": "NASA",
      "date": "2024-01-15",
      "stance": "contradicts",
      "credibility": "High",
      "domain_authority_score": 1.0,
      "temporal_freshness_score": 0.7,
      "credibility_score": 0.92,
      "tier": 1,
      "relevance": 10,
      "summary": "NASA confirms Earth's curvature.",
      "quote": "Earth's equatorial radius is 6378 km."
    }
  ]
}
```

### Threat Scan Response

```json
{
  "jobId": "uuid",
  "threats": [
    {
      "threat_type": "vendor",
      "severity": "high",
      "title": "Supply chain vendor reports data breach",
      "description": "A major vendor reported a breach...",
      "source_url": "https://krebsonsecurity.com",
      "source_domain": "krebsonsecurity.com",
      "confidence": 0.85,
      "alert_status": "new",
      "body_preview": "The breach exposed...",
      "bright_data_product": "Residential Proxies"
    }
  ],
  "count": 1
}
```

### Circuit Breaker Health Response

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

### Backend (`factguard-backend/.env`)

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `GEMINI_API_KEYS` | ✅ | — | Comma-separated Gemini API keys |
| `SUPABASE_URL` | ✅ | — | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | — | Supabase admin key |
| `BRIGHTDATA_API_KEY` | ✅ | — | BrightData API key |
| `GROQ_API_KEY` | — | — | Groq API key (free fallback AI) |
| `BRIGHTDATA_SERP_ZONE` | — | — | BrightData SERP zone name (auto-discovered if unset) |
| `CLAUDE_API_KEYS` | — | — | Comma-separated Claude API keys |
| `DEEPSEEK_API_KEYS` | — | — | OpenRouter/DeepSeek keys |
| `REDIS_URL` | — | — | Redis connection string |
| `FRONTEND_URL` | — | `http://localhost:3000` | CORS allowed origin |
| `GEMINI_MODEL_NAME` | — | `gemini-2.5-flash` | Gemini model |
| `CACHE_TTL` | — | `86400` | Cache TTL in seconds |
| `LOG_LEVEL` | — | `INFO` | Logging verbosity |

### Frontend (`factguard-frontend/.env.local`)

| Variable | Required | Description |
|----------|:--------:|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend URL (e.g. `http://localhost:8000`) |

---

## Key Design Decisions

- **Three-provider free AI resilience chain**: Gemini → DeepSeek → Groq + heuristic fallback — enterprise-grade failover without paid APIs
- **Circuit breaker pattern**: Each Bright Data integration has independent failure tracking with auto-reset, preventing cascading failures
- **3-tier content extraction**: Crawl API → Web Unlocker → Scraping Browser — each tier handles progressively harder cases
- **Composite credibility scoring**: Domain authority (35%) + stance alignment (25%) + temporal freshness (20%) + base tier (20%)
- **Multi-track architecture**: Single product, four demo scenarios — GTM Intelligence, Finance & Risk, Security & Compliance, Cart
- **Source fabrication prohibition**: Every URL is validated against actual search results — no AI hallucinations
- **Polling architecture**: Job-based async processing with Redis progress tracking — works on any hosting platform
- **`bright_data_product` tagging**: Every extraction and discovery call is tagged with the originating Bright Data product name
- **MCP Discover as Step 0**: Before any extraction, queries MCP Server for available tools
