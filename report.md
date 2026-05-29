# FactGuard — System Health Report

**Generated:** 2026-05-29  
**Backend:** Python 3.14 / FastAPI  
**Frontend:** Next.js 16 / React 19 / Tailwind v4

---

## 1. Test Suite

| Result | Count |
|--------|-------|
| Passed | 19/19 |
| Failed | 0 |

All backend unit tests pass (constants, pricing parser, validators, verify API).

---

## 2. Section-by-Section Results

### 2.1 Verify — `POST /verify`

**Test claim:** `"Humanoid robots 'the future' of car making, says BMW"`

| Field | Value |
|-------|-------|
| Status | `done` |
| Verdict | `Likely True` |
| Confidence | `Medium` |
| Summary | BBC article + BMW press release confirm humanoid robot pilot at Leipzig plant |
| Supports / Contradicts / Neutral | 3 / 0 / 0 |
| Source Diversity | `Medium` |
| AI Provider | `aiml` (gpt-5-2-chat-latest) |
| Claim in response | ✅ Now included (was missing, fixed) |

**Sources:**

| # | Source | URL | Stance | Credibility |
|---|--------|-----|--------|-------------|
| 1 | BBC News — Humanoid robots 'the future' of car making, says BMW | bbc.com | supports | High |
| 2 | BMW Group press release — deploying humanoid robots in Germany | press.bmwgroup.com | supports | High |
| 3 | Automotive Addicts — BMW Bringing Humanoid Robots to German Factory | automotiveaddicts.com | supports | Medium |

**Assessment:** Strong result — AIML API correctly returned "Likely True" with 3 credible supporting sources. Source credibility scoring works (High for BBC/BMW, Medium for auto blog).

---

### 2.2 Financial — `POST /financial`

**Test query:** `"Dell"`

| Field | Value |
|-------|-------|
| Status | `done` |
| AI Provider | `aiml` (gpt-5-2-chat-latest) |
| Signal | `Neutral` |
| Signal Strength | 42/100 |
| Risk Level | `Medium` |
| Price Trend | `Sideways` |
| Sources Found | 5 |
| graph_data | `null` (no live price feed returned) |

**Sources:** Yahoo Finance, Wikipedia, Dell.com, Instagram, Reddit

**Analysis details:**
- Reported fiscal Q1 revenue up 88% YoY to $43.84B (flagged as unverified, needs corroboration)
- Full-year guidance raised — management confidence signal
- 30-day prediction: base case +3% (50%), bear case -10% (20%), bull case +8% (30%)
- Risk catalysts: AI server margin dilution, hyperscaler order lumpiness, PC softness

**Assessment:** Comprehensive financial analysis with prediction scenarios and risk factors. `graph_data` is null — DELL stock ticker not returning chart data via yfinance in current config (works for crypto tickers like SOL-USD). WSS enrichment polling works correctly (frontend continues polling while `enriching === true`).

---

### 2.3 Cart / Pricing — `POST /cart`

**Test product:** `"ps4"`

| Field | Value |
|-------|-------|
| Status | `done` |
| Product | `ps4` |
| Listings Found | 18 |
| Price Range | $29.75 – $642.00 USD |
| AI Provider | `aiml` (gpt-4o-mini) |
| Cart completion time | ~31s (AIML ~24s + overhead) |

**Sample Listings:**

| Price | Merchant | Product | Deal Score |
|-------|----------|---------|------------|
| $29.75 | Amazon | Wireless Controller (accessory) | — |
| $129.99 | eBay | Sony PlayStation 4 Consoles | 85 |
| $168.99 | Amazon | PS4 500GB Console (Renewed) | — |
| $188.99 | Amazon | PS4 Slim 1TB (Renewed) | — |
| $287.09 | Amazon | PS4 Dual Player Gaming Bundle | 42 |
| $642.00 | Amazon | PlayStation 5 1TB (cross-match) | — |
| $100.00 | YouTube | Deal video (Low trust) | — |
| $129.99 | GameStop | PS4 Consoles & Accessories | — |

**Analysis:**
- Fair Market Range: $29.75 – $642.00
- Price Trend: Stable
- Recommendation: Compare seller reputation before purchasing
- Best Time to Buy: Wait
- Deal Scores: Now showing (index-based matching from AI enrichment)

**Assessment:** 18 listings across Amazon, eBay, Walmart, Best Buy, GameStop, YouTube, Pricecharting, PlayStation. Trust levels and deal scores assigned. Only top 12 listings sent to AI for enrichment (shorter prompt → faster response).

---

## 3. AI Provider Architecture

**Single provider:** AIML API only — all other providers removed.

| Service | File | Model | Timeout |
|---------|------|-------|---------|
| Query Router | `router_ai.py` | `gpt-4.1-nano-2025-04-14` | 60s (default) |
| Verify | `gemini.py` | `gpt-5-2-chat-latest` | 60s (default) |
| Financial | `financial.py` | `gpt-5-2-chat-latest` | 120s |
| Cart | `cart_ai.py` | `gpt-4o-mini` | 45s |
| Credibility | `credibility.py` | `gpt-5-2-chat-latest` | 60s (default) |

**Removed providers:** Gemini, DeepSeek, Groq, Claude — all stripped from every service, including `deepseek.py`, `groq_service.py`, `GeminiService` from `dependencies.py`, `GeminiAPIError` from `exceptions.py`, and all associated config vars.

