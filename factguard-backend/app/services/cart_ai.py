import re

from app.config import settings
from app.logging_config import get_logger
from app.services.cache import set_progress
from app.utils.parsing import parse_json_response

logger = get_logger("cart_ai")

_PRICE_PATTERN = re.compile(r"\$[\d,]+(?:\.\d{2})?")

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
    for i, listing in enumerate(listings):
        price = f"${listing['price']:.2f}" if listing.get("price") else "N/A"
        rows.append(
            f"{i} | {listing.get('title','')[:60]} | {price} | "
            f"{listing.get('merchant','?')} | {listing.get('url','')[:50]} | "
            f"{listing.get('condition') or 'New'}"
        )
    return "\n".join(rows)


def _regex_fallback(listings: list[dict], product_name: str) -> dict:
    """Last-resort: extract prices from listing titles/snippets via regex."""
    logger.info("Using regex fallback for cart enrichment")
    enriched = []
    for listing in listings:
        price = listing.get("price")
        if not price:
            title = listing.get("title", "")
            snippet = listing.get("snippet", "")
            text = f"{title} {snippet}"
            match = _PRICE_PATTERN.search(text)
            if match:
                try:
                    price = float(match.group(0).replace("$", "").replace(",", ""))
                except (ValueError, AttributeError):
                    price = None
        enriched.append({
            "title": listing.get("title", ""),
            "merchant": listing.get("merchant", "Unknown"),
            "price": price,
            "currency": listing.get("currency", "USD"),
            "url": listing.get("url", ""),
            "trust_level": "YELLOW",
            "deal_score": 0,
            "trust_reason": "Auto-extracted — verify independently",
            "counterfeit_risk": "None",
            "condition": listing.get("condition", "Unknown"),
            "in_stock": True,
        })

    prices = [l["price"] for l in enriched if l["price"]]
    low = min(prices) if prices else 0
    high = max(prices) if prices else 0

    return {
        "product_name": product_name,
        "msrp": None,
        "fair_market_range": {"min": str(low), "max": str(high), "currency": "USD"},
        "best_deal": {"merchant": enriched[0]["merchant"], "price": str(low), "url": enriched[0]["url"], "reason": "Lowest price found"},
        "listings": enriched,
        "analysis": {
            "warnings": ["AI enrichment unavailable — prices extracted via pattern matching"],
            "recommendation": "Verify prices manually; AI analysis was unavailable.",
            "price_trend": "Stable",
            "best_time_to_buy": "Wait",
        },
    }


def _compute_deal_scores(result: dict) -> dict:
    """Overwrite deal_score with a deterministic formula using objective metrics."""
    listings = result.get("listings", [])
    prices = [l.get("price") for l in listings if isinstance(l.get("price"), (int, float))]
    avg_price = sum(prices) / len(prices) if prices else 0

    trust_weights = {"GREEN": 30, "YELLOW": 15, "RED": 0}
    condition_weights = {"New": 20, "Refurbished": 10, "Used": 5, "Unknown": 10}
    risk_penalties = {"High": 25, "Medium": 15, "Low": 5, "None": 0}

    for listing in listings:
        price = listing.get("price")
        trust = trust_weights.get(listing.get("trust_level", "YELLOW"), 15)
        condition = condition_weights.get(listing.get("condition", "Unknown"), 10)
        risk = risk_penalties.get(listing.get("counterfeit_risk", "None"), 0)
        stock = 10 if listing.get("in_stock") else 0

        if price and avg_price > 0:
            ratio = price / avg_price
            if ratio <= 0.85:
                price_score = 25
            elif ratio <= 1.0:
                price_score = 20
            elif ratio <= 1.15:
                price_score = 15
            elif ratio <= 1.3:
                price_score = 10
            else:
                price_score = 5
        else:
            price_score = 10

        score = price_score + trust + condition + stock - risk
        listing["deal_score"] = max(0, min(100, score))

    if prices and listings:
        best = max(listings, key=lambda l: l.get("deal_score", 0))
        result["best_deal"] = {
            "merchant": best.get("merchant", "Unknown"),
            "price": str(best.get("price", "")),
            "url": best.get("url", ""),
            "reason": f"Best risk-adjusted deal (score: {best.get('deal_score', 0)}/100)",
        }

    return result


def _post_process_result(result: dict, listings: list[dict], product_name: str) -> dict:
    """Ensure all required fields exist, then compute deal scores."""
    if not result or "listings" not in result:
        return _regex_fallback(listings, product_name)
    result.setdefault("analysis", {}).setdefault("warnings", [])
    result.setdefault("analysis", {}).setdefault("recommendation", "")
    result.setdefault("analysis", {}).setdefault("price_trend", "Stable")
    result.setdefault("analysis", {}).setdefault("best_time_to_buy", "Wait")
    result.setdefault("product_name", product_name)
    result.setdefault("msrp", None)
    result.setdefault("fair_market_range", {"min": "0", "max": "0", "currency": "USD"})
    return _compute_deal_scores(result)


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

    if job_id:
        await set_progress(job_id, "Running AI price analysis...")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Send top 12 listings for faster AI response
    top_listings = listings[:12]
    listings_table = format_listings_table(top_listings)
    user_prompt = CART_USER_PROMPT.format(
        product_name=product_name, today=today, listings_table=listings_table,
    )

    result = None

    try:
        if settings.AIML_API_ENABLED and settings.aiml_api_keys_list:
            from app.services.aiml_service import call_aiml
            raw = await call_aiml(CART_SYSTEM_PROMPT, user_prompt, model=settings.AIML_CART_MODEL, max_tokens=2048, timeout=45.0)
            result = parse_json_response(raw)
            logger.info("Cart enrichment via AI/ML API")
    except Exception as e:
        logger.warning(f"AIML enrichment failed: {e}")

    if result is None:
        logger.warning("AIML unavailable — using regex extraction")
        result = _regex_fallback(listings, product_name)

    return _post_process_result(result, listings, product_name)
