#!/usr/bin/env python3
"""
Pre-seeds Redis with 15+ fixture results for demo safety across all 3 tracks.
Run once before the demo: python scripts/seed_demo.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.services.cache import set_cached_analysis, compute_claim_hash

# ── Track 1: GTM Intelligence ──────────────────────────────────
VERIFY_FIXTURES = [
  {
    "claim": "The Earth is flat",
    "mode": "verify",
    "track": "gtm",
    "verdict": "Unverified",
    "confidence": "High",
    "supports": 0,
    "contradicts": 12,
    "neutral": 2,
    "summary": "Overwhelming scientific consensus confirms Earth is an oblate spheroid.",
    "narrative_frame": "Flat Earth claims persist in fringe communities despite centuries of evidence.",
    "source_diversity": "High",
    "bias_signals": ["cherry_picking"],
    "sources": [
      {"title": "NASA Earth Facts", "url": "https://nasa.gov", "author": "NASA", "date": "2026-01-15", "stance": "supports", "credibility": "High", "tier": 1, "relevance": 10, "summary": "NASA confirms Earth is an oblate spheroid.", "quote": "Earth is an oblate spheroid."},
      {"title": "National Geographic", "url": "https://nationalgeographic.com", "author": "NatGeo", "date": "2025-11-20", "stance": "contradicts", "credibility": "High", "tier": 1, "relevance": 9, "summary": "Flat Earth debunked by satellite imagery.", "quote": "Satellite images confirm Earth's curvature."},
    ],
  },
  {
    "claim": "WHO confirmed ivermectin cures COVID-19",
    "mode": "verify",
    "track": "gtm",
    "verdict": "Likely Misleading",
    "confidence": "High",
    "supports": 1,
    "contradicts": 9,
    "neutral": 2,
    "summary": "WHO recommends against ivermectin for COVID-19 outside clinical trials. Major health authorities and peer-reviewed studies found no benefit.",
    "narrative_frame": "Selective citation of a single preprint amplifies a disproven treatment claim.",
    "source_diversity": "Medium",
    "bias_signals": ["cherry_picking", "misleading_statistics"],
    "sources": [
      {"title": "WHO Statement on Ivermectin", "url": "https://who.int", "author": "WHO", "date": "2025-09-10", "stance": "contradicts", "credibility": "High", "tier": 1, "relevance": 10, "summary": "WHO recommends against ivermectin for COVID-19.", "quote": "Current evidence does not support ivermectin for COVID-19."},
    ],
  },
  {
    "claim": "Vaccines cause autism",
    "mode": "verify",
    "track": "gtm",
    "verdict": "Unverified",
    "confidence": "High",
    "supports": 0,
    "contradicts": 15,
    "neutral": 1,
    "summary": "Decades of large-scale studies involving millions of children have found no link between vaccines and autism. The original 1998 study was retracted for fraud.",
    "narrative_frame": "Long-debunked claim resurfaces through social media amplification.",
    "source_diversity": "High",
    "bias_signals": ["unverified_anecdote", "appeal_to_authority"],
    "sources": [
      {"title": "CDC Vaccine Safety", "url": "https://cdc.gov", "author": "CDC", "date": "2026-02-01", "stance": "contradicts", "credibility": "High", "tier": 1, "relevance": 10, "summary": "CDC confirms no link between vaccines and autism.", "quote": "Vaccines do not cause autism."},
      {"title": "Lancet Retraction", "url": "https://thelancet.com", "author": "The Lancet", "date": "2010-02-02", "stance": "contradicts", "credibility": "High", "tier": 1, "relevance": 9, "summary": "Original study linking vaccines to autism was retracted.", "quote": "Retracted due to fraudulent data."},
    ],
  },
  {
    "claim": "Apple will release a foldable iPhone in 2026",
    "mode": "verify",
    "track": "gtm",
    "verdict": "Mixed Evidence",
    "confidence": "Medium",
    "supports": 4,
    "contradicts": 3,
    "neutral": 2,
    "summary": "Multiple supply chain analysts predict a foldable iPhone in 2026 or 2027, but Apple has not confirmed. Leaked patents and display orders support the claim.",
    "narrative_frame": "Supply chain leaks drive speculation ahead of official announcement.",
    "source_diversity": "Medium",
    "bias_signals": ["emotional_language"],
    "sources": [
      {"title": "Kuo: Foldable iPhone in 2026", "url": "https://macrumors.com", "author": "MacRumors", "date": "2026-03-10", "stance": "supports", "credibility": "Medium", "tier": 2, "relevance": 9, "summary": "Analyst Kuo predicts foldable iPhone in 2026.", "quote": "Supply chain checks indicate foldable iPhone in 2026."},
    ],
  },
  {
    "claim": "Tesla delivered 2 million vehicles in 2025",
    "mode": "verify",
    "track": "gtm",
    "verdict": "Likely True",
    "confidence": "Medium",
    "supports": 5,
    "contradicts": 1,
    "neutral": 1,
    "summary": "Tesla reported 1.81M deliveries in 2024 and is on track for ~2M in 2025 based on quarterly growth trends and production capacity expansion.",
    "narrative_frame": "Growth narrative supported by production numbers and delivery trends.",
    "source_diversity": "Medium",
    "bias_signals": [],
    "sources": [
      {"title": "Tesla Q4 2025 Delivery Report", "url": "https://ir.tesla.com", "author": "Tesla IR", "date": "2026-01-02", "stance": "supports", "credibility": "High", "tier": 1, "relevance": 10, "summary": "Tesla reports record deliveries.", "quote": "468,000 vehicles delivered in Q4."},
    ],
  },
]

# ── Track 2: Finance & Risk ────────────────────────────────────
FINANCIAL_FIXTURES = [
  {
    "query": "Major cloud provider enters market at 40% cheaper",
    "mode": "financial",
    "track": "finance",
    "verdict": "LIKELY TRUE",
    "confidence": "Medium",
    "summary": "Multiple analyst reports confirm aggressive pricing from a new cloud entrant, undercutting AWS/Azure by 35-45% on compute instances.",
    "graph_data": {
      "label": "Cloud Pricing Trend",
      "unit": "USD/hr",
      "current_price": 0.042,
      "change_24h": "-2.1%",
      "change_7d": "-8.3%",
      "data": [{"date": f"2026-04-{d:02d}", "price": 0.048 - d * 0.0005} for d in range(1, 25)],
    },
    "analysis": {
      "signal": "WATCH",
      "signal_strength": "Moderate",
      "price_trend": "Downward",
      "key_factors": ["New entrant pricing", "AWS price match", "Enterprise migration costs"],
      "risk_level": "Medium",
      "prediction_30d": "Pricing pressure expected to persist as new entrant gains market share.",
      "confidence": "Medium",
      "summary": "Cloud pricing war intensifying with new entrant at 40% below market.",
    },
    "sources": [
      {"title": "Cloud Pricing Analysis Q2 2026", "url": "https://gartner.com", "stance": "supports", "credibility": "High"},
    ],
  },
  {
    "query": "Competitor raised Series C at $100M valuation",
    "mode": "financial",
    "track": "finance",
    "verdict": "VERIFIED",
    "confidence": "High",
    "summary": "Crunchbase, TechCrunch, and PitchBook confirm competitor raised $100M Series C at $800M valuation led by Sequoia.",
    "graph_data": {
      "label": "Competitor Funding Rounds",
      "unit": "USD M",
      "current_price": 100,
      "change_24h": "0%",
      "change_7d": "0%",
      "data": [{"date": "2024-06-01", "price": 20}, {"date": "2025-01-15", "price": 45}, {"date": "2026-05-01", "price": 100}],
    },
    "analysis": {
      "signal": "VERIFIED",
      "signal_strength": "Strong",
      "price_trend": "Upward",
      "key_factors": ["Series C close", "Sequoia lead", "SaaS growth metrics"],
      "risk_level": "Low",
      "prediction_30d": "Competitor will likely increase sales spend following raise.",
      "confidence": "High",
      "summary": "Competitor Series C confirmed at $100M.",
    },
    "sources": [
      {"title": "TechCrunch: Competitor Raises $100M", "url": "https://techcrunch.com", "stance": "supports", "credibility": "High"},
    ],
  },
  {
    "query": "S&P 500 outlook 2026",
    "mode": "financial",
    "track": "finance",
    "verdict": "HOLD",
    "confidence": "Low",
    "summary": "S&P 500 facing resistance at 5600 amid rate uncertainty and trade tensions.",
    "graph_data": {
      "label": "S&P 500",
      "unit": "points",
      "current_price": 5520,
      "change_24h": "-0.3%",
      "change_7d": "-1.2%",
      "data": [{"date": f"2026-04-{d:02d}", "price": 5550 - d * 1.5} for d in range(1, 25)],
    },
    "analysis": {
      "signal": "HOLD",
      "signal_strength": "Weak",
      "price_trend": "Bearish",
      "key_factors": ["Fed rate decision", "Earnings season", "Geopolitical risk"],
      "risk_level": "Medium",
      "prediction_30d": "Sideways to slightly lower.",
      "confidence": "Low",
      "summary": "Market uncertainty persists.",
    },
  },
  {
    "query": "Dollar to BDT rate forecast",
    "mode": "financial",
    "track": "finance",
    "verdict": "WATCH",
    "confidence": "Medium",
    "summary": "USD/BDT hovering near 110 with central bank intervention expected.",
    "graph_data": {
      "label": "USD/BDT",
      "unit": "BDT",
      "current_price": 109.8,
      "change_24h": "+0.2%",
      "change_7d": "-0.5%",
      "data": [{"date": f"2026-04-{d:02d}", "price": 109.0 + d * 0.05} for d in range(1, 25)],
    },
    "analysis": {
      "signal": "WATCH",
      "signal_strength": "Moderate",
      "price_trend": "Sideways",
      "key_factors": ["Fed policy", "BD exports", "Remittance inflow"],
      "risk_level": "Medium",
      "prediction_30d": "Stable range expected with possible central bank intervention.",
      "confidence": "Medium",
      "summary": "USD/BDT stable near 110 with central bank watching.",
    },
  },
  {
    "query": "Bitcoin price analysis April 2026",
    "mode": "financial",
    "track": "finance",
    "verdict": "BUY",
    "confidence": "Medium",
    "summary": "BTC showing bullish consolidation above $90k support with strong ETF inflows.",
    "graph_data": {
      "label": "BTC/USD",
      "unit": "USD",
      "current_price": 94500,
      "change_24h": "+3.1%",
      "change_7d": "+8.7%",
      "data": [{"date": f"2026-04-{d:02d}", "price": 92000 + d * 100} for d in range(1, 25)],
    },
    "analysis": {
      "signal": "BUY",
      "signal_strength": "Strong",
      "price_trend": "Bullish",
      "key_factors": ["ETF inflows", "Halving effect", "Institutional adoption"],
      "risk_level": "High",
      "prediction_30d": "Potential rally toward $105k if $90k support holds.",
      "confidence": "Medium",
      "summary": "Bitcoin bullish momentum intact with strong ETF demand.",
    },
  },
]

# ── Track 3: Security & Compliance ──────────────────────────────
THREAT_FIXTURES = [
  {
    "query": "Data breach at key vendor reported",
    "mode": "threat",
    "track": "security",
    "threat_type": "vendor",
    "severity": "high",
    "title": "Supply chain vendor reports data breach affecting customer data",
    "description": "A major third-party logistics vendor reported a breach exposing customer names, addresses, and payment data. Incident discovered during routine security audit.",
    "source_url": "https://krebsonsecurity.com",
    "confidence": 0.85,
    "alert_status": "new",
    "sources": [
      {"title": "KrebsOnSecurity: Vendor Breach", "url": "https://krebsonsecurity.com", "stance": "supports", "credibility": "High"},
    ],
  },
  {
    "query": "New GDPR compliance requirement for AI",
    "mode": "threat",
    "track": "security",
    "threat_type": "regulatory",
    "severity": "medium",
    "title": "EU proposes new AI compliance rules for enterprise systems",
    "description": "European Commission proposes updated GDPR guidelines specifically for AI-powered data processing. Enterprises using LLMs for customer data will need additional compliance measures.",
    "source_url": "https://europa.eu",
    "confidence": 0.75,
    "alert_status": "new",
    "sources": [
      {"title": "EU AI Act Updates", "url": "https://europa.eu", "stance": "supports", "credibility": "High"},
    ],
  },
  {
    "query": "Disinformation campaign targeting financial sector",
    "mode": "threat",
    "track": "security",
    "threat_type": "disinformation",
    "severity": "critical",
    "title": "Coordinated disinformation campaign targets banking sector stocks",
    "description": "Analysis reveals a coordinated network of bots and fake news sites spreading false information about major bank solvency. Campaign appears designed to trigger a short-selling attack.",
    "source_url": "https://reuters.com",
    "confidence": 0.92,
    "alert_status": "new",
    "sources": [
      {"title": "Reuters: Disinformation Campaign", "url": "https://reuters.com", "stance": "supports", "credibility": "High"},
    ],
  },
  {
    "query": "Brand impersonation scams increasing",
    "mode": "threat",
    "track": "security",
    "threat_type": "brand",
    "severity": "medium",
    "title": "Brand impersonation scams up 340% in Q1 2026",
    "description": "Security researchers report surge in phishing campaigns impersonating major tech brands. Attackers using AI-generated websites and emails to steal credentials.",
    "source_url": "https://bleepingcomputer.com",
    "confidence": 0.80,
    "alert_status": "new",
    "sources": [
      {"title": "BleepingComputer: Scam Surge", "url": "https://bleepingcomputer.com", "stance": "supports", "credibility": "Medium"},
    ],
  },
  {
    "query": "Zero-day vulnerability in enterprise VPN",
    "mode": "threat",
    "track": "security",
    "threat_type": "brand",
    "severity": "critical",
    "title": "Critical zero-day vulnerability disclosed in enterprise VPN solution",
    "description": "CVE-2026-1234: Remote code execution vulnerability affecting all versions of popular enterprise VPN. Proof of concept published. Exploitation observed in the wild targeting Fortune 500 companies.",
    "source_url": "https://cve.mitre.org",
    "confidence": 0.95,
    "alert_status": "new",
    "sources": [
      {"title": "CVE Database Entry", "url": "https://cve.mitre.org", "stance": "supports", "credibility": "High"},
    ],
  },
]

CART_FIXTURES = [
  {
    "product": "iPhone 16 Pro",
    "mode": "cart",
    "track": "cart",
    "verdict": "Buy Now",
    "confidence": "Medium",
    "summary": "Best price on Amazon. Avoid third-party sellers on eBay.",
    "listings": [
      {"platform": "Amazon", "title": "Apple iPhone 16 Pro 256GB", "url": "https://amazon.com/...", "snippet": "$999 — Ships Prime", "trust_signal": "green"},
      {"platform": "eBay", "title": "iPhone 16 Pro SEALED", "url": "https://ebay.com/...", "snippet": "$879 — Unverified seller", "trust_signal": "red"},
    ],
    "analysis": {
      "best_deal": {"platform": "Amazon", "price": "$999", "why": "Prime + warranty"},
      "verdict": "Buy Now",
      "price_range": {"low": "$879", "high": "$1099"},
      "recommendation": "Purchase from Amazon for warranty protection.",
      "warnings": ["eBay listing has no seller rating — avoid"],
      "market_average": "$999",
    },
  },
  {
    "product": "MacBook Air M4",
    "mode": "cart",
    "track": "cart",
    "verdict": "Shop Around",
    "confidence": "High",
    "summary": "Price varies significantly across retailers. Best Buy offers the best deal.",
    "listings": [
      {"platform": "Best Buy", "title": "MacBook Air M4 13-inch 16GB RAM", "url": "https://bestbuy.com/...", "snippet": "$1099 — In stock", "trust_signal": "green"},
      {"platform": "Amazon", "title": "MacBook Air M4 13-inch", "url": "https://amazon.com/...", "snippet": "$1149 — Ships in 1 week", "trust_signal": "yellow"},
      {"platform": "Walmart", "title": "MacBook Air M4 (2026)", "url": "https://walmart.com/...", "snippet": "$1079 — Marketplace seller", "trust_signal": "yellow"},
    ],
    "analysis": {
      "best_deal": {"platform": "Best Buy", "price": "$1099", "why": "Best price from authorized retailer"},
      "verdict": "Shop Around",
      "price_range": {"low": "$1079", "high": "$1299"},
      "recommendation": "Buy from Best Buy for the best combination of price and reliability.",
      "warnings": ["Walmart listing is a third-party marketplace seller"],
      "market_average": "$1149",
    },
  },
  {
    "product": "Sony WH-1000XM6",
    "mode": "cart",
    "track": "cart",
    "verdict": "Buy Now",
    "confidence": "High",
    "summary": "Strong consensus: Amazon has the best price on these headphones.",
    "listings": [
      {"platform": "Amazon", "title": "Sony WH-1000XM6 Wireless Noise Cancelling", "url": "https://amazon.com/...", "snippet": "$349 — Free shipping", "trust_signal": "green"},
      {"platform": "Target", "title": "Sony WH-1000XM6", "url": "https://target.com/...", "snippet": "$379 — Member price", "trust_signal": "green"},
    ],
    "analysis": {
      "best_deal": {"platform": "Amazon", "price": "$349", "why": "Lowest price with free shipping"},
      "verdict": "Buy Now",
      "price_range": {"low": "$349", "high": "$399"},
      "recommendation": "Amazon has the best price. No reason to wait.",
      "warnings": [],
      "market_average": "$369",
    },
  },
]


async def seed():
    print("Seeding demo fixtures into Redis...")

    for f in VERIFY_FIXTURES:
        key = compute_claim_hash(f["claim"])
        await set_cached_analysis(key, f)
        print(f"  [GTM] verify: {f['claim'][:50]}")

    for f in FINANCIAL_FIXTURES:
        key = compute_claim_hash(f'fin:{f["query"]}')
        await set_cached_analysis(key, f)
        print(f"  [FINANCE] financial: {f['query'][:50]}")

    for f in THREAT_FIXTURES:
        key = compute_claim_hash(f'threat:{f["query"]}')
        await set_cached_analysis(key, f)
        print(f"  [SECURITY] threat: {f['query'][:50]}")

    for f in CART_FIXTURES:
        key = compute_claim_hash(f'cart:{f["product"]}')
        await set_cached_analysis(key, f)
        print(f"  [CART] cart: {f['product']}")

    print(f"\nDone. Total: {len(VERIFY_FIXTURES) + len(FINANCIAL_FIXTURES) + len(THREAT_FIXTURES) + len(CART_FIXTURES)} fixtures seeded.")


if __name__ == "__main__":
    asyncio.run(seed())
