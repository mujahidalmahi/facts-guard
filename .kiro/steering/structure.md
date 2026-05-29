# Project Structure

## Repository Layout

```
news-guard/
├── database/               # SQL schema files (run in Supabase SQL Editor)
│   ├── schema.sql          # Core tables: claims, results, sources
│   ├── schema2.sql         # Migration
│   ├── finance_cart.sql    # Financial + cart tables
│   ├── market.sql          # Market data tables
│   └── threats.sql         # Threats + audit_logs tables
├── factguard-backend/      # Python/FastAPI backend
├── factguard-frontend/     # Next.js/TypeScript frontend
├── docker-compose.yml      # Full-stack local setup
└── splash-demo.html        # Standalone demo page
```

## Backend Structure (`factguard-backend/`)

```
app/
├── main.py                 # FastAPI app factory — registers routers, middleware, CORS
├── config.py               # Typed settings from .env via pydantic-settings
├── schemas.py              # All Pydantic request/response models
├── exceptions.py           # Custom exception types (FactGuardException)
├── dependencies.py         # Shared service singletons (Gemini, Supabase)
├── logging_config.py       # Structured logging + request_id context var
│
├── api/                    # Route handlers (thin — delegate to services)
│   ├── verify.py           # POST /verify, GET /result/{job_id}
│   ├── financial.py        # POST /financial
│   ├── pricing.py          # POST /cart
│   ├── threats.py          # GET+POST /threats/scan, GET /threats/report
│   ├── history.py          # GET /history
│   └── metrics.py          # Prometheus metrics endpoint
│
├── middleware/
│   ├── audit.py            # AuditMiddleware — logs all requests
│   └── ratelimit.py        # RateLimitMiddleware — 30 req/min/IP
│
├── services/               # All business logic lives here
│   ├── gemini.py           # VERITAS AI prompt + Gemini API calls
│   ├── deepseek.py         # DeepSeek financial analysis
│   ├── groq_service.py     # Groq llama-3.3-70b fallback
│   ├── cart_ai.py          # PRICEWATCH AI prompt for price comparison
│   ├── router_ai.py        # Query classifier (Gemini → Groq fallback)
│   ├── brightdata.py       # All 6 Bright Data integrations
│   ├── routing.py          # Circuit breaker + MCP Discover + 3-tier fallback
│   ├── credibility.py      # Composite source credibility scoring
│   ├── threat_monitor.py   # Threat scanning + proxy enrichment
│   ├── financial.py        # Financial analysis orchestration
│   ├── pricing.py          # Price comparison orchestration
│   ├── cache.py            # Redis operations
│   ├── supabase_db.py      # Supabase persistence layer
│   └── db.py               # Low-level DB helpers
│
└── utils/
    ├── search.py           # Web search routing (BrightData → DuckDuckGo)
    ├── duckduckgo.py       # DuckDuckGo free fallback
    ├── parsing.py          # JSON extraction + URL validation
    ├── pricing_parser.py   # Merchant classification
    ├── validators.py       # SQL injection detection
    └── constants.py        # Shared constants

tests/                      # pytest test suite
scripts/
└── seed_demo.py            # Seeds 15+ demo fixtures across all 4 tracks
```

## Frontend Structure (`factguard-frontend/`)

```
app/                        # Next.js App Router pages
├── layout.tsx              # Root layout — Nav, fonts, global providers
├── page.tsx                # Home — 4-mode switcher + claim input
├── globals.css             # Global styles
├── loading/page.tsx        # Animated loading with progress polling
├── history/page.tsx        # Past results list
└── result/[jobId]/
    ├── page.tsx            # Unified result page (all 4 tracks)
    ├── layout.tsx          # OG image metadata
    ├── FinancialResultView.tsx
    ├── CartResultView.tsx
    └── ThreatResultView.tsx

components/                 # Reusable React components
├── Nav.tsx                 # Header with Bright Data circuit-breaker health dots
├── ModeSwitcher.tsx        # 4-mode toggle (Verify / Financial / Security / Cart)
├── VerdictBadge.tsx
├── ConfidencePill.tsx
├── AgreementMeter.tsx
├── EvidenceTimeline.tsx
├── SourceGraph.tsx
├── BiasHeatmap.tsx
├── ThreatResultView.tsx
└── ui/                     # Base UI primitives (badge, button, card, progress, separator)

lib/
├── constants.ts            # Shared frontend constants
├── utils.ts                # Utility functions
└── useJobPolling.ts        # React hook — polls backend every 1.5s for job status

types/
└── index.ts                # TypeScript type definitions (ThreatResult, TrackType, etc.)
```

## Architectural Patterns

- **API routes are thin** — handlers validate input and delegate immediately to `services/`
- **Services are the business logic layer** — all AI calls, scraping, and DB operations live here
- **Circuit breaker per integration** — each Bright Data product has independent failure tracking in `routing.py`
- **Job-based async** — long-running tasks return a `jobId` immediately; frontend polls `/result/{jobId}`
- **AI fallback chain** — every AI call goes Gemini → DeepSeek/Groq → heuristic; never fails silently
- **All Bright Data calls tagged** — every call sets `bright_data_product` field for traceability
- **Pydantic everywhere** — all request/response shapes defined in `schemas.py`; use `field_validator` for input sanitization
- **Settings via `config.py`** — never read `os.environ` directly; always use the `settings` singleton
