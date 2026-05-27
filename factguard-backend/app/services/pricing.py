import asyncio

from app.logging_config import get_logger
from app.services.supabase_db import (
    save_cart_result,
    get_saved_cart_result,
)
from app.services.db import (
    insert,
    select,
    update,
)
from datetime import datetime, timezone

from app.utils.constants import (
    PRICING_PROGRESS_ANALYZING,
    PRICING_PROGRESS_SAVING,
    PRICING_PROGRESS_SEARCHING,
    STATUS_DONE,
    STATUS_ERROR,
    STATUS_PROCESSING,
)
from app.services.cache import (
    compute_claim_hash,
    get_cached_analysis,
    push_claim_to_history,
    set_cached_analysis,
    set_progress,
)
from app.services.cart_ai import (
    enrich_cart_listings,
)
from app.services.marketplace_scraper import (
    search_all_marketplaces,
)
from app.utils.pricing_parser import (
    classify_merchant,
    cluster_listings,
    extract_model_name,
    extract_price,
    get_trust_level,
    sort_listings,
)
from app.utils.search import (
    search_claim,
)

logger = get_logger("pricing")

CACHE_PREFIX = "factguard:pricing:"


def _listing_to_insert(
    listing: dict,
    query_id: str,
) -> dict:
    return {
        "query_id": query_id,
        "title": listing.get(
            "title",
            "",
        ),
        "price": listing.get("price"),
        "currency": listing.get(
            "currency",
            "USD",
        ),
        "merchant": listing.get(
            "merchant",
            "",
        ),
        "url": listing.get(
            "url",
            "",
        ),
        "image": listing.get("image"),
        "condition": listing.get("condition"),
        "model_name": listing.get("model_name"),
    }


def _build_ai_analysis(
    ai_enrichment: dict | None,
    listings_data: list[dict],
) -> dict:
    prices = []
    for x in listings_data:
        p = x.get("price")
        if p is not None:
            try:
                prices.append(float(p))
            except (ValueError, TypeError):
                pass
    low_price = str(min(prices, default=0.0))
    high_price = str(max(prices, default=0.0))
    product_name = listings_data[0].get("title", "") if listings_data else ""

    if not ai_enrichment:
        return {
            "product_name": product_name,
            "msrp": None,
            "fair_market_range": {
                "min": low_price,
                "max": high_price,
                "currency": "USD",
            },
            "best_deal": {
                "merchant": (
                    listings_data[0].get("merchant", "Unknown") if listings_data else "Unknown"
                ),
                "price": f"${low_price}" if listings_data else "N/A",
                "url": listings_data[0].get("url", "") if listings_data else "",
                "reason": "Lowest trusted result",
            },
            "analysis": {
                "warnings": [],
                "recommendation": "Compare seller reputation before purchasing.",
                "price_trend": "Stable",
                "best_time_to_buy": "Wait",
            },
        }

    best_deal = ai_enrichment.get("best_deal")
    return {
        "product_name": product_name,
        "msrp": None,
        "fair_market_range": {
            "min": str((ai_enrichment.get("price_range") or {}).get("low", low_price)),
            "max": str((ai_enrichment.get("price_range") or {}).get("high", high_price)),
            "currency": "USD",
        },
        "best_deal": {
            "merchant": best_deal.get("platform", "Unknown") if best_deal else "Unknown",
            "price": f"${best_deal.get('price', low_price)}" if best_deal else f"${low_price}",
            "url": best_deal.get("url", "") if best_deal else "",
            "reason": best_deal.get("why", "") if best_deal else "",
        },
        "analysis": {
            "warnings": ai_enrichment.get(
                "warnings",
                [],
            ),
            "recommendation": ai_enrichment.get(
                "recommendation",
                "Compare seller reputation before purchasing.",
            ),
            "price_trend": "Stable",
            "best_time_to_buy": "Wait",
        },
    }


