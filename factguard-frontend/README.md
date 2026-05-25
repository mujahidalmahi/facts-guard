# FactGuard Frontend

This is the **browser app** for FactGuard — what you see and interact with. It's built with **Next.js 16**, a popular React framework that handles routing, page rendering, and builds.

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
│
├── public/                      # Static files (images, icons)
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
│
├── app/                         # 👈 PAGES (each folder = a URL)
│   │
│   ├── layout.tsx               # Root layout — wraps every page
│   │                            #   Contains: fonts, Nav bar, Theme, Footer
│   │
│   ├── globals.css              # Global styles — Tailwind + custom CSS
│   │                            #   (glassmorphism, gradient text, etc.)
│   │
│   ├── page.tsx                 # HOME PAGE ("/") — the main interface
│   │                            #   Mode switcher + text input + splash screen
│   │
│   ├── loading/                 # LOADING PAGE ("/loading?job=...&mode=...")
│   │   └── page.tsx             #   Animated spinner + progress steps
│   │
│   ├── price-loading/           # LEGACY loading page for cart mode
│   │   └── page.tsx
│   │
│   ├── history/                 # HISTORY PAGE ("/history")
│   │   └── page.tsx             #   Shows past verifications from the database
│   │
│   └── result/                  # RESULT PAGES ("/result/some-job-id?mode=...")
│       └── [jobId]/             #   Dynamic route — [jobId] changes per result
│           ├── page.tsx         #   Main result display
│           ├── layout.tsx       #   OG image metadata (for social sharing)
│           ├── FinancialResultView.tsx  # Financial mode result
│           └── CartResultView.tsx       # Cart mode result
│
├── components/                  # 👈 REUSABLE UI COMPONENTS
│   │
│   │  # === Navigation & Layout ===
│   ├── Nav.tsx                  # Top navigation bar with theme toggle
│   ├── ModeSwitcher.tsx         # Toggle buttons: Verify | Financial | Cart
│   ├── ThemeProvider.tsx        # Dark/light mode context
│   ├── ThemeScript.tsx          # Prevents white flash on page load
│   │
│   │  # === Result Display ===
│   ├── VerdictBadge.tsx         # Animated verdict card (Verified → Unverified)
│   ├── ConfidencePill.tsx       # Confidence level (High/Medium/Low)
│   ├── AgreementMeter.tsx       # Stacked bar chart (supports vs contradicts)
│   ├── EvidenceTimeline.tsx     # Sorted source list with stance stripes
│   ├── SourceGraph.tsx          # Node graph visualization of sources
│   ├── BiasHeatmap.tsx          # Detected bias manipulation signals
│   ├── SignalBadge.tsx          # Financial signal (Bullish/Bearish/Neutral)
│   ├── PriceChart.tsx           # Price history line chart
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
│   └── ui/                      # Basic building blocks
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── progress.tsx
│       └── separator.tsx
│
├── lib/                         # 👈 SHARED CODE (not React components)
│   ├── constants.ts             # Colors, verdict mappings, example data
│   ├── utils.ts                 # Helper functions (e.g., cn() for class merging)
│   └── useJobPolling.ts         # React hook — polls backend every 1.5s
│
└── types/                       # 👈 TYPE DEFINITIONS
    └── index.ts                 # All TypeScript types/interfaces
