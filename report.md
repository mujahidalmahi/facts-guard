# FactGuard — System Health Report

**Generated:** 2026-05-28 (updated)  
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

**Test claim:** `"claude started opus 4.8 today"`

| Field | Value |
|-------|-------|
| Status | `done` |
| Verdict | `Unverified` |
| Confidence | `Low` |
| Summary | `Could not analyze claim. Please try again.` |
| Supports / Contradicts / Neutral | 0 / 0 / 0 |
| Source Diversity | `Low` |
| Sources Found | 7 |

**Sources:**
| # | Source | URL | Stance | Credibility |
|---|--------|-----|--------|-------------|
| 1 | Introducing Claude Opus 4.7 | anthropic.com | neutral | Medium |
| 2 | Claude Max subscription cancellations | reddit.com | neutral | Medium |
| 3 | Podcast Analytics With Claude Opus 4.8 | videotto.com | neutral | Medium |
| 4 | Claude Opus 4.8 | anthropic.com | neutral | Medium |
| 5 | Claude Sonnet 4.8 Release | nxcode.io | neutral | Medium |
| 6 | Claude Sonnet 4.8 Leak Analysis | wavespeed.ai | neutral | Medium |
| 7 | Claude 4.8 in development | facebook.com | neutral | Medium |

**Assessment:** Sources are highly relevant to the query, but the AI analysis (verdict, stance classification, summary) is crippled by Gemini quota exhaustion. The fallback chain retrieved sources via BrightData SERP but couldn't generate a meaningful analysis.

---

### 2.2 Financial — `POST /financial`

**Test query:** `"solana market price"`

| Field | Value |
|-------|-------|
| Status | `done` |
| AI Provider | `deepseek` |
| graph_data | ✅ **SOL-USD, $82.43, 30 data points** |
| Signal | `Neutral` |
| Summary | `Analysis unavailable.` |
| Sources Found | 5 |

**Chart pipeline:** yfinance → CoinGecko → investing.com (removed, Cloudflare blocked)  
**Live data:** Yes — yfinance and CoinGecko called on every request, prices current at request time  
**Pipeline restructured:** AI analysis runs on SERP snippets (parallel with chart) → save complete result in ~15s → WSS enrichment fires in background with Semaphore(5)

**Assessment:** yfinance now supports SOL-USD and returns 30-day chart data. graph_data contains label, current_price, high/low, and daily price points. The AI analysis falls through to DeepSeek which returns "Analysis unavailable" due to key exhaustion. WSS enrichment improves source text quality but BrightData blocks CoinMarketCap/Binance by policy.

---

### 2.3 Cart / Pricing — `POST /cart`

**Test product:** `"ps5"`

| Field | Value |
|-------|-------|
| Status | `done` |
| Product | `ps5` |
| Listings Found | 18 |
| Price Range | $28.49 – $899.99 USD |

**Sample Listings:**
| Price | Merchant | Product |
|-------|----------|---------|
| $28.49 | Amazon | FYOUNG 3 in 1 Accessories Bundle for PS Portal |
| $290.00 | eBay | Sony PlayStation 5 Consoles |
| $349.99 | Amazon | Meta (accessory) |
| $538.88 | Amazon | Sony Playstation 5 Disc Version |
| $588.00 | Amazon | PS5 Digital Edition + Controller |

**Assessment:** Cart analysis works well — 18 listings scraped with correct prices, merchant names, and trust scoring. The query "ps5" matched PS5 accessories alongside consoles, which is expected behavior.

---

### 2.4 Threats — `POST /threats/scan`

**Test query:** `"Download this free software now"`

| Field | Value |
|-------|-------|
| Status | `done` |
| Threats Detected | 0 |
| Compliance Report | Generated |

**Assessment:** Threat scanning endpoint is operational. For generic test input no threats were found. Requires real malicious URLs/IPs for meaningful validation.

---

## 3. External Service Health

### 3.1 AI Providers — Fallback Chain

| Provider | Model | Keys | Status |
|----------|-------|------|--------|
| Gemini | `gemini-2.5-flash` | 3 | ❌ **429 RESOURCE_EXHAUSTED** (all 3 keys, free tier limit 20 req/day each) |
| DeepSeek | `deepseek/deepseek-chat-v3-0324` (via OpenRouter) | 3 | ❌ **All 3 keys exhausted** — non-JSON responses ("Expecting value: line 1 column 1") |
| Groq | `mixtral-8x7b-32768` | 1 | ✅ **Available** — last resort, not triggered yet |

**Fallback chain:** Gemini → DeepSeek → Groq  
**Key rotation:** Fast failover — 5s first-timeout then full timeout (10-30s) per provider  
**Issue:** All 6 API keys (3 Gemini + 3 DeepSeek) are exhausted. The entire AI analysis chain is effectively down. Only Groq remains available as last-resort heuristic fallback.

### 3.2 BrightData SERP API

| Metric | Value |
|--------|-------|
| Provider | BrightData |
| SERP Zone | `serp_api1` |
| Circuit Breaker | ✅ **Closed** (0 failures) |
| Status | ✅ **Healthy** — all search requests succeeded |

### 3.3 BrightData WSS Browser

