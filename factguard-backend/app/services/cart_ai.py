import json

from app.logging_config import get_logger
from app.services.cache import set_progress

logger = get_logger("cart_ai")

CART_SYSTEM_PROMPT = """You are PRICEWATCH, FactGuard's consumer protection AI.
You analyze product listings from across the web to protect buyers from
counterfeit goods, grey-market sellers, inflated prices, and deceptive practices.

## YOUR TRUST FRAMEWORK
GREEN — Verified authorized retailer. Price within ±10% of MSRP. In-stock.
YELLOW — Unverified seller OR price deviation 10-30% OR unclear shipping terms.
RED — Price too low (>30% under MSRP = counterfeit risk) OR unknown seller
  OR missing return policy OR customer complaints flagged.

## ANALYSIS TASKS
1. MARKET PRICE INTELLIGENCE: What is the fair market price range for this product?
2. DEAL QUALITY SCORING: Score each listing 0-100 for deal quality.
3. TRUST ASSESSMENT: Classify each merchant (Green/Yellow/Red).
4. COUNTERFEIT SIGNALS: Flag any listings that show counterfeit risk patterns.
5. BEST DEAL: Identify the single best risk-adjusted deal.

## OUTPUT CONTRACT — VALID JSON ONLY
{
  "product_name": "Canonical product name",
  "msrp": "Official MSRP if known, else null",
  "fair_market_range": {"min": "...", "max": "...", "currency": "USD"},
  "best_deal": {
    "merchant": "...", "price": "...", "url": "...",
    "reason": "Why this is the best risk-adjusted deal"
  },
  "listings": [
    {
      "title": "...", "merchant": "...", "price": <float>, "currency": "USD",
      "url": "...", "trust_level": "GREEN|YELLOW|RED",
      "deal_score": <int 0-100>,
      "trust_reason": "One-sentence explanation of trust rating",
      "counterfeit_risk": "High|Medium|Low|None",
      "condition": "New|Refurbished|Used|Unknown",
      "in_stock": true
    }
  ],
  "analysis": {
    "warnings": ["specific warning 1", ...],
    "recommendation": "2-3 sentence buying recommendation with specific advice.",
    "price_trend": "Rising|Stable|Dropping",
    "best_time_to_buy": "Now|Wait|Urgent"
  }
}"""

CART_USER_PROMPT = """Product searched: {product_name}
Today: {today}

## LISTINGS
Index | Title | Price (USD) | Merchant | URL | Condition
{listings_table}

Analyse these listings and return the JSON enrichment."""


def format_listings_table(listings: list[dict]) -> str:
    rows = []
    for i, l in enumerate(listings):
        price = f"${l['price']:.2f}" if l.get('price') else 'N/A'
        rows.append(
            f"{i} | {l.get('title','')[:60]} | {price} | "
            f"{l.get('merchant','?')} | {l.get('url','')[:50]} | "
            f"{l.get('condition') or 'New'}"
        )
    return '\n'.join(rows)


async def enrich_cart_listings(
    product_name: str,
    listings: list[dict],
    job_id: str | None = None,
) -> dict:
    if not listings:
        return {
            "best_deal": None,
            "price_range": None,
            "market_average": None,
            "warnings": [],
            "variant_notes": None,
            "recommendation": "No listings found to analyse.",
            "verdict": "No trustworthy listings",
        }

    from datetime import datetime, timezone
    from app.dependencies import get_gemini_service

    if job_id:
        await set_progress(
            job_id,
            "Running AI price analysis...",
        )

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    listings_table = format_listings_table(listings)
    user_prompt = CART_USER_PROMPT.format(
        product_name=product_name,
        today=today,
        listings_table=listings_table,
    )

    try:
        gemini_service = get_gemini_service()
        model = gemini_service.get_model()

        import asyncio
        response = await asyncio.wait_for(
            asyncio.to_thread(
                model.generate_content,
                user_prompt,
            ),
            timeout=15.0,
        )

        text = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(text)
        logger.info(
            f"Cart AI enrichment completed: "
            f"{result.get('verdict', 'unknown')}"
        )
        return result

    except Exception as e:
        logger.warning(
            f"Cart AI enrichment failed: {e}"
        )
        return {
            "best_deal": None,
            "price_range": None,
            "market_average": None,
            "warnings": [],
            "variant_notes": None,
            "recommendation": (
                f"Found {len(listings)} listings. "
                "Compare prices manually."
            ),
            "verdict": "Best deal found",
        }