def _listing_to_response(
    listing: dict,
) -> dict:
    trust = get_trust_level(
        listing.get(
            "merchant",
            "",
        )
    ).lower()

    trust_signal = "green" if trust == "high" else ("yellow" if trust == "medium" else "red")

    return {
        "title": listing.get(
            "title",
            "",
        ),
        "merchant": listing.get(
            "merchant",
            "Unknown",
        ),
        "price": listing.get("price"),
        "currency": listing.get(
            "currency",
            "USD",
        ),
        "url": listing.get(
            "url",
            "",
        ),
        "trust_level": trust_signal.upper(),
        "deal_score": 0,
        "trust_reason": "",
        "counterfeit_risk": "None",
        "condition": listing.get(
            "condition",
            "Unknown",
        ),
        "in_stock": True,
        "image": listing.get("image"),
        "rating": listing.get("rating"),
    }


async def create_query(
    product_name: str,
    job_id: str,
) -> str:
    try:
        result = await insert(
            "product_queries",
            {
                "product_name": product_name,
                "job_id": job_id,
                "status": STATUS_PROCESSING,
            },
        )

        if not result or not result.data:
            raise ValueError("No data returned from database")
        query_id = result.data[0]["id"]

        logger.debug(f"Price query created: " f"{query_id}")

        return query_id

    except Exception as e:
        logger.error(f"Failed to create " f"price query: " f"{type(e).__name__}: {e}")
        raise


async def save_listings(
    query_id: str,
    listings: list[dict],
):
    if not listings:
        logger.debug("No listings to save")
        return

    try:
        rows = [
            _listing_to_insert(
                listing,
                query_id,
            )
            for listing in listings
        ]

        await insert(
            "product_listings",
            rows,
        )

        logger.debug(f"Saved " f"{len(rows)} " f"listings")

    except Exception as e:
        logger.error(f"Failed to save " f"listings: " f"{type(e).__name__}: {e}")


async def update_query_status(
    query_id: str,
    status: str,
):
    try:
        await update(
            "product_queries",
            {"status": status},
            "id",
            query_id,
        )

        logger.debug(f"Query " f"{query_id} " f"status updated " f"to: {status}")

    except Exception as e:
        logger.error(f"Failed to update " f"query status: " f"{type(e).__name__}: {e}")


async def get_full_price_result(
    job_id: str,
) -> dict | None:

    saved = await get_saved_cart_result(job_id)

    if saved:
        logger.info(f"Cart cache hit: " f"{job_id}")

        return saved.get("result")

    try:
        query_response = await select(
            "product_queries",
            eq_field="job_id",
            eq_value=job_id,
            maybe_single=True,
        )

    except Exception as e:
        logger.error(
            f"Failed to query "
            f"price result "
            f"for job_id "
            f"{job_id}: "
            f"{type(e).__name__}: "
            f"{e}"
        )

        return None

    if not query_response or not query_response.data:
        logger.warning(f"Price query " f"not found for " f"job_id: {job_id}")

        return None

    query = query_response.data

    query_id = query.get("id")

    if not query_id:
        logger.warning(f"Price query " f"has no id for " f"job_id: {job_id}")

        return None

    status = query.get(
        "status",
        STATUS_PROCESSING,
    )

    if status == STATUS_PROCESSING:
        return {
            "status": STATUS_PROCESSING,
            "jobId": query.get(
                "job_id",
                job_id,
            ),
            "product": query.get(
                "product_name",
                "",
            ),
            "createdAt": query.get("created_at"),
        }

    try:
        listings_response = await select(
            "product_listings",
            eq_field="query_id",
            eq_value=query_id,
        )

        listings_data = listings_response.data or []

    except Exception as e:
        logger.error(
            f"Failed to query "
            f"listings for "
            f"query {query_id}: "
            f"{type(e).__name__}: "
            f"{e}"
        )

        listings_data = []

    ai_enrichment = query.get("ai_enrichment")

    analysis = _build_ai_analysis(
        ai_enrichment,
        listings_data,
    )

    result = {
        "mode": "cart",
        "status": status,
        "jobId": query.get(
            "job_id",
            job_id,
        ),
        "product": query.get(
            "product_name",
            "",
        ),
        "createdAt": query.get("created_at"),
        "listings": [_listing_to_response(listing) for listing in listings_data],
        "analysis": analysis,
    }

    await save_cart_result(
        job_id,
        query.get(
            "product_name",
            "",
        ),
        result,
    )

    return result


