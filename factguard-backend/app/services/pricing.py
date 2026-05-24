from app.logging_config import get_logger
from app.services.db import insert, select, update
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
    set_cached_analysis,
    set_progress,
)
from app.utils.pricing_parser import (
    classify_merchant,
    cluster_listings,
    extract_model_name,
    extract_price,
    get_trust_level,
    sort_listings,
)
from app.utils.search import search_claim

logger = get_logger("pricing")

CACHE_PREFIX = "factguard:pricing:"


def _listing_to_insert(l: dict, query_id: str) -> dict:
    return {
        "query_id": query_id,
        "title": l.get("title", ""),
        "price": l.get("price"),
        "currency": l.get("currency", "USD"),
        "merchant": l.get("merchant", ""),
        "url": l.get("url", ""),
        "image": l.get("image"),
        "condition": l.get("condition"),
        "model_name": l.get("model_name"),
    }


def _listing_to_response(l: any) -> dict:
    return {
        "title": l.get("title", ""),
        "price": l.get("price"),
        "currency": l.get("currency", "USD"),
        "merchant": l.get("merchant", ""),
        "trustLevel": get_trust_level(l.get("merchant", "")),
        "url": l.get("url", ""),
        "image": l.get("image"),
        "condition": l.get("condition"),
    }


async def create_query(product_name: str, job_id: str) -> str:
    try:
        result = await insert("product_queries", {
            "product_name": product_name,
            "job_id": job_id,
            "status": STATUS_PROCESSING,
        })
        query_id = result.data[0]["id"]
        logger.debug(f"Price query created: {query_id}")
        return query_id
    except Exception as e:
        logger.error(f"Failed to create price query: {type(e).__name__}: {e}")
        raise


async def save_listings(query_id: str, listings: list[dict]):
    if not listings:
        logger.debug("No listings to save")
        return
    try:
        rows = [_listing_to_insert(l, query_id) for l in listings]
        await insert("product_listings", rows)
        logger.debug(f"Saved {len(rows)} listings")
    except Exception as e:
        logger.error(f"Failed to save listings: {type(e).__name__}: {e}")


async def update_query_status(query_id: str, status: str):
    try:
        await update("product_queries", {"status": status}, "id", query_id)
        logger.debug(f"Query {query_id} status updated to: {status}")
    except Exception as e:
        logger.error(f"Failed to update query status: {type(e).__name__}: {e}")


async def get_full_price_result(job_id: str) -> dict | None:
    try:
        query_response = await select(
            "product_queries", eq_field="job_id", eq_value=job_id, maybe_single=True
        )
    except Exception as e:
        logger.error(f"Failed to query price result for job_id {job_id}: {type(e).__name__}: {e}")
        return None

    if not query_response or not query_response.data:
        logger.warning(f"Price query not found for job_id: {job_id}")
        return None

    query = query_response.data
    query_id = query.get("id")
    if not query_id:
        logger.warning(f"Price query has no id for job_id: {job_id}")
        return None

    status = query.get("status", STATUS_PROCESSING)

    if status == STATUS_PROCESSING:
        return {
            "status": STATUS_PROCESSING,
            "jobId": query.get("job_id", job_id),
            "product": query.get("product_name", ""),
            "createdAt": query.get("created_at"),
        }

    try:
        listings_response = await select(
            "product_listings", eq_field="query_id", eq_value=query_id
        )
        listings_data = listings_response.data or []
    except Exception as e:
        logger.error(f"Failed to query listings for query {query_id}: {type(e).__name__}: {e}")
        listings_data = []

    variants = query.get("variants_data")
    if isinstance(variants, list):
        for v in variants:
            if "priceRange" not in v:
                v["priceRange"] = "Price unavailable"

    return {
        "status": status,
        "jobId": query.get("job_id", job_id),
        "product": query.get("product_name", ""),
        "createdAt": query.get("created_at"),
        "listings": [_listing_to_response(l) for l in listings_data],
        "variants": variants if isinstance(variants, list) else [],
    }


async def fetch_product_prices(product_name: str) -> tuple[list[dict], list[dict]]:
    search_query = f"{product_name} price buy online"
    results = await search_claim(search_query, max_results=10)

    seen_urls: set[str] = set()
    raw_listings: list[dict] = []

    for r in results:
        url = r.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        snippet = r.get("snippet", "")
        title = r.get("title", "")

        price = extract_price(snippet) or extract_price(title)
        merchant = classify_merchant(url)
        model_name = extract_model_name(title)

        raw_listings.append({
            "title": title,
            "price": price,
            "currency": "USD",
            "merchant": merchant,
            "url": url,
            "image": None,
            "condition": None,
            "model_name": model_name,
        })

    sorted_listings = sort_listings(raw_listings)
    variants = cluster_listings(sorted_listings)

    return sorted_listings, variants


async def process_price_check(query_id: str, product_name: str, job_id: str):
    try:
        await set_progress(job_id, PRICING_PROGRESS_SEARCHING)

        search_hash = compute_claim_hash(product_name)
        cached = await get_cached_analysis(f"{CACHE_PREFIX}{search_hash}")
        if cached:
            logger.info(f"Cache hit for product search: {product_name}")
            listings = cached.get("listings", [])
            variants = cached.get("variants", [])
        else:
            logger.info(f"Cache miss, searching prices for: {product_name}")
            await set_progress(job_id, PRICING_PROGRESS_ANALYZING)
            listings, variants = await fetch_product_prices(product_name)
            await set_cached_analysis(f"{CACHE_PREFIX}{search_hash}", {
                "listings": listings,
                "variants": variants,
            })

        await set_progress(job_id, PRICING_PROGRESS_SAVING)
        await save_listings(query_id, listings)
        await update(
            "product_queries",
            {"status": STATUS_DONE, "variants_data": variants},
            "id",
            query_id,
        )

        logger.info(f"Price check {query_id} completed with {len(listings)} listings")
    except Exception as e:
        logger.error(f"Failed to process price check {query_id}: {str(e)}")
        await set_progress(job_id, "Failed")
        await update_query_status(query_id, STATUS_ERROR)
