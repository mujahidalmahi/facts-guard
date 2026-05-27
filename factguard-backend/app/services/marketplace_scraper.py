import asyncio
import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from app.logging_config import get_logger
from app.services.brightdata import scrape_page_full

logger = get_logger("marketplace_scraper")


def _parse_price(text: str | None) -> float | None:
    if not text:
        return None
    m = re.search(r"[\$€£]?\s?([0-9,]+\.\d{2})", text.replace(",", ""))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    m = re.search(r"[\$€£]?\s?([0-9,]+)", text.replace(",", ""))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def _normalise_listing(
    title: str,
    price_text: str | None,
    url: str,
    image: str | None,
    merchant: str,
    rating: str | None = None,
    condition: str | None = None,
) -> dict:
    price = _parse_price(price_text)
    return {
        "title": title.strip() if title else "",
        "price": price,
        "currency": "USD",
        "merchant": merchant,
        "url": url,
        "image": image,
        "condition": condition or "Unknown",
        "rating": rating,
        "model_name": "",
        "source": f"scrape_{merchant.lower().replace(' ', '_')}",
    }


async def amazon_search(product: str, max_results: int = 8) -> list[dict]:
    query = quote(product)
    url = f"https://www.amazon.com/s?k={query}&ref=nb_sb_noss"
    html = await scrape_page_full(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    listings: list[dict] = []

    containers = soup.select("[data-component-type='s-search-result']")
    if not containers:
        containers = soup.select(".s-result-item")

    for item in containers[:max_results]:
        try:
            title_el = item.select_one("h2") or item.select_one(
                "[data-cy='title-recipe'] a"
            )
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            parent_a = title_el.parent if title_el.name != "a" else title_el
            parent_a = item.select_one("a.a-link-normal") if not parent_a or not parent_a.get("href") else parent_a
            href = parent_a.get("href", "")
            full_url = f"https://www.amazon.com{href}" if href.startswith("/") else href

            price_el = item.select_one(
                ".a-price .a-offscreen"
            ) or item.select_one(".a-price-whole")
            price_text = price_el.get_text(strip=True) if price_el else None

            img_el = item.select_one("img.s-image")
            image = img_el.get("src") if img_el else None

            rating_el = item.select_one(
                "i.a-icon-star-mini span.a-icon-alt"
            ) or item.select_one("i.a-icon-star span.a-icon-alt")
            rating = rating_el.get_text(strip=True).split()[0] if rating_el else None

            listings.append(
                _normalise_listing(
                    title=title,
                    price_text=price_text,
                    url=full_url,
                    image=image,
                    merchant="Amazon",
                    rating=rating,
                    condition="New",
                )
            )
        except Exception:
            continue

    logger.info(f"Amazon scrape: {len(listings)} listings")
    return listings


async def search_all_marketplaces(
    product: str, max_per_site: int = 8
) -> list[dict]:
    try:
        return await asyncio.wait_for(
            amazon_search(product, max_per_site), timeout=60
        )
    except (Exception, asyncio.TimeoutError) as e:
        logger.warning(f"Amazon scraper error: {e}")
        return []
