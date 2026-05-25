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
from app.utils.search import (
    search_claim,
)

logger = get_logger(
    "pricing"
)

CACHE_PREFIX = (
    "factguard:pricing:"
)


def _listing_to_insert(
    l: dict,
    query_id: str,
) -> dict:
    return {
        "query_id":
            query_id,

        "title":
            l.get(
                "title",
                "",
            ),

        "price":
            l.get(
                "price"
            ),

        "currency":
            l.get(
                "currency",
                "USD",
            ),

        "merchant":
            l.get(
                "merchant",
                "",
            ),

        "url":
            l.get(
                "url",
                "",
            ),

        "image":
            l.get(
                "image"
            ),

        "condition":
            l.get(
                "condition"
            ),

        "model_name":
            l.get(
                "model_name"
            ),
    }


def _listing_to_response(
    l: dict,
) -> dict:
    trust = (
        get_trust_level(
            l.get(
                "merchant",
                "",
            )
        )
        .lower()
    )

    trust_signal = (
        "green"
        if trust == "high"
        else (
            "yellow"
            if trust
            == "medium"
            else "red"
        )
    )

    return {
        "platform":
            l.get(
                "merchant",
                "Unknown",
            ),

        "title":
            l.get(
                "title",
                "",
            ),

        "url":
            l.get(
                "url",
                "",
            ),

        "snippet":
            l.get(
                "title",
                "",
            ),

        "trust_signal":
            trust_signal,
    }


async def create_query(
    product_name: str,
    job_id: str,
) -> str:
    try:
        result = await insert(
            "product_queries",
            {
                "product_name":
                    product_name,

                "job_id":
                    job_id,

                "status":
                    STATUS_PROCESSING,
            },
        )

        query_id = (
            result.data[0]["id"]
        )

        logger.debug(
            f"Price query created: "
            f"{query_id}"
        )

        return query_id

    except Exception as e:
        logger.error(
            f"Failed to create "
            f"price query: "
            f"{type(e).__name__}: {e}"
        )
        raise


async def save_listings(
    query_id: str,
    listings: list[dict],
):
    if not listings:
        logger.debug(
            "No listings to save"
        )
        return

    try:
        rows = [
            _listing_to_insert(
                l,
                query_id,
            )
            for l in listings
        ]

        await insert(
            "product_listings",
            rows,
        )

        logger.debug(
            f"Saved "
            f"{len(rows)} "
            f"listings"
        )

    except Exception as e:
        logger.error(
            f"Failed to save "
            f"listings: "
            f"{type(e).__name__}: {e}"
        )


async def update_query_status(
    query_id: str,
    status: str,
):
    try:
        await update(
            "product_queries",
            {
                "status":
                    status
            },
            "id",
            query_id,
        )

        logger.debug(
            f"Query "
            f"{query_id} "
            f"status updated "
            f"to: {status}"
        )

    except Exception as e:
        logger.error(
            f"Failed to update "
            f"query status: "
            f"{type(e).__name__}: {e}"
        )