```

---

## How the Frontend is Organized

Think of the frontend as a house with different rooms:

| Folder | What it is |
|--------|-----------|
| `app/` | Each room in the house — one folder per page/URL |
| `components/` | The furniture — reusable pieces that can go in any room |
| `lib/` | The toolbox — shared utilities and helpers |
| `types/` | The blueprint — defines what everything looks like |

### The `app/` folder (Next.js App Router)

Next.js uses **file-based routing**. The URL path matches the folder structure:

| URL | Folder | What you see |
|-----|--------|-------------|
| `/` | `app/page.tsx` | Home page |
| `/loading` | `app/loading/page.tsx` | Loading page |
| `/history` | `app/history/page.tsx` | History page |
| `/result/abc-123` | `app/result/[jobId]/page.tsx` | Result for job "abc-123" |

The `[jobId]` folder is a **dynamic route** — the `[brackets]` mean "any value works here." This lets a single component handle ALL results, no matter their ID.

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
│    │  • Mode badge: "AI Fact Intelligence" / "Live Market    │      │
│    │    Oracle" / "Price Trust Engine" (animates per mode)   │      │
│    │  • Animated gradient headline                            │      │
│    │  • ModeSwitcher: [Verify] [Financial] [Cart]            │      │
│    │  • Glassmorphism textarea with character counter        │      │
│    │  • Glowing "Analyse Claim" button                        │      │
│    │  • Example buttons (click to auto-fill)                  │      │
│    └─────────────────────────────────────────────────────────┘      │
│                        │                                            │
│                        ▼ Type a claim, click submit                │
│                        │                                            │
└────────────────────────┼────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. LOADING PAGE (/loading?job=abc-123&mode=verify)                 │
│                                                                     │
│    ┌─────────────────────────────────────────────────────────┐      │
│    │ This page polls the backend every 1.5 seconds:           │      │
│    │   GET /result/abc-123?mode=verify                       │      │
│    │                                                         │      │
│    │ You see:                                                 │      │
│    │  • Spinning indigo loading indicator                    │      │
│    │  • Current progress message with icon                    │      │
│    │  • Progress bar (fills up as steps complete)             │      │
│    │  • Step-by-step checklist with pulse-ring dots:          │      │
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
│    │ Displays the verdict, evidence, and analysis             │      │
│    │                                                         │      │
│    │ For VERIFY mode:                                         │      │
│    │  • The original claim in a card                         │      │
│    │  • Animated verdict badge with glow + icon              │      │
│    │  • Confidence pill + source diversity badge              │      │
│    │  • Narrative frame (italic blockquote)                   │      │
│    │  • Summary explanation                                   │      │
│    │  • Agreement meter (supports vs contradicts bar)        │      │
│    │  • Bias heatmap (if biases detected)                    │      │
│    │  • Source list/network toggle                            │      │
│    │    [List View] [Graph View]                              │      │
│    │    Graph View shows nodes as colored circles             │      │
│    │    (green=support, red=contradict, gray=neutral)        │      │
│    │  • Share + download buttons                              │      │
│    │                                                         │      │
│    │ For FINANCIAL mode:                                      │      │
│    │  • Signal badge (Bullish/Bearish/Neutral)               │      │
│    │  • Signal strength gauge (0-100 circular arc)           │      │
│    │  • Price trend + risk level + freshness dot              │      │
│    │  • Price chart (from yFinance data)                     │      │
│    │  • Key factors + risk catalysts                         │      │
│    │  • 30-day prediction (3-column card: bull/base/bear)    │      │
│    │  • Market sources                                        │      │
│    │                                                         │      │
│    │ For CART mode:                                           │      │
│    │  • Product name + fair market range                     │      │
│    │  • Best deal card (star-highlighted)                    │      │
│    │  • Recommendation + price trend + best time to buy      │      │
│    │  • Warnings (red alert boxes)                           │      │
│    │  • Product grid with trust-level color coding:          │      │
│    │      GREEN = trusted, YELLOW = unverified, RED = risky  │      │
│    └─────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Components Explained

### VerdictBadge.tsx
The big animated card that shows the verdict. Each verdict has its own:
- **Color** — emerald (Verified), indigo (Likely True), amber (Mixed), red (Misleading), slate (Unverified)
- **Glow effect** — a colored shadow that makes the card "glow"
- **Icon** — checkmark (✓), diamond (◆), X (✗), question mark (?)
- **Spring animation** — bounces in when the page loads

### BiasHeatmap.tsx
Shows detected manipulation tactics as colored chips. Each chip has:
- The tactic name (e.g., "cherry picking")
- A "Signal Detected" badge
- A tooltip explaining what that tactic means
- Hidden entirely (shows "No signals detected") when array is empty

### SourceGraph.tsx
A visual network of sources drawn with SVG (Scalable Vector Graphics):
- **Nodes** = sources, positioned in a circle
- **Color** = stance (green=supports, red=contradicts, gray=neutral)
- **Size** = credibility tier (bigger = more authoritative)
- **Glow** = subtle color halo around each node
- Toggle between List View and Graph View

### AgreementMeter.tsx
A stacked horizontal bar chart:
- Green section = supporting sources
- Gray section = neutral sources
- Red section = contradicting sources
- Below: numerical breakdown with bold counts

### EvidenceTimeline.tsx
A vertical list of sources sorted by:
1. **Tier** (1 = government/academic first, 4 = blogs last)
2. **Relevance** (most relevant first within each tier)
Each source shows: colored stance stripe, title, author, date, tier badge, summary, and a quote.

### CartProductCard.tsx
Displays a single product listing with:
- Merchant name + trust badge (ShieldCheck = GREEN, AlertCircle = YELLOW, AlertTriangle = RED)
- Product title
- Price (large, bold)
- Counterfeit risk level + condition + stock status
- Deal score (0-100)
- Trust reason explanation
- "Shop on..." link

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
   │  The hook returns:
   │  • progress (e.g., "Searching via Bright Data...")
   │  • icon (emoji for current mode)
   │
   │  Loading page shows progress steps with pulse-ring dots
   │  Progress bar fills (25% → 50% → 75% → 100%)
   │
   ▼
5. Status = "done" → navigate to result page
   │  window.location.href = `/result/${jobId}?mode=verify`
   │
   ▼
6. RESULT PAGE (result/[jobId]/page.tsx)
   │
   │  Fetches result data one more time
   │  Renders the appropriate view based on mode:
   │  • verify → default view (VerdictBadge, AgreementMeter, etc.)
   │  • financial → FinancialResultView
   │  • cart → CartResultView
   │
   ▼
7. User can share or download the result
   │  ShareCard → copies link to clipboard
   │  Download → saves JSON file
```

### Key Concept: Polling vs Waiting

The frontend uses **polling** (asking repeatedly) instead of **waiting** (holding the connection open). This is because AI analysis takes 15-30 seconds, and keeping an HTTP connection open that long is unreliable.

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

This reads `package.json` and downloads all required packages into `node_modules/`.

### Step 2: Configure Environment

Create `.env.local` in the `factguard-frontend/` folder:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This tells the frontend where the backend server is running.

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
| `/` | `app/page.tsx` | Home — mode switcher, input, splash screen |
| `/loading?job=X&mode=Y` | `app/loading/page.tsx` | Polling with progress steps |
| `/result/:jobId` | `app/result/[jobId]/page.tsx` | Result display for all modes |
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

Each verdict in `VERDICT_STYLES` (inside `VerdictBadge.tsx`) has:
- A `glow` color for the shadow
- A gradient `bg` background
- A `border` color
- An `icon` (checkmark, diamond, X, question mark)
- A `text` color
