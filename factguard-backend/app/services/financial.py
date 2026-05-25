import random
import yfinance as yf
from app.services.supabase_db import (
    save_financial_result,
    get_saved_financial_result,
)
from datetime import (
    datetime,
    timedelta,
)

from app.logging_config import (
    get_logger,
)

from app.services.cache import (
    set_progress,
)

from app.services.deepseek import (
    deepseek_financial_analysis,
)

logger = get_logger(
    "financial"
)


async def create_financial_query(
    query: str,
    job_id: str,
) -> str:
    return job_id


def _normalize_symbol(
    query: str,
) -> str:
    q = query.strip().upper()

    mapping = {
        "BITCOIN":
            "BTC-USD",
        "BTC":
            "BTC-USD",
        "ETH":
            "ETH-USD",
        "ETHEREUM":
            "ETH-USD",
        "TESLA":
            "TSLA",
        "APPLE":
            "AAPL",
        "NVIDIA":
            "NVDA",
    }

    return mapping.get(
        q,
        q,
    )


def generate_graph_data(
    history,
):
    points = []

    for date, row in (
        history.iterrows()
    ):
        price = row.get(
            "Close"
        )

        if price is None:
            continue

        points.append(
            {
                "date":
                    date.strftime(
                        "%Y-%m-%d"
                    ),
                "price":
                    round(
                        float(
                            price
                        ),
                        2,
                    ),
            }
        )

    return points


async def process_financial_analysis(
    query_id: str,
    query: str,
    job_id: str,
):
    logger.info(
        f"Financial analysis started: {query}"
    )

    await set_progress(
        job_id,
        "Fetching market data...",
    )

    return True


async def get_full_financial_result(
    job_id: str,
):
    saved = (
        await get_saved_financial_result(
            job_id
        )
    )

    if saved:
        logger.info(
            f"Financial cache hit: {job_id}"
        )

        return saved.get(
            "result"
        )

    query = "Bitcoin"

    symbol = (
        _normalize_symbol(
            query
        )
    )

    ticker = yf.Ticker(
        symbol
    )

    history = (
        ticker.history(
            period="1mo"
        )
    )

    if history.empty:
        raise Exception(
            "No market data found"
        )

    graph = (
        generate_graph_data(
            history
        )
    )

    prices = [
        p["price"]
        for p in graph
    ]

    current_price = (
        prices[-1]
    )

    market_context = f"""
Symbol: {symbol}
Current Price: {current_price}
30d High: {max(prices)}
30d Low: {min(prices)}
Trend:
{prices[-7:]}
"""

    ai_analysis = (
        await deepseek_financial_analysis(
            query,
            market_context,
        )
    )

    result = {
        "mode":
            "financial",

        "status":
            "done",

        "jobId":
            job_id,

        "query":
            query,

        "graph_data": {
            "label":
                symbol,

            "unit":
                "USD",

            "current_price":
                current_price,

            "change_24h":
                "Live",

            "change_7d":
                "Live",

            "all_time_high":
                max(prices),

            "data":
                graph,
        },

        "analysis":
            ai_analysis,

        "sources": [
            {
                "title":
                    "Yahoo Finance",

                "url":
                    "https://finance.yahoo.com",

                "credibility":
                    "High",

                "stance":
                    ai_analysis.get(
                        "price_trend",
                        "Neutral",
                    ),

                "summary":
                    "Live financial market data.",

                "date":
                    datetime.now().strftime(
                        "%Y-%m-%d"
                    ),
            }
        ],
    }

    await save_financial_result(
        job_id,
        query,
        result,
    )

    return result