async def get_full_price_result(
    job_id: str,
) -> dict | None:

    saved = (
        await get_saved_cart_result(
            job_id
        )
    )

    if saved:
        logger.info(
            f"Cart cache hit: "
            f"{job_id}"
        )

        return saved.get(
            "result"
        )

    try:
        query_response = (
            await select(
                "product_queries",
                eq_field=
                    "job_id",
                eq_value=
                    job_id,
                maybe_single=
                    True,
            )
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

    if (
        not query_response
        or not query_response.data
    ):
        logger.warning(
            f"Price query "
            f"not found for "
            f"job_id: {job_id}"
        )

        return None

    query = (
        query_response.data
    )

    query_id = query.get(
        "id"
    )

    if not query_id:
        logger.warning(
            f"Price query "
            f"has no id for "
            f"job_id: {job_id}"
        )

        return None

    status = query.get(
        "status",
        STATUS_PROCESSING,
    )

    if (
        status
        == STATUS_PROCESSING
    ):
        return {
            "status":
                STATUS_PROCESSING,

            "jobId":
                query.get(
                    "job_id",
                    job_id,
                ),

            "product":
                query.get(
                    "product_name",
                    "",
                ),

            "createdAt":
                query.get(
                    "created_at"
                ),
        }

    try:
        listings_response = (
            await select(
                "product_listings",
                eq_field=
                    "query_id",
                eq_value=
                    query_id,
            )
        )

        listings_data = (
            listings_response.data
            or []
        )

    except Exception as e:
        logger.error(
            f"Failed to query "
            f"listings for "
            f"query {query_id}: "
            f"{type(e).__name__}: "
            f"{e}"
        )

        listings_data = []

    result = {
        "mode":
            "cart",

        "status":
            status,

        "jobId":
            query.get(
                "job_id",
                job_id,
            ),

        "product":
            query.get(
                "product_name",
                "",
            ),

        "createdAt":
            query.get(
                "created_at"
            ),

        "listings": [
            _listing_to_response(
                l
            )
            for l in listings_data
        ],

        "analysis": {
            "best_deal": {
                "platform":
                    listings_data[
                        0
                    ].get(
                        "merchant",
                        "Unknown",
                    )
                if listings_data
                else "Unknown",

                "price":
                    str(
                        listings_data[
                            0
                        ].get(
                            "price",
                            "N/A",
                        )
                    )
                if listings_data
                else "N/A",

                "why":
                    "Lowest trusted result",
            },

            "verdict":
                f"Found "
                f"{len(listings_data)} "
                f"listings",

            "price_range": {
                "low":
                    str(
                        min(
                            [
                                x.get(
                                    "price"
                                )
                                for x in listings_data
                                if x.get(
                                    "price"
                                )
                                is not None
                            ],
                            default=0,
                        )
                    ),

                "high":
                    str(
                        max(
                            [
                                x.get(
                                    "price"
                                )
                                for x in listings_data
                                if x.get(
                                    "price"
                                )
                                is not None
                            ],
                            default=0,
                        )
                    ),
            },

            "recommendation":
                "Compare seller "
                "reputation "
                "before purchasing.",

            "warnings":
                [],

            "market_average":
                "Dynamic",
        },
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
    search_query = (
        f"{product_name} "
        f"price buy online"
    )

    results = (
        await search_claim(
            search_query,
            max_results=10,
        )
    )

    seen_urls = set()
    raw_listings = []

    for r in results:
        url = r.get(
            "url",
            ""
        )

        if url in seen_urls:
            continue

        seen_urls.add(
            url
        )

        snippet = r.get(
            "snippet",
            "",
        )

        title = r.get(
            "title",
            "",
        )

        price = (
            extract_price(
                snippet
            )
            or extract_price(
                title
            )
        )

        merchant = (
            classify_merchant(
                url
            )
        )

        model_name = (
            extract_model_name(
                title
            )
        )

        raw_listings.append(
            {
                "title":
                    title,

                "price":
                    price,

                "currency":
                    "USD",

                "merchant":
                    merchant,

                "url":
                    url,

                "image":
                    None,

                "condition":
                    None,

                "model_name":
                    model_name,
            }
        )

    sorted_listings = (
        sort_listings(
            raw_listings
        )
    )

    variants = (
        cluster_listings(
            sorted_listings
        )
    )

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

        search_hash = (
            compute_claim_hash(
                product_name
            )
        )

        cached = (
            await get_cached_analysis(
                f"{CACHE_PREFIX}{search_hash}"
            )
        )

        if cached:
            logger.info(
                f"Cache hit "
                f"for product "
                f"search: "
                f"{product_name}"
            )

            listings = cached.get(
                "listings",
                [],
            )

            variants = cached.get(
                "variants",
                [],
            )

        else:
            logger.info(
                f"Cache miss, "
                f"searching "
                f"prices for: "
                f"{product_name}"
            )

            await set_progress(
                job_id,
                PRICING_PROGRESS_ANALYZING,
            )

            listings, variants = (
                await fetch_product_prices(
                    product_name
                )
            )

            await set_cached_analysis(
                f"{CACHE_PREFIX}{search_hash}",
                {
                    "listings":
                        listings,

                    "variants":
                        variants,
                },
            )

        await set_progress(
            job_id,
            PRICING_PROGRESS_SAVING,
        )

        await save_listings(
            query_id,
            listings,
        )

        await update(
            "product_queries",
            {
                "status":
                    STATUS_DONE,

                "variants_data":
                    variants,
            },
            "id",
            query_id,
        )

        logger.info(
            f"Price check "
            f"{query_id} "
            f"completed with "
            f"{len(listings)} "
            f"listings"
        )

    except Exception as e:
        logger.error(
            f"Failed to "
            f"process price "
            f"check "
            f"{query_id}: "
            f"{str(e)}"
        )

        await set_progress(
            job_id,
            "Failed",
        )

        await update_query_status(
            query_id,
            STATUS_ERROR,
        )