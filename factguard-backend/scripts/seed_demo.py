#!/usr/bin/env python3
"""
Pre-seeds Redis with fixture results for demo safety.
Run once before the demo: python scripts/seed_demo.py
"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.services.cache import set_cached_analysis, compute_claim_hash

VERIFY_FIXTURES = [
  {
    "claim": "The Earth is flat",
    "mode": "verify",
    "verdict": "Unverified",
    "confidence": "High",
    "supports": 0,
    "contradicts": 12,
    "neutral": 2,
    "summary": "Overwhelming scientific consensus confirms Earth is an oblate spheroid. All major space agencies and peer-reviewed studies confirm this.",
    "sources": [
      {
        "title": "NASA Earth Facts",
        "url": "https://nasa.gov",
        "stance": "Contradicts",
        "credibility": "High",
        "snippet": "...",
      }
    ],
  },
  {
    "claim": "WHO confirmed ivermectin cures COVID-19",
    "mode": "verify",
    "verdict": "Likely Misleading",
    "confidence": "High",
    "supports": 1,
    "contradicts": 9,
    "neutral": 2,
    "summary": "WHO recommends against ivermectin for COVID-19 outside clinical trials.",
    "sources": [],
  },
  {
    "claim": "Vaccines cause autism",
    "mode": "verify",
    "verdict": "Unverified",
    "confidence": "High",
    "supports": 0,
    "contradicts": 15,
    "neutral": 1,
    "summary": "Decades of large-scale studies have found no link between vaccines and autism. The original 1998 study was retracted due to fraud.",
    "sources": [
      {
        "title": "CDC Vaccine Safety",
        "url": "https://cdc.gov",
        "stance": "Contradicts",
        "credibility": "High",
        "snippet": "...",
      }
    ],
  },
]

FINANCIAL_FIXTURES = [
  {
    "query": "Dollar to BDT rate",
    "mode": "financial",
    "verdict": "WATCH",
    "confidence": "Medium",
    "summary": "USD/BDT hovering near 110.",
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
      "key_factors": ["Fed policy", "BD exports"],
      "risk_level": "Medium",
      "prediction_30d": "Stable range expected.",
      "confidence": "Medium",
      "summary": "USD/BDT stable near 110.",
    },
    "sources": [],
  },
  {
    "query": "Bitcoin price analysis",
    "mode": "financial",
    "verdict": "BUY",
    "confidence": "Medium",
    "summary": "BTC showing bullish consolidation above $90k support.",
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
      "summary": "Bitcoin bullish momentum intact.",
    },
    "sources": [],
  },
  {
    "query": "S&P 500 outlook",
    "mode": "financial",
    "verdict": "HOLD",
    "confidence": "Low",
    "summary": "S&P 500 facing resistance at 5600 amid rate uncertainty.",
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
      "prediction_30d": "Sideways to slightly lower — wait for clearer signal.",
      "confidence": "Low",
      "summary": "Market uncertainty persists.",
    },
    "sources": [],
  },
]

CART_FIXTURES = [
  {
    "product": "iPhone 16 Pro",
    "mode": "cart",
    "verdict": "Buy Now",
    "confidence": "Medium",
    "summary": "Best price on Amazon. Avoid third-party sellers on eBay.",
    "listings": [
      {
        "platform": "Amazon",
        "title": "Apple iPhone 16 Pro 256GB",
        "url": "https://amazon.com/...",
        "snippet": "$999 — Ships Prime",
        "trust_signal": "green",
      },
      {
        "platform": "eBay",
        "title": "iPhone 16 Pro SEALED",
        "url": "https://ebay.com/...",
        "snippet": "$879 — Unverified seller",
        "trust_signal": "red",
      },
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
    "verdict": "Shop Around",
    "confidence": "High",
    "summary": "Price varies significantly across retailers. Best Buy offers the best deal.",
    "listings": [
      {
        "platform": "Best Buy",
        "title": "MacBook Air M4 13-inch 16GB RAM",
        "url": "https://bestbuy.com/...",
        "snippet": "$1099 — In stock",
        "trust_signal": "green",
      },
      {
        "platform": "Amazon",
        "title": "MacBook Air M4 13-inch",
        "url": "https://amazon.com/...",
        "snippet": "$1149 — Ships in 1 week",
        "trust_signal": "yellow",
      },
      {
        "platform": "Walmart",
        "title": "MacBook Air M4 (2026)",
        "url": "https://walmart.com/...",
        "snippet": "$1079 — Marketplace seller",
        "trust_signal": "yellow",
      },
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
    "verdict": "Buy Now",
    "confidence": "High",
    "summary": "Strong consensus: Amazon has the best price on these headphones.",
    "listings": [
      {
        "platform": "Amazon",
        "title": "Sony WH-1000XM6 Wireless Noise Cancelling",
        "url": "https://amazon.com/...",
        "snippet": "$349 — Free shipping",
        "trust_signal": "green",
      },
      {
        "platform": "Target",
        "title": "Sony WH-1000XM6",
        "url": "https://target.com/...",
        "snippet": "$379 — Member price",
        "trust_signal": "green",
      },
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
        print(f"  verify: {f['claim'][:40]}")

    for f in FINANCIAL_FIXTURES:
        key = compute_claim_hash(f'fin:{f["query"]}')
        await set_cached_analysis(key, f)
        print(f"  financial: {f['query']}")

    for f in CART_FIXTURES:
        key = compute_claim_hash(f'cart:{f["product"]}')
        await set_cached_analysis(key, f)
        print(f"  cart: {f['product']}")

    print("Done. Run this before every demo.")


if __name__ == "__main__":
    asyncio.run(seed())
