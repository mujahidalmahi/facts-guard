# FactGuard Frontend

This is the **browser app** for FactGuard — what you see and interact with. Built with **Next.js 16**, React framework that handles routing, page rendering, and builds.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [How the Frontend is Organized](#how-the-frontend-is-organized)
3. [Page Flow (The User's Journey)](#page-flow-the-users-journey)
4. [Components Explained](#components-explained)
5. [How Data Moves Through the Frontend](#how-data-moves-through-the-frontend)
6. [Setup](#setup)
7. [Pages](#pages)
8. [Commands](#commands)
9. [Design System](#design-system)

---

## Project Structure

```
factguard-frontend/
│
├── .env.local                   # Frontend secrets (e.g., API URL)
├── .env.example                 # Template — copy to .env.local
├── package.json                 # List of JavaScript packages
├── tsconfig.json                # TypeScript configuration
├── postcss.config.mjs           # CSS processing config
├── next.config.ts               # Next.js configuration
├── vercel.json                  # Vercel deployment config
│
├── public/                      # Static files (images, icons)
│
├── app/                         # 👈 PAGES (each folder = a URL)
│   │
│   ├── layout.tsx               # Root layout — wraps every page
│   │                            #   Contains: Nav, Theme, Footer
│   │
│   ├── globals.css              # Global styles (Tailwind + custom)
│   │
│   ├── page.tsx                 # HOME PAGE ("/") — 4-mode switcher + input
│   │
│   ├── loading/                 # LOADING PAGE ("/loading?job=...&mode=...")
│   │   └── page.tsx             #   Animated spinner + progress steps
│   │
│   ├── price-loading/           # LEGACY loading page for cart mode
│   │   └── page.tsx
│   │
│   ├── history/                 # HISTORY PAGE ("/history")
│   │   └── page.tsx             #   Past results from database
│   │
│   └── result/                  # RESULT PAGES ("/result/some-job-id?mode=...")
│       └── [jobId]/             #   Dynamic route — [jobId] changes per result
│           ├── page.tsx           # Main result display (all 4 modes)
│           ├── layout.tsx         # OG image metadata (for social sharing)
│           ├── FinancialResultView.tsx  # Financial mode result
│           ├── CartResultView.tsx       # Cart mode result
│           └── ThreatResultView.tsx     # Security mode result + report download
│
├── components/                  # 👈 REUSABLE UI COMPONENTS
│   │
│   │  # === Navigation & Layout ===
│   ├── Nav.tsx                  # Top bar with Bright Data health dots
│   │                           #   5 colored circles (MCP/SERP/Crawl/Unlock/Browser)
│   │                           #   Polls /routing/health every 15s
│   ├── ModeSwitcher.tsx         # 4-mode toggle: Verify | Financial | Security | Cart
│   ├── ThemeProvider.tsx        # Dark/light mode context
│   ├── ThemeScript.tsx          # Prevents white flash on page load
│   │
│   │  # === Result Display ===
│   ├── VerdictBadge.tsx         # Animated verdict card
│   ├── ConfidencePill.tsx       # Confidence level (High/Medium/Low)
│   ├── AgreementMeter.tsx       # Stacked bar (supports vs contradicts)
│   ├── EvidenceTimeline.tsx     # Sorted source list with stance stripes
│   ├── SourceGraph.tsx          # SVG node graph of sources
│   ├── BiasHeatmap.tsx          # Detected bias manipulation signals
│   ├── SignalBadge.tsx          # Financial signal (Bullish/Bearish/Neutral)
│   ├── PriceChart.tsx           # Price history line chart
│   │
│   │  # === Security Mode ===
│   ├── ThreatResultView.tsx     # Threat list with severity bars + download report
│   │
│   │  # === Cart Mode ===
│   ├── CartProductCard.tsx      # Product card with trust score
│   ├── PriceComparisonTable.tsx # Side-by-side price comparison
│   ├── PriceCheckSection.tsx
│   ├── PriceShareCard.tsx
│   ├── ProductVariants.tsx
│   │
│   │  # === Utility ===
│   ├── ShareCard.tsx            # Copy result link
│   ├── Skeleton.tsx             # Loading placeholder
│   ├── SplashScreen.tsx         # First-visit welcome screen
│   ├── ErrorBoundary.tsx        # Catches crashes gracefully
│   ├── ResultErrorBoundary.tsx
│   │
│   │  # === UI Primitives ===
│   └── ui/                      # Base building blocks
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── progress.tsx
│       └── separator.tsx
│
├── lib/                         # 👈 SHARED CODE (not React)
│   ├── constants.ts             # Colors, verdict mappings, example data
│   ├── utils.ts                 # Helpers (e.g., cn() for class merging)
│   └── useJobPolling.ts         # React hook — polls backend every 1.5s
│
└── types/                       # 👈 TYPE DEFINITIONS
    └── index.ts                 # ThreatResult, TrackType, ThreatType, etc.
```

---

## How the Frontend is Organized

| Folder | What it is |
|--------|-----------|
| `app/` | Each room in the house — one folder per page/URL |
| `components/` | The furniture — reusable pieces that can go in any room |
| `lib/` | The toolbox — shared utilities and helpers |
| `types/` | The blueprint — defines what everything looks like |

### The `app/` folder (Next.js App Router)

Next.js uses **file-based routing**:

| URL | Folder | What you see |
|-----|--------|-------------|
| `/` | `app/page.tsx` | Home page |
| `/loading` | `app/loading/page.tsx` | Loading page |
| `/history` | `app/history/page.tsx` | History page |
| `/result/abc-123` | `app/result/[jobId]/page.tsx` | Result for job "abc-123" |

The `[jobId]` folder is a **dynamic route** — `[brackets]` mean "any value works here." A single component handles ALL results.

---

## Page Flow (The User's Journey)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. HOME PAGE (/)                                                    │
│                                                                     │
│    ┌─────────────────────────────────────────────────────────┐      │
│    │ On first visit → SplashScreen (welcome message)         │      │
│    │                                                         │      │
│    │ You see:                                                 │      │
│    │  • ModeSwitcher: [Verify] [Financial] [Security] [Cart] │      │
│    │  • Mode badge with rotating taglines                     │      │
│    │  • Animated gradient headline                            │      │
│    │  • Glassmorphism textarea with character counter        │      │
│    │  • Glowing "Analyse Claim" button                        │      │
│    │  • Example buttons (click to auto-fill)                  │      │
│    └─────────────────────────────────────────────────────────┘      │
│                        │                                            │
│                        ▼ Type a query, click submit                 │
│                        │                                            │
└────────────────────────┼────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. LOADING PAGE (/loading?job=abc-123&mode=verify)                 │
│                                                                     │
│    ┌─────────────────────────────────────────────────────────┐      │
│    │ Polls backend every 1.5 seconds:                         │      │
│    │   GET /result/abc-123?mode=verify                       │      │
│    │                                                         │      │
│    │ You see:                                                 │      │
│    │  • Spinning indigo loading indicator                    │      │
│    │  • Progress bar with step-by-step checklist:             │      │
│    │       ● Checking cache...                                │      │
│    │       ● Searching via Bright Data...                     │      │
│    │       ● Analysing with AI...                             │      │
│    │       ● Saving results...                                │      │
│    │  • "Powered by BrightData" footer                        │      │
│    └─────────────────────────────────────────────────────────┘      │
│                        │                                            │
│              When status = "done" → redirect                        │
└────────────────────────┼────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. RESULT PAGE (/result/abc-123?mode=verify)                       │
│                                                                     │
│    ┌─────────────────────────────────────────────────────────┐      │
│    │ Displays the verdict/analysis based on mode:            │      │
│    │                                                         │      │
│    │ For VERIFY mode:                                         │      │
│    │  • Original claim card                                   │      │
│    │  • Animated verdict badge with glow + icon               │      │
│    │  • Confidence pill + source diversity badge              │      │
│    │  • Narrative frame + summary                             │      │
│    │  • Agreement meter (supports vs contradicts bar)        │      │
│    │  • Bias heatmap (if biases detected)                    │      │
│    │  • Source list/network toggle [List] [Graph]            │      │
│    │    Graph: nodes as colored circles                       │      │
│    │    (green=support, red=contradict, gray=neutral)        │      │
│    │  • Share + download buttons                              │      │
│    │                                                         │      │
│    │ For FINANCIAL mode:                                      │      │
│    │  • Signal badge (Bullish/Bearish/Neutral)               │      │
│    │  • Signal strength gauge (0-100 arc)                    │      │
│    │  • Price trend + risk level + freshness dot              │      │
│    │  • Price chart (from yFinance)                          │      │
│    │  • Key factors + risk catalysts                         │      │
│    │  • 30-day prediction (bull/base/bear columns)           │      │
│    │  • Market sources                                        │      │
│    │                                                         │      │
│    │ For SECURITY mode:                                       │      │
│    │  • Threat count summary                                  │      │
│    │  • Per-threat cards with severity bar + type badge       │      │
│    │  • Confidence percentage for each threat                 │      │
│    │  • Source links to original articles                     │      │
│    │  • Download Report button (.txt compliance report)      │      │
│    │                                                         │      │
│    │ For CART mode:                                           │      │
│    │  • Product name + fair market range                     │      │
│    │  • Best deal card (star-highlighted)                    │      │
│    │  • Recommendation + price trend + best time to buy      │      │
│    │  • Warnings (red alert boxes)                           │      │
│    │  • Product grid: GREEN=trusted, YELLOW=unverified,      │      │
│    │    RED=risky                                            │      │
│    └─────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Components Explained

### VerdictBadge.tsx
The big animated card that shows the verdict. Each verdict has its own color, glow effect, icon, and spring animation.

### BiasHeatmap.tsx
Detected manipulation tactics as colored chips with tooltips. Hidden entirely when no signals detected.

### SourceGraph.tsx
SVG network of sources: nodes = sources (colored by stance, sized by credibility tier), toggle between List View and Graph View.

### AgreementMeter.tsx
Stacked horizontal bar: green (supports), gray (neutral), red (contradicts), with numerical breakdown.

### EvidenceTimeline.tsx
Vertical list of sources sorted by tier (government/academic first) then relevance. Shows colored stance stripe, title, author, date, tier badge, summary, and quote.

### ThreatResultView.tsx
Security track result display:
- Threat count with "no threats detected" emerald card when empty
- Per-threat motion cards with severity color (red/orange/amber/yellow)
- Type badge (Brand Threat, Regulatory Change, Vendor Risk, Disinformation Campaign)
- Confidence percentage + severity progress bar
- Source link to original article
- **Download Report** button: generates `.txt` compliance report from in-memory threats data

### CartProductCard.tsx
Product listing with merchant name, trust badge (ShieldCheck/AlertCircle/AlertTriangle), price, counterfeit risk, deal score (0-100), and trust reason.

### Nav.tsx
Top navigation bar with:
- Theme toggle (dark/light)
- Bright Data circuit-breaker health dots — 5 colored circles (MCP/SERP/Crawl/Unlock/Browser)
- Polls `GET /routing/health` every 15 seconds
- Green = circuit closed (healthy), Red = circuit open (down)

### ModeSwitcher.tsx
4-mode toggle: **Verify** · **Financial** · **Security** · **Cart**. Each mode changes the input placeholder, example buttons, and mode badge tagline.

---

## How Data Moves Through the Frontend

```
1. HOME PAGE (page.tsx)
   │
   │  User types input, clicks submit
   │
   ▼
2. POST to backend API
   │  fetch(`http://localhost:8000/verify`, {
   │    method: 'POST',
   │    body: JSON.stringify({ claim: input })
   │  })
   │
   ▼
3. Receive jobId → navigate to loading page
   │  router.push(`/loading?job=${data.jobId}&mode=verify`)
   │
   ▼
4. LOADING PAGE (loading/page.tsx)
   │  useJobPolling() hook runs:
   │  every 1.5s → GET /result/{jobId}?mode=verify
   │
   │  Returns progress + icon → shows steps with pulse-ring dots
   │
   ▼
5. Status = "done" → navigate to result page
   │  window.location.href = `/result/${jobId}?mode=verify`
   │
   ▼
6. RESULT PAGE (result/[jobId]/page.tsx)
   │
   │  Fetches result data one more time
   │  Renders appropriate view based on mode:
   │  • verify → VerdictBadge, AgreementMeter, etc.
   │  • financial → FinancialResultView
   │  • security → ThreatResultView
   │  • cart → CartResultView
   │
   ▼
7. User can share or download the result
   │  ShareCard → copies link to clipboard
   │  Download → saves JSON file
   │  Security: Download Report → saves .txt compliance report
```

### Key Concept: Polling vs Waiting

The frontend uses **polling** (asking repeatedly) instead of **waiting** (holding the connection open). AI analysis takes 15-30 seconds, and keeping an HTTP connection open that long is unreliable.

Think of it like checking if food is ready at a restaurant:
- **Polling**: "Is my order ready?" → "Not yet" → wait 1.5s → "Is my order ready?" → "Yes!"
- **Waiting**: Stand at the counter for 30 seconds staring at the chef

---

## Setup

### Prerequisites

- **Node.js** 20+ (JavaScript runtime)
- **pnpm** (faster alternative to npm)

### Step 1: Install Dependencies

```bash
cd factguard-frontend
pnpm install
```

### Step 2: Configure Environment

Create `.env.local` in the `factguard-frontend/` folder:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3: Start the Backend

Open a separate terminal and make sure the backend is running:

```bash
cd factguard-backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 4: Start the Frontend

```bash
pnpm dev
```

Your browser app is now at **http://localhost:3000**.

---

## Pages

| Route | File | What it does |
|-------|------|-------------|
| `/` | `app/page.tsx` | Home — 4-mode switcher, input, splash screen |
| `/loading?job=X&mode=Y` | `app/loading/page.tsx` | Polling with progress steps |
| `/result/:jobId` | `app/result/[jobId]/page.tsx` | Result display for all 4 modes |
| `/history` | `app/history/page.tsx` | Past verifications list |

---

## Commands

```bash
pnpm dev       # Start dev server with hot reload
pnpm build     # Type check + create production build
pnpm lint      # Check code for errors and style issues
pnpm start     # Start production server (after pnpm build)
```

---

## Design System

FactGuard uses a **dark space theme** with deep navy/indigo colors:

### CSS Variables

| Variable | Light | Dark | What it controls |
|----------|-------|------|-----------------|
| `--background` | White (`#ffffff`) | Deep navy (`#06091A`) | Page background |
| `--foreground` | Near-black (`#171717`) | Light slate (`#F1F5F9`) | Text color |
| `--accent` | Indigo (`#6366f1`) | Indigo (`#6366F1`) | Primary interactive color |
| `--card` | White | Translucent dark | Card backgrounds |
| `--glass` | Translucent white | Translucent dark | Glassmorphism panels |

### Custom CSS Classes

| Class | What it does | Where it's used |
|-------|-------------|-----------------|
| `.glass-card` | Translucent panel with blur effect | Input container, result cards |
| `.btn-glow` | Gradient button with glow shadow | Submit button |
| `.gradient-text` | Animated gradient (indigo → sky → indigo) | Main headline |
| `.pulse-ring` | Expanding ring animation | Mode badge dot, loading step indicators |

### Color Semantics

| Color | Meaning |
|-------|---------|
| **Emerald** (green) | Verified, supports, trusted, bullish |
| **Indigo** (purple-blue) | Likely True, neutral action, primary UI |
| **Amber** (yellow) | Mixed Evidence, medium confidence, unverified |
| **Red** | Likely Misleading, contradicts, risky, bearish |
| **Slate** (gray) | Unverified, neutral, stale data |

### Verdict Colors

Each verdict in `VERDICT_STYLES` has a `glow` color, gradient `bg`, `border`, `icon`, and `text` color.
