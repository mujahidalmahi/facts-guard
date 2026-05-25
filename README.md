# FactGuard — AI-Powered Truth Engine

FactGuard is a **three-mode AI platform** that helps you figure out what's true online. Think of it as a personal fact-checker that reads the internet for you:

- **Verify Mode** — Paste a claim (like "The Earth is flat") and get a verdict backed by real web sources
- **Financial Mode** — Ask about a stock or market (like "Is Tesla overvalued?") and get an AI analyst brief
- **Cart Mode** — Search for a product (like "iPhone 16 Pro") and get trust-scored price comparisons

Every answer comes with **live web evidence**, **source citations**, and a **confidence score** — so you can see exactly why FactGuard reached its conclusion.

---

## Table of Contents

1. [How It Works (For Beginners)](#how-it-works-for-beginners)
2. [Architecture Overview](#architecture-overview)
3. [The Three Modes Explained](#the-three-modes-explained)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Setup Guide](#setup-guide)
7. [API Documentation](#api-documentation)
8. [Data Flow (How a Claim Becomes a Verdict)](#data-flow)
9. [Environment Variables](#environment-variables)
10. [Key Design Decisions](#key-design-decisions)

---

## How It Works (For Beginners)

Imagine you hear a rumour and want to know if it's true. You'd normally:
1. Search Google
2. Read a few articles
3. Decide which sources are trustworthy
4. Make a judgement

FactGuard does all four steps **automatically** in under 60 seconds:

```
You type a claim          ──►  FactGuard searches the web
                                   (via BrightData API)
                                     │
                                     ▼
                            AI reads the search results
                                   (Gemini 2.5 Flash)
                                     │
                                     ▼
                            AI produces a structured verdict:
                            "Verified" / "Likely True" / etc.
                            + confidence score
                            + list of sources with quotes
                            + bias detection
```

---

## Architecture Overview

FactGuard follows a standard **client-server architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                   BROWSER (Frontend)                     │
│                                                         │
│  Next.js 16 · React 19 · TypeScript · Tailwind v4       │
│  Framer Motion (animations) · Lucide (icons)            │
│                                                         │
│  Pages: Splash → Input → Loading → Result               │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (REST API)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   SERVER (Backend)                       │
│                                                         │
│  Python 3.12 · FastAPI · Uvicorn                        │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ /verify  │  │/financial│  │  /cart   │  ← API routes │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │             │                     │
│       ▼              ▼             ▼                     │
│  ┌─────────────────────────────────────┐                │
│  │       AI Analysis Engines           │                │
│  │  Gemini 2.5 Flash (primary)         │                │
│  │  DeepSeek (financial fallback)      │                │
│  └──────────────┬──────────────────────┘                │
│                 │                                       │
│                 ▼                                       │
│  ┌─────────────────────────────────────┐                │
│  │        Web Search Layer             │                │
│  │  BrightData SERP API (primary)      │                │
│  │  DuckDuckGo (fallback)              │                │
│  └──────────────┬──────────────────────┘                │
│                 │                                       │
│                 ▼                                       │
│  ┌─────────────────────────────────────┐                │
│  │     Persistence & Cache             │                │
│  │  Supabase (Postgres) — permanent    │                │
│  │  Redis (Upstash) — cache + progress │                │
│  └─────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────┘
```

### What each piece does:

| Layer | Job |
|-------|-----|
| **Frontend** | What you see in your browser. Handles user input, shows loading animations, displays results |
| **API Routes** | The backend's "doors" — each mode has its own door (`/verify`, `/financial`, `/cart`) |
| **AI Engines** | The "brain" — reads search results and makes judgements. Gemini is the main brain, DeepSeek is a backup |
| **Web Search** | The "eyes" — reads the live internet to find evidence. BrightData is the primary source, DuckDuckGo is a backup |
| **Database/Cache** | The "memory" — stores results permanently (Supabase) and keeps a fast temporary cache (Redis) |

---

## The Three Modes Explained

### 1. Verify Mode (Misinformation Detection)

**Use when:** You see a suspicious headline, social media post, or claim.

**What happens:**
1. Your claim is sent to the backend
2. BrightData searches Google for relevant articles
3. Gemini reads the search results and produces:
   - A **verdict** (Verified → Likely Misleading → Unverified)
   - A **confidence level** (High / Medium / Low)
   - A **narrative frame** (e.g. "Uses alarmist language to imply urgency")
   - **Bias signals** detected in the claim (e.g. cherry_picking, emotional_language)
   - A **source diversity** score (High / Medium / Low)

**What makes it special:** Unlike ChatGPT which makes up answers, FactGuard cites real URLs and quotes from live search results. If a source doesn't exist in the search results, it won't invent it.

### 2. Financial Mode (Market Intelligence)

**Use when:** You want to know if a stock is a buy/sell, or understand a market trend.

**What happens:**
1. Your query goes to the backend
2. BrightData searches for news + yFinance fetches price charts
3. DeepSeek (or Gemini) analyzes everything and returns:
   - A **signal** (Bullish / Bearish / Neutral)
   - A **signal strength** (0-100)
   - A **30-day prediction** with three scenarios (bull / base / bear)
   - **Risk catalysts** — specific risks to watch
   - **Data freshness** indicator

### 3. Cart Mode (Price Comparison)

**Use when:** You're shopping and want to know the best deal without getting scammed.

**What happens:**
1. You type a product name
2. BrightData searches major retailers
3. Gemini analyzes each listing with a **trust framework**:
   - **GREEN** — Verified retailer, fair price, in stock
   - **YELLOW** — Unverified seller, or price is 10-30% off
   - **RED** — Too cheap (>30% below MSRP = counterfeit risk), unknown seller
4. Returns: the best deal, trust assessment per listing, counterfeit risk, and a recommendation

---

## Tech Stack

### Backend
| Technology | Why it's used |
|------------|---------------|
| **Python 3.12** | Easy to read, huge AI/ML library ecosystem |
| **FastAPI 0.115** | Modern Python web framework — fast, automatic API docs |
| **Uvicorn** | Python server that handles many users at once |
| **Google Gemini 2.5 Flash** | Primary AI — fast, cheap, great at reasoning |
| **DeepSeek (via OpenRouter)** | Backup AI for financial analysis |
| **BrightData SERP API** | Real Google search results (this is a BrightData hackathon!) |
| **Supabase** | Postgres database — stores all results permanently |
| **Redis (Upstash)** | Fast in-memory cache — avoids re-processing the same claim |
| **httpx** | Modern Python HTTP client for API calls |

### Frontend
| Technology | Why it's used |
|------------|---------------|
| **Next.js 16** | React framework — handles routing, builds, and server rendering |
| **React 19** | Library for building user interfaces |
| **TypeScript** | JavaScript with types — catches bugs before they happen |
| **Tailwind CSS v4** | Write CSS directly in HTML — fast, consistent styling |
| **Framer Motion** | Smooth animations — makes the UI feel polished |
| **Lucide React** | Beautiful open-source icons |

---

## Project Structure

```
news-guard/
│
├── .github/workflows/ci.yml     # Auto-tests on every git push
├── docker-compose.yml           # One-command server setup
├── database/                    # SQL schema files
│   ├── schema.sql               # Main database structure
│   ├── schema2.sql              # Alternative schema
│   ├── finance_cart.sql         # Finance/cart tables
│   └── market.sql               # Market data tables
│
├── factguard-backend/           # 👈 THE SERVER (Python)
│   ├── .env                     # Secret keys (never commit!)
│   ├── .env.example             # Template for .env
│   ├── requirements.txt         # List of Python packages
│   ├── Dockerfile               # Container packaging
│   ├── app/
│   │   ├── main.py              # App entry point — wires everything together
│   │   ├── config.py            # Reads .env variables into Python objects
│   │   ├── schemas.py           # Defines request/response data shapes
│   │   ├── exceptions.py        # Custom error types
│   │   ├── middleware.py        # Global error handling
│   │   ├── logging_config.py    # Logging setup
│   │   ├── dependencies.py      # Shared services (Gemini, Supabase clients)
│   │   │
│   │   ├── api/                 # API ROUTES (the "doors")
│   │   │   ├── verify.py        # POST /verify — submit a claim
│   │   │   ├── financial.py     # POST /financial — market query
│   │   │   ├── pricing.py       # POST /cart — product search
│   │   │   └── history.py       # GET /history — past results
│   │   │
│   │   ├── services/            # BUSINESS LOGIC (the "brain")
│   │   │   ├── gemini.py        # Gemini AI — verify mode prompt + parsing
│   │   │   ├── deepseek.py      # DeepSeek AI — financial analysis
│   │   │   ├── cart_ai.py       # Gemini AI — cart mode prompt + parsing
│   │   │   ├── financial.py     # Orchestrates financial analysis (yfinance + AI)
│   │   │   ├── pricing.py       # Orchestrates price comparison
│   │   │   ├── router_ai.py     # Decides which mode a query belongs to
│   │   │   ├── cache.py         # Redis — claim dedup + progress tracking
│   │   │   ├── supabase_db.py   # Saves/loads data from Supabase
│   │   │   ├── credibility.py   # Rates source credibility
│   │   │   └── db.py            # Low-level database helpers
│   │   │
│   │   └── utils/               # UTILITY CODE (the "tools")
│   │       ├── search.py        # Web search via BrightData (primary) or DuckDuckGo (fallback)
│   │       ├── parsing.py       # Extracts JSON from AI responses
│   │       ├── pricing_parser.py# Parses pricing data from search results
│   │       ├── validators.py    # Detects SQL injection attempts
│   │       └── constants.py     # Shared constants (verdicts, etc.)
│   │
│   ├── scripts/
│   │   └── seed_demo.py         # Pre-loads demo data
│   └── tests/                   # Automated tests
│       ├── test_constants.py
│       ├── test_pricing_parser.py
│       └── test_validators.py
│
├── factguard-frontend/          # 👈 THE BROWSER APP (TypeScript)
│   ├── .env.local               # Frontend secrets
│   ├── package.json             # List of JavaScript packages
│   ├── Dockerfile               # Container packaging
│   │
│   ├── app/                     # PAGES (each folder = a URL route)
│   │   ├── layout.tsx           # Root layout — Nav bar, footer, fonts
│   │   ├── globals.css          # Global styles + custom CSS classes
│   │   ├── page.tsx             # Home page — mode switcher + input + splash
│   │   │
│   │   ├── loading/             # Loading page (shown while AI works)
│   │   │   └── page.tsx         # Progress steps + animated spinner
│   │   │
│   │   ├── price-loading/       # Legacy cart loading page
│   │   │   └── page.tsx
│   │   │
│   │   ├── history/             # History page
│   │   │   └── page.tsx         # Shows past verifications
│   │   │
│   │   └── result/              # Result pages
│   │       └── [jobId]/         # Dynamic route: /result/some-job-id
│   │           ├── page.tsx     # Main result — shows verdict, sources, graph
│   │           ├── layout.tsx   # OG image metadata for social sharing
│   │           ├── FinancialResultView.tsx  # Financial mode result card
│   │           └── CartResultView.tsx       # Cart mode result card
│   │
│   ├── components/              # REUSABLE UI PIECES
│   │   ├── Nav.tsx              # Navigation bar
│   │   ├── ModeSwitcher.tsx     # Toggle between verify/financial/cart
│   │   ├── VerdictBadge.tsx     # Animated verdict card (Verified, Likely True, etc.)
│   │   ├── ConfidencePill.tsx   # Confidence level badge
│   │   ├── AgreementMeter.tsx   # Bar chart: supports vs contradicts
│   │   ├── EvidenceTimeline.tsx # Sorted source list with tier badges
│   │   ├── SourceGraph.tsx      # Interactive node graph of sources
│   │   ├── BiasHeatmap.tsx      # Detected bias signals as pill chips
│   │   ├── SignalBadge.tsx      # Financial signal (Bullish/Bearish/Neutral)
│   │   ├── PriceChart.tsx       # Price history line chart
│   │   ├── CartProductCard.tsx  # Product listing card with trust score
│   │   ├── PriceComparisonTable.tsx
│   │   ├── PriceCheckSection.tsx
│   │   ├── PriceShareCard.tsx
│   │   ├── ProductVariants.tsx
│   │   ├── ShareCard.tsx        # Copy link to result
│   │   ├── Skeleton.tsx         # Loading placeholder
│   │   ├── SplashScreen.tsx     # First-visit welcome screen
│   │   ├── ThemeProvider.tsx    # Dark/light mode switching
│   │   ├── ThemeScript.tsx      # Prevents flash on page load
│   │   ├── ErrorBoundary.tsx    # Catches crashes gracefully
│   │   ├── ResultErrorBoundary.tsx
│   │   └── ui/                  # Basic building blocks
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── progress.tsx
│   │       └── separator.tsx
│   │
│   ├── lib/                     # SHARED CODE
│   │   ├── constants.ts         # Colors, example data
│   │   ├── utils.ts             # Helper functions
│   │   ├── polling.ts           # Polling utility
│   │   └── useJobPolling.ts     # React hook: polls backend every 1.5s
│   │
│   └── types/
│       └── index.ts             # All TypeScript type definitions
│
├── splash-demo.html             # Standalone demo page
├── export_for_review.py         # Export tool
└── README.md                    # This file!
```

---

## Setup Guide

### Prerequisites (What you need installed)

| Tool | Version | Why |
|------|---------|-----|
| **Python** | 3.12+ | Runs the backend |
| **Node.js** | 20+ | Runs the frontend |
| **pnpm** | Latest | Package manager (like npm but faster) |
| **Git** | Any | Version control |
| **Supabase account** | Free | Database hosting |
| **Google AI Studio key** | Free | Gemini API access |

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd news-guard
```

### Step 2: Set Up the Backend

```bash
cd factguard-backend

# Create a virtual environment (isolates Python packages)
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a file called `.env` inside `factguard-backend/`:

```env
# Required: Get your key from https://aistudio.google.com/apikey
GEMINI_API_KEYS=your-gemini-key-here

# Required: Your Supabase project URL and service role key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Required for BrightData (BrightData hackathon!):
BRIGHTDATA_API_KEY=your-brightdata-key

# Optional but recommended:
REDIS_URL=rediss://default:password@host:port
FRONTEND_URL=http://localhost:3000
```

### Step 3: Set Up the Database

1. Go to [Supabase Dashboard](https://supabase.com)
2. Create a new project (free tier works)
3. Open the **SQL Editor**
4. Copy and paste the contents of `database/schema.sql`
5. Click **Run** — this creates all the tables

### Step 4: Seed Demo Data (Optional)

```bash
cd factguard-backend
python scripts/seed_demo.py
```

This pre-loads some example claims and results into Redis so you can test without waiting for AI each time.

### Step 5: Start the Backend

```bash
cd factguard-backend
python -m uvicorn app.main:app --reload --port 8000
```

Your backend is now running at `http://localhost:8000`. You can visit `http://localhost:8000/docs` for an interactive API testing page (Swagger UI).

### Step 6: Set Up the Frontend

Open a **new terminal** (keep the backend running):

```bash
cd factguard-frontend

# Install JavaScript dependencies
pnpm install
```

Create `.env.local` in `factguard-frontend/`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 7: Start the Frontend

```bash
cd factguard-frontend
pnpm dev
```

Your frontend is now running at `http://localhost:3000`. Open it in your browser!

---

## API Documentation

### Endpoints

| Method | Path | What it does |
|--------|------|-------------|
| `POST` | `/verify` | Submit a claim to fact-check |
| `POST` | `/financial` | Submit a financial/market question |
| `POST` | `/cart` | Submit a product name for price comparison |
| `GET` | `/result/{job_id}?mode=verify\|financial\|cart` | Poll for the result |
| `GET` | `/history` | Get recent results |
| `GET` | `/health` | Check if server is alive |

### Verify Mode — Full Response Shape

```json
{
  "status": "done",
  "jobId": "abc-123-def",
  "mode": "verify",
  "claim": "Is the Earth flat?",
  "verdict": "Likely Misleading",
  "confidence": "High",
  "narrative_frame": "Uses a false dichotomy to dismiss centuries of scientific consensus.",
  "summary": "Overwhelming scientific evidence from NASA, NOAA, and every major space agency confirms Earth is an oblate spheroid. The claim contradicts all available satellite imagery, physics, and direct observation.",
  "supports": 0,
  "contradicts": 5,
  "neutral": 1,
  "bias_signals": ["cherry_picking", "false_equivalence"],
  "source_diversity": "High",
  "sources": [
    {
      "title": "NASA: Earth Fact Sheet",
      "url": "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html",
      "author": "NASA",
      "date": "2024-01-15",
      "stance": "contradicts",
      "credibility": "High",
      "tier": 1,
      "relevance": 10,
      "summary": "NASA provides detailed measurements confirming Earth's curvature.",
      "quote": "Earth's equatorial radius is 6378 km, polar radius is 6357 km."
    }
  ]
}
```

### Financial Mode — Key Fields

```json
{
  "analysis": {
    "signal": "Bullish",
    "signal_strength": 78,
    "asset": "Tesla Inc. (TSLA)",
    "current_price": "$345.20",
    "price_trend": "Up",
    "trend_magnitude": "Strong",
    "risk_level": "Medium",
    "risk_catalysts": [
      "Regulatory probe into Autopilot claims",
      "EU tariff escalation on Chinese EVs",
      "Bond yield spike compressing growth valuations"
    ],
    "key_factors": ["Q2 delivery beat", "Energy storage revenue up 40%"],
    "summary": "3-4 sentence institutional-quality brief...",
    "prediction_30d": {
      "bull_case": "$380+ (45%) — requires FSD approval catalyst",
      "base_case": "$340-360 (35%) — steady delivery growth",
      "bear_case": "$300-320 (20%) — triggered by macro downturn"
    },
    "data_freshness": "real-time"
  }
}
```

### Cart Mode — Key Fields

```json
{
  "analysis": {
    "product_name": "Sony WH-1000XM5",
    "msrp": "$349.99",
    "fair_market_range": { "min": "$288.00", "max": "$349.99", "currency": "USD" },
    "best_deal": {
      "merchant": "Amazon",
      "price": "$288.00",
      "url": "https://amazon.com/...",
      "reason": "Lowest price from a verified authorized retailer with free returns"
    },
    "listings": [{
      "title": "Sony WH-1000XM5 Wireless...",
      "merchant": "Amazon",
      "price": 288.00,
      "currency": "USD",
      "url": "https://...",
      "trust_level": "GREEN",
      "deal_score": 92,
      "trust_reason": "Amazon is a verified authorized Sony retailer",
      "counterfeit_risk": "None",
      "condition": "New",
      "in_stock": true
    }],
    "analysis": {
      "warnings": ["Price on eBay is 35% below MSRP — high counterfeit risk"],
      "recommendation": "Buy from Amazon at $288.00...",
      "price_trend": "Stable",
      "best_time_to_buy": "Now"
    }
  }
}
```

### Processing Response (while waiting)

```json
{
  "status": "processing",
  "jobId": "abc-123-def"
}
```

---

## Data Flow

Here's exactly what happens when you type a claim and press submit:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. YOU type "The Earth is flat" and click "Analyse Claim"          │
│    ┌─────────────────────────────────────────────────────────┐     │
│    │ Frontend: POST /verify  { "claim": "The Earth is flat" }│     │
│    └────────────┬────────────────────────────────────────────┘     │
└─────────────────┼───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. BACKEND receives the claim                                      │
│    ┌─────────────────────────────────────────────────────────┐     │
│    │ a. Creates a job record in Supabase database             │     │
│    │ b. Sets Redis progress: "Checking cache..."             │     │
│    │ c. Checks Redis for an identical past claim (SHA-256    │     │
│    │    hash) → HIT? Return cached result instantly → DONE!  │     │
│    │ d. MISS? Start background processing...                 │     │
│    └─────────────────────────────────────────────────────────┘     │
└─────────────────┼───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. WEB SEARCH (BrightData)                                         │
│    ┌─────────────────────────────────────────────────────────┐     │
│    │ a. Backend calls BrightData SERP API:                   │     │
│    │    "https://api.brightdata.com/request"                 │     │
│    │    with query "The Earth is flat"                       │     │
│    │ b. BrightData returns Google-like search results        │     │
│    │ c. Backend extracts: title, URL, snippet from each      │     │
│    │ d. If BrightData fails → falls back to DuckDuckGo       │     │
│    │ e. Sets Redis progress: "Analysing with AI..."          │     │
│    └─────────────────────────────────────────────────────────┘     │
└─────────────────┼───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. AI ANALYSIS (Gemini 2.5 Flash)                                  │
│    ┌─────────────────────────────────────────────────────────┐     │
│    │ a. Backend builds a prompt (instructions + search data): │     │
│    │    "You are VERITAS... Here are the search results...   │     │
│    │     Now evaluate this claim: 'The Earth is flat'"       │     │
│    │ b. Gemini thinks inside <scratchpad>:                   │     │
│    │    Step 1: Is the claim empirical? Yes.                 │     │
│    │    Step 2: What framing? False dichotomy.               │     │
│    │    Step 3: Source triage — NASA contradicts, ...        │     │
│    │    Step 4: Strong consensus against claim.              │     │
│    │    Step 5: Verdict = Likely Misleading, High confidence │     │
│    │ c. Gemini returns structured JSON                       │     │
│    │ d. Backend validates: all required fields present?       │     │
│    │    verdict valid? sources have real URLs?               │     │
│    └─────────────────────────────────────────────────────────┘     │
└─────────────────┼───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. STORE & RETURN                                                  │
│    ┌─────────────────────────────────────────────────────────┐     │
│    │ a. Save result to Supabase (permanent storage)          │     │
│    │ b. Save to Redis cache (24h TTL — next hit is instant)  │     │
│    │ c. Set Redis progress: "Saving results..."              │     │
│    │ d. Mark job as complete                                 │     │
│    └─────────────────────────────────────────────────────────┘     │
└─────────────────┼───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. FRONTEND receives the result                                    │
│    ┌─────────────────────────────────────────────────────────┐     │
│    │ a. The loading page was polling every 1.5 seconds:      │     │
│    │    GET /result/job-123?mode=verify                       │     │
│    │ b. Now status = "done" → redirects to /result/job-123   │     │
│    │ c. Result page shows:                                   │     │
│    │    - Verdict badge with glow animation                   │     │
│    │    - Confidence + source diversity badges               │     │
│    │    - Narrative frame (italic blockquote)                │     │
│    │    - Summary explanation                                │     │
│    │    - Agreement meter (bar chart)                         │     │
│    │    - Bias heatmap (if biases detected)                  │     │
│    │    - Evidence timeline (sorted by tier)                  │     │
│    │    - Source graph (toggle list/graph view)              │     │
│    │    - Share + download buttons                           │     │
│    └─────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concept: Why Polling?

You might wonder: "Why does the frontend keep asking (polling) instead of waiting for an answer?"

This is a common pattern in web development. Since AI analysis can take 15-30 seconds, we can't keep the HTTP connection open that long. Instead:

1. The backend immediately returns a `jobId` (a unique identifier)
2. The frontend asks "is it done yet?" every 1.5 seconds
3. When the answer is ready, the frontend shows the result

Think of it like ordering pizza: you get a ticket number right away, then check back until your order is ready.

---

## Environment Variables

### Backend (`factguard-backend/.env`)

| Variable | Required | Default | What it does |
|----------|----------|---------|-------------|
| `GEMINI_API_KEYS` | ✅ Yes | — | Comma-separated Gemini API keys (you can have multiple for redundancy) |
| `SUPABASE_URL` | ✅ Yes | — | Your Supabase project URL (found in Supabase dashboard → Settings → API) |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | — | Supabase admin key (kept secret — never in frontend code!) |
| `BRIGHTDATA_API_KEY` | ✅ Yes | — | BrightData API key for web search |
| `DEEPSEEK_API_KEYS` | No | — | Comma-separated DeepSeek/OpenRouter keys (fallback AI) |
| `REDIS_URL` | No | — | Redis connection string (for caching). Without it, app still works — just slower |
| `FRONTEND_URL` | No | `http://localhost:3000` | Which domain is allowed to call the API (CORS) |
| `GEMINI_MODEL_NAME` | No | `gemini-2.5-flash` | Which Gemini model to use |
| `CACHE_TTL` | No | `86400` | How many seconds to cache a claim result (86400 = 24 hours) |
| `LOG_LEVEL` | No | `INFO` | How detailed logs should be (DEBUG = very detailed, INFO = normal, WARNING = only issues) |

### Frontend (`factguard-frontend/.env.local`)

| Variable | Required | What it does |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | The backend's URL (e.g. `http://localhost:8000` or your deployed URL) |

---

## Key Design Decisions

### Why Redis for caching?
Redis is an in-memory database — it's extremely fast. When you check the same claim twice, Redis returns the cached result in milliseconds instead of waiting 20 seconds for the AI again. This also saves money on API calls.

### Why polling instead of WebSockets?
WebSockets (real-time two-way communication) would be more elegant, but polling is simpler and more reliable. The frontend asks "is it done?" every 1.5 seconds — this works on any hosting platform and doesn't require special server configuration.

### Why multiple API keys?
Both Gemini and DeepSeek have rate limits (you can only make so many requests per minute). By providing multiple keys, FactGuard automatically rotates to the next key when one runs out.

### Why source fabrication prohibition?
Large language models (LLMs) sometimes "hallucinate" — they make up convincing-sounding URLs and quotes. The VERITAS prompt has strict rules against this, and the backend validates that every source URL actually came from the search results.

### Why bias detection?
Standard fact-checking tells you IF something is true. FactGuard also tells you HOW the claim tries to manipulate you (e.g., cherry-picking data, using emotional language). This is a unique feature that helps users build critical thinking skills.