---

## 4. External Service Health

### 4.1 AIML API (Sole AI Provider)

| Metric | Value |
|--------|-------|
| Keys Configured | **4** |
| Key Status | ✅ **All healthy** (none exhausted) |
| Base URL | `https://api.aimlapi.com/v1` |
| Default Timeout | **60s** (raised from 30s) |
| Retry | 1 retry on transient error, then rotate key |
| Uptime | ✅ Healthy — occasional transient timeouts, retry succeeds |

### 4.2 BrightData

| Service | Status | Notes |
|---------|--------|-------|
| SERP API | ✅ **Healthy** — circuit breaker closed (0 failures) |
| Web Unlocker | ✅ Fallback | Article extraction tier 2 |
| Scraping Browser | ✅ Fallback | Article extraction tier 3 |
| **MCP Discover** | ❌ **Removed** | Was returning 400 (expired token), fully removed from code + config |

### 4.3 Redis (Upstash)

| Metric | Value |
|--------|-------|
| Status | ✅ **Working** — caching, progress tracking operational |
| Cache hit | ✅ Cart product search cached |
| Verify caching | ✅ Result cached after computation |

### 4.4 Supabase

| Metric | Value |
|--------|-------|
| Status | ✅ **Working** |
| DB fix | Removed `credibility` from `_source_toinsert()` — was causing PGRST204 error |

---

## 5. API Endpoints Health

| Method | Path | Status | Notes |
|--------|------|--------|-------|
| `GET` | `/` | ✅ | Root health check |
| `GET` | `/health` | ✅ | Circuit breakers + AIML key status |
| `GET` | `/routing/health` | ✅ | Circuit breaker health |
| `POST` | `/verify` | ✅ **202** | Job created, claim field now included in response |
| `GET` | `/result/{job_id}` | ✅ | Returns analysis + claim text |
| `POST` | `/cart` | ✅ **200** | Price comparison started |
| `GET` | `/price-result/{job_id}` | ✅ | Returns listings + AI enrichment + deal scores |
| `POST` | `/financial` | ✅ **200** | Financial analysis started |
| `GET` | `/financial-result/{job_id}` | ✅ | Returns analysis + WSS enrichment (polling working) |
| `POST` | `/threats/scan` | ⏹️ Not re-tested | Previously verified working |
| `GET` | `/history` | ✅ **200** | History working |
| `GET` | `/metrics` | ✅ | Prometheus endpoint |

---

## 6. Frontend Changes

| Change | File | Detail |
|--------|------|--------|
| Data Sources panel removed | `Sidebar.tsx` | Health status panel removed; Recent History expands to fill space |
| Loading page light mode fix | `loading/page.tsx` | Log text now always light-colored on dark terminal bg regardless of theme |
| Skeleton visible in light mode | `globals.css` | `--muted` changed from `#f1f5f9` → `#cbd5e1` |
| Terminal NO_COLOR | `main.py` | `NO_COLOR=1` set at startup; `--no-use-colors` in `render.yaml` |
| WSS enrichment polling | `page.tsx` | Frontend continues polling while `enriching === true` |
| ANALYSED CLAIM section | `verify.py` | Claim text now injected into verify response (was missing) |

---

## 7. Identified Issues

### 🔴 Critical
None — all critical issues from previous report resolved.

### 🟡 High
1. **No Redis connection timeouts** — potential hang on Redis failure
2. **No `CancelledError` handling** — server restart leaves jobs stuck "processing" forever
3. **Key rotation not thread-safe** — under concurrency, keys get doubled/skipped
4. **yfinance sync calls block event loop** — server timeouts during price fetch
5. **Financial `graph_data: null`** — DELL ticker not returning chart data via yfinance

### 🟢 Medium
6. **No financial advice disclaimer** — regulatory risk
7. **Supabase service role key used everywhere** — RLS bypassed, full DB access
8. **CoinGecko free tier rate limit** — 10-30 calls/min; may throttle under high concurrency

---

## 8. Summary

| Section | Endpoint | Result | AI Quality | Provider |
|---------|----------|--------|------------|----------|
| Verify | `POST /verify` | ✅ Done | ✅ Good (Likely True, 3 sources, claim included) | AIML API (gpt-5-2-chat-latest) |
| Financial | `POST /financial` | ✅ Done | ✅ Good (detailed analysis + 30d prediction) | AIML API (gpt-5-2-chat-latest) |
| Cart | `POST /cart` | ✅ Done | ✅ Good (18 listings, deal scores, ~31s) | AIML API (gpt-4o-mini) |
| Threats | `POST /threats/scan` | ⏹️ Not re-tested | ✅ Previously operational | — |
| AIML API | — | ✅ **Healthy** | 4 keys, none exhausted | Sole AI provider |
| BrightData SERP | — | ✅ **Healthy** | Circuit breaker closed (0 failures) | — |
| MCP Discover | — | ❌ **Removed** | Was erroring 400, fully removed | — |
| Supabase | — | ✅ **Working** | DB save fixed (removed `credibility` field) | — |
| Sidebar Data Sources | — | ❌ **Removed** | Replaced by extended Recent History | — |
| Backend Tests | — | ✅ **19/19** | All passing | — |
