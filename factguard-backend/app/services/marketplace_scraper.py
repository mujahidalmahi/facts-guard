import asyncio
import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from app.logging_config import get_logger
from app.services.brightdata import scrape_page_full
from app.utils.pricing_parser import classify_merchant

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
            title_el = item.select_one("h2 a.a-link-normal") or item.select_one(
                "h2 a"
            )
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            full_url = f"https://www.amazon.com{href}" if href.startswith("/") else href

            price_el = item.select_one(
                ".a-price .a-offscreen"
            ) or item.select_one(".a-price-whole")
            price_text = price_el.get_text(strip=True) if price_el else None

            img_el = item.select_one("img.s-image")
            image = img_el.get("src") if img_el else None

            rating_el = item.select_one(
                "i.a-icon-star-small span.a-icon-alt"
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


async def ebay_search(product: str, max_results: int = 8) -> list[dict]:
    query = quote(product)
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_sop=15"
    html = await scrape_page_full(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    listings: list[dict] = []

    items = soup.select(".s-item") or soup.select(".srp-results .s-item")
    if not items:
        items = soup.select("li.brwrvr-item")

    for item in items[:max_results]:
        try:
            title_el = item.select_one(
                ".s-item__title span"
            ) or item.select_one(".s-item__title")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title or title == "Shop on eBay":
                continue

            link_el = item.select_one(".s-item__link") or item.select_one("a")
            href = link_el.get("href", "") if link_el else ""
            full_url = href.split("?")[0] if href else ""

            price_el = item.select_one(
                ".s-item__price"
            ) or item.select_one(".s-item__details .s-item__price")
            price_text = price_el.get_text(strip=True) if price_el else None

            img_el = item.select_one(".s-item__image img") or item.select_one("img")
            image = img_el.get("src") if img_el else None

            cond_el = item.select_one(
                ".s-item__itemDetails .s-item__condition"
            ) or item.select_one(".s-item__subtitle")
            condition = cond_el.get_text(strip=True) if cond_el else None

            listings.append(
                _normalise_listing(
                    title=title,
                    price_text=price_text,
                    url=full_url,
                    image=image,
                    merchant="eBay",
                    condition=condition,
                )
            )
        except Exception:
            continue

    logger.info(f"eBay scrape: {len(listings)} listings")
    return listings


async def walmart_search(product: str, max_results: int = 8) -> list[dict]:
    query = quote(product)
    url = f"https://www.walmart.com/search?q={query}"
    html = await scrape_page_full(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    listings: list[dict] = []

    items = soup.select("[data-item-id]") or soup.select(
        ".search-result-gridview-item"
    ) or soup.select("div[data-testid='itemTile']")

    for item in items[:max_results]:
        try:
            title_el = item.select_one("a[link-identifier='item-title']") or item.select_one(
                "a span")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue

            link_el = item.select_one("a[link-identifier='item-title']") or item.select_one("a")
            href = link_el.get("href", "") if link_el else ""
            full_url = (
                f"https://www.walmart.com{href}" if href.startswith("/") else href
            )

            price_el = item.select_one(
                "[data-automation-id='product-price']"
            ) or item.select_one(".price-group")
            price_text = price_el.get_text(strip=True) if price_el else None

            img_el = item.select_one("img") or item.select_one("[data-testid='productTileImage']")
            image = img_el.get("src") if img_el else None

            listings.append(
                _normalise_listing(
                    title=title,
                    price_text=price_text,
                    url=full_url,
                    image=image,
                    merchant="Walmart",
                    condition="New",
                )
            )
        except Exception:
            continue

    logger.info(f"Walmart scrape: {len(listings)} listings")
    return listings


async def bestbuy_search(product: str, max_results: int = 8) -> list[dict]:
    query = quote(product)
    url = f"https://www.bestbuy.com/site/searchpage.jsp?st={query}"
    html = await scrape_page_full(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    listings: list[dict] = []

    items = soup.select("[data-testid='list-view'] li") or soup.select(
        ".shop-sku-list-item"
    ) or soup.select(".list-item")

    for item in items[:max_results]:
        try:
            title_el = item.select_one("h4 a") or item.select_one("h4") or item.select_one(
                ".sku-header a"
            )
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue

            link_el = item.select_one("a") if item.select_one("h4 a") else title_el
            href = link_el.get("href", "") if link_el else ""
            full_url = (
                f"https://www.bestbuy.com{href}" if href.startswith("/") else href
            )

            price_el = item.select_one(
                "[data-testid='customer-price'] span"
            ) or item.select_one(".priceView-customer-price span")
            price_text = price_el.get_text(strip=True) if price_el else None

            img_el = item.select_one(
                ".product-image img"
            ) or item.select_one("[data-testid='product-image'] img")
            image = img_el.get("src") if img_el else None

            listings.append(
                _normalise_listing(
                    title=title,
                    price_text=price_text,
                    url=full_url,
                    image=image,
                    merchant="Best Buy",
                    condition="New",
                )
            )
        except Exception:
            continue

    logger.info(f"Best Buy scrape: {len(listings)} listings")
    return listings


async def search_all_marketplaces(
    product: str, max_per_site: int = 8
) -> list[dict]:
    tasks = [
        asyncio.wait_for(amazon_search(product, max_per_site), timeout=20),
        asyncio.wait_for(ebay_search(product, max_per_site), timeout=20),
        asyncio.wait_for(walmart_search(product, max_per_site), timeout=20),
        asyncio.wait_for(bestbuy_search(product, max_per_site), timeout=20),
    ]
    result_list: list[Exception | list[dict]] = await asyncio.gather(
        *tasks, return_exceptions=True
    )

    seen_urls: set[str] = set()
    merged: list[dict] = []

    for res in result_list:
        if isinstance(res, (Exception, asyncio.TimeoutError)):
            logger.warning(f"Marketplace scraper error: {res}")
            continue
        for listing in res:
            url = listing.get("url", "")
            key = url.rstrip("/").lower()
            if key and key not in seen_urls:
                seen_urls.add(key)
                merged.append(listing)

    logger.info(f"Marketplace search total: {len(merged)} listings")
    return merged
