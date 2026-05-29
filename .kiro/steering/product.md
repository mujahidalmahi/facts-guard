# FactGuard — Product Overview

FactGuard is a multi-track AI intelligence platform that verifies claims, analyzes financial data, monitors security threats, and compares prices. It is built for enterprise GTM, finance, and security teams.

## Four Tracks

| Track | Purpose |
|-------|---------|
| **Verify** | Fact-check competitor claims, headlines, and market intelligence using the VERITAS reasoning protocol |
| **Financial** | Verify earnings claims, M&A rumors, and market trends with AI-powered analysis |
| **Security** | Monitor brand threats, regulatory changes, vendor risks, and disinformation campaigns |
| **Cart** | Trust-scored price comparison across retailers with counterfeit risk detection |

## Core Value Propositions

- Every answer is backed by **live web evidence** with source citations
- **Probabilistic credibility scoring** on all sources (domain authority, stance, freshness)
- **Three-provider AI resilience**: Gemini 2.5 Flash → DeepSeek → Groq + heuristic fallback — no single point of AI failure
- **Six Bright Data integrations** with independent circuit breakers: MCP, SERP, Web Unlocker, Crawl API, Scraping Browser, Residential Proxies
- **Job-based async processing** with Redis progress tracking and frontend polling

## Key Design Principles

- Source fabrication is prohibited — every URL is validated against actual search results
- All Bright Data API calls are tagged with `bright_data_product` for traceability
- MCP Discover runs as Step 0 before any extraction to discover available tools
- Circuit breakers prevent cascading failures across integrations (3 failures → open → 30s cooldown)