| Metric | Value |
|--------|-------|
| Endpoint | `wss://brd.superproxy.io:9222` |
| Browser Zone | `scraping_browser1` |
| Browser Timeout | 45s |
| Concurrency | `Semaphore(5)` (bumped from 2) |
| URLs per enrichment | 3 (reduced from 5) |
| Cache TTL | 3600s |
| Pipeline role | **Background enrichment only** — runs after main result saved |
| Status | ⚠️ **Configured** — BrightData policy blocks CoinMarketCap, Binance, and similar crypto/trading sites |
| investing.com | ❌ **Cloudflare-protected** — returns 403 challenge on direct HTTP API; not tested via WSS |

### 3.4 DeepSeek (OpenRouter)

| Metric | Value |
|--------|-------|
| Keys Configured | **3** |
| Status | ❌ **All 3 keys exhausted** — returns non-JSON responses; see §3.1 |
| Caveat | Even when working, returns `Analysis unavailable.` as a successful string (not an error), confusing fallback chain logging |

### 3.5 Groq

| Metric | Value |
|--------|-------|
| Key Configured | Yes (56 chars) |
| Status | ✅ **Available** — last resort in fallback chain, not triggered in these tests |

### 3.6 Redis (Upstash)

| Metric | Value |
|--------|-------|
| URL | Configured (TLS) |
| Status | ✅ **Working** — caching, progress tracking, rate limiting operational |
| Notice | No `socket_connect_timeout` / `socket_timeout` set — potential hang risk |

### 3.7 Supabase

| Metric | Value |
|--------|-------|
| URL | Configured |
| Service Role Key | Configured |
| Status | ✅ **Working** — history, audit logs operational |
| Notice | Service role key used directly (bypasses RLS) — any SQL injection grants full DB access |

---

## 4. Infrastructure

### 4.1 Backend

| Component | Status |
|-----------|--------|
| FastAPI server | ✅ Boots cleanly |
| All routers registered | ✅ (verify, financial, cart, threats, history, metrics) |
| Rate limiting (30 req/min/IP via Redis) | ✅ |
| Request audit logging | ✅ |
| CORS configured | ✅ |
| Prometheus `/metrics` | ✅ |
| Tests (19/19) | ✅ |

### 4.2 Frontend

| Component | Status |
|-----------|--------|
| Next.js build | ✅ **0 errors, 0 warnings** |
| TypeScript strict | ✅ |
| Tailwind v4 | ✅ |
| Routes | `/`, `/history`, `/loading`, `/result/[jobId]` |
| API polling with exponential backoff | ✅ |
| Error boundaries | ✅ |

### 4.3 Configuration

| File | Status |
|------|--------|
| `.env` | ⚠️ **15+ API keys committed to repo** — security incident |
| `.gitignore` | ❌ `.env` not listed — keys tracked in git history |
| `docker-compose.yml` | ✅ |
| `Dockerfile` (backend) | ✅ Multi-stage Python 3.12-slim |
| `Dockerfile` (frontend) | ✅ Multi-stage Node 20-slim |
| Vercel config | ✅ |
| Render config | ✅ |

---

## 5. Identified Issues

### 🔴 Critical
1. **15+ live API keys in `.env` committed to repo** — rotate all immediately (Gemini, DeepSeek/Groq, Supabase SERVICE_ROLE, BrightData, Upstash Redis)
2. **`.env` not in `.gitignore`** — keys remain tracked in git history
3. **All 6 AI keys exhausted** — 3 Gemini (429 quota) + 3 DeepSeek (non-JSON). Full fallback chain broken. Only Groq remains.

### 🟡 High
4. **`credibility.py` Gemini call missing system prompt** — Gemini returns random JSON
5. **No Redis connection timeouts** — potential hang on Redis failure
6. **No `CancelledError` handling** — server restart leaves jobs stuck "processing" forever
7. **Key rotation not thread-safe** — under concurrency, keys get doubled/skipped
8. **yfinance sync calls block event loop** — server timeouts during price fetch
9. **investing.com Cloudflare block** — `_try_investing_chart()` removed after discovering 403 Cloudflare challenge on direct HTTP API. Not tested via WSS.

### 🟢 Medium
10. **Financial "Analysis unavailable" return is a success string** — confuses fallback chain logging
11. **No financial advice disclaimer** — regulatory risk
12. **Stance classification always "neutral"** — AI analysis not functioning
13. **Supabase service role key used everywhere** — RLS bypassed, full DB access
14. **CoinGecko free tier rate limit** — 10-30 calls/min; may throttle under high concurrency
15. **BrightData policy blocks crypto sites** — CoinMarketCap, Binance not accessible via WSS; limits crypto source enrichment

---

## 6. Summary

| Section | Endpoint | Result | AI Quality |
|---------|----------|--------|------------|
| Verify | `POST /verify` | ✅ Done | ❌ Weak (Gemini, DeepSeek both exhausted) |
| Financial | `POST /financial` | ✅ Done | ❌ AI unavailable; **graph_data ok** (yfinance → CoinGecko, live) |
| Cart | `POST /cart` | ✅ Done | ✅ Good (18 listings) |
| Threats | `POST /threats/scan` | ✅ Done | ✅ Operational |
| Gemini API | — | ❌ 429 Quota | All 3 keys exhausted |
| DeepSeek (OpenRouter) | — | ❌ Non-JSON | All 3 keys exhausted |
| BrightData SERP | — | ✅ Healthy | Circuit breaker closed |
| WSS Browser | — | ⚠️ Semi-blocked | BrightData blocks crypto/trading sites; Semaphore(5) |
| investing.com | — | ❌ Cloudflare | Replaced with yfinance global indices (20+ added) |
| Backend Tests | — | ✅ 19/19 | All passing |
| Frontend Build | — | ✅ 0 errors | Clean build |