async def fetch_product_prices(
    product_name: str,
) -> tuple[
    list[dict],
    list[dict],
]:
    search_query = f"{product_name} " f"price buy online"

    marketplace_task = asyncio.wait_for(
        search_all_marketplaces(product_name), timeout=40
    )
    serp_task = asyncio.wait_for(
        search_claim(search_query, max_results=10), timeout=40
    )

    (marketplace_results, serp_results) = await asyncio.gather(
        marketplace_task, serp_task, return_exceptions=True
    )

    if isinstance(marketplace_results, Exception):
        logger.warning(f"Marketplace search failed: {marketplace_results}")
        marketplace_results = []
    if isinstance(serp_results, Exception):
        logger.warning(f"SERP search failed: {serp_results}")
        serp_results = []

    seen_urls: set[str] = set()
    raw_listings: list[dict] = []

    for listing in marketplace_results:
        url = listing.get("url", "")
        key = url.rstrip("/").lower()
        if key and key not in seen_urls:
            seen_urls.add(key)
            if listing.get("merchant") in ("Unknown", ""):
                listing["merchant"] = classify_merchant(url)
            raw_listings.append(listing)

    for r in serp_results:
        url = r.get("url", "")
        key = url.rstrip("/").lower()
        if key and key not in seen_urls:
            seen_urls.add(key)

            snippet = r.get("snippet", "")
            title = r.get("title", "")

            price = extract_price(snippet) or extract_price(title)
            merchant = classify_merchant(url)
            model_name = extract_model_name(title)

            raw_listings.append(
                {
                    "title": title,
                    "price": price,
                    "currency": "USD",
                    "merchant": merchant,
                    "url": url,
                    "image": None,
                    "condition": None,
                    "model_name": model_name,
                    "rating": None,
                    "source": r.get("source", "serp"),
                }
            )

    sorted_listings = sort_listings(raw_listings)

    variants = cluster_listings(sorted_listings)

    return (
        sorted_listings,
        variants,
    )


async def process_price_check(
    query_id: str,
    product_name: str,
    job_id: str,
):
    try:
        await set_progress(
            job_id,
            PRICING_PROGRESS_SEARCHING,
        )

        search_hash = compute_claim_hash(product_name)

        cached = await get_cached_analysis(f"{CACHE_PREFIX}{search_hash}")

        if cached:
            logger.info(f"Cache hit " f"for product " f"search: " f"{product_name}")

            listings = cached.get(
                "listings",
                [],
            )

            variants = cached.get(
                "variants",
                [],
            )

        else:
            logger.info(f"Cache miss, " f"searching " f"prices for: " f"{product_name}")

            await set_progress(
                job_id,
                PRICING_PROGRESS_ANALYZING,
            )

            listings, variants = await fetch_product_prices(product_name)

            await set_cached_analysis(
                f"{CACHE_PREFIX}{search_hash}",
                {
                    "listings": listings,
                    "variants": variants,
                },
            )

        try:
            ai_enrichment = await enrich_cart_listings(
                product_name,
                listings,
                job_id,
            )
        except Exception as e:
            logger.warning(f"AI enrichment failed (non-fatal): {e}")
            ai_enrichment = None

        await set_progress(
            job_id,
            PRICING_PROGRESS_SAVING,
        )

        await save_listings(
            query_id,
            listings,
        )

        try:
            await update(
                "product_queries",
                {
                    "status": STATUS_DONE,
                    "variants_data": variants,
                    "ai_enrichment": ai_enrichment,
                },
                "id",
                query_id,
            )
        except Exception as e:
            logger.warning(f"status update failed (non-fatal): {e}")

        try:
            await push_claim_to_history(
                {
                    "jobId": job_id,
                    "claim": f"[CART] {product_name}",
                    "status": STATUS_DONE,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception as e:
            logger.warning(f"push_claim_to_history failed (non-fatal): {e}")

        logger.info(
            f"Price check " f"{query_id} " f"completed with " f"{len(listings)} " f"listings"
        )

    except Exception as e:
        logger.error(f"Failed to " f"process price " f"check " f"{query_id}: " f"{str(e)}")

        await set_progress(
            job_id,
            "Failed",
        )

        await update_query_status(
            query_id,
            STATUS_ERROR,
        )
