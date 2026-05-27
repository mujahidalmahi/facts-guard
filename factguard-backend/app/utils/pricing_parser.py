import re
from typing import Optional

from app.logging_config import get_logger

logger = get_logger("pricing_parser")

MERCHANT_DOMAINS: dict[str, str] = {
    "amazon": "Amazon",
    "amzn": "Amazon",
    "ebay": "eBay",
    "aliexpress": "AliExpress",
    "alibaba": "Alibaba",
    "walmart": "Walmart",
    "bestbuy": "Best Buy",
    "best buy": "Best Buy",
    "newegg": "Newegg",
    "target": "Target",
    "costco": "Costco",
    "bhphotovideo": "B&H Photo",
    "adorama": "Adorama",
    "etsy": "Etsy",
    "wish": "Wish",
    "shopify": "Shopify",
    "flipkart": "Flipkart",
    "rakuten": "Rakuten",
    "mercadolibre": "Mercado Libre",
    "jd.com": "JD",
    "taobao": "Taobao",
    "tmall": "Tmall",
    "zalando": "Zalando",
    "asos": "ASOS",
    "apple": "Apple",
    "microsoft": "Microsoft",
    "samsung": "Samsung",
}

MERCHANT_TRUST: dict[str, str] = {
    "Amazon": "High",
    "Apple": "High",
    "Best Buy": "High",
    "Walmart": "High",
    "Target": "High",
    "Costco": "High",
    "B&H Photo": "High",
    "Adorama": "High",
    "Microsoft": "High",
    "Samsung": "High",
    "eBay": "Medium",
    "AliExpress": "Medium",
    "Alibaba": "Medium",
    "Newegg": "Medium",
    "Etsy": "Medium",
    "Flipkart": "Medium",
    "Rakuten": "Medium",
    "Mercado Libre": "Medium",
    "JD": "Medium",
    "Taobao": "Medium",
    "Tmall": "Medium",
    "Shopify": "Medium",
    "Zalando": "Medium",
    "ASOS": "Medium",
    "Wish": "Low",
}

MERCHANT_PRIORITY: dict[str, int] = {
    "Amazon": 0,
    "eBay": 0,
    "AliExpress": 0,
    "Walmart": 1,
    "Best Buy": 1,
    "Target": 1,
    "Newegg": 1,
    "Costco": 1,
    "B&H Photo": 2,
    "Adorama": 2,
    "Apple": 1,
    "Microsoft": 2,
    "Samsung": 2,
    "Alibaba": 2,
    "Etsy": 2,
    "Flipkart": 2,
    "Rakuten": 2,
    "Mercado Libre": 2,
    "JD": 2,
    "Taobao": 3,
    "Tmall": 3,
    "Shopify": 3,
    "Zalando": 3,
    "ASOS": 3,
    "Wish": 4,
}

PRICE_PATTERNS = [
    re.compile(r"\$\s*([\d,]+)\s*-\s*\$\s*([\d,]+)"),
    re.compile(r"\$[\s]*([\d,]+\.?\d*)"),
    re.compile(r"€[\s]*([\d,]+\.?\d*)"),
    re.compile(r"£[\s]*([\d,]+\.?\d*)"),
    re.compile(r"₹[\s]*([\d,]+\.?\d*)"),
    re.compile(r"([\d,]+\.?\d*)\s*€"),
    re.compile(r"([\d,]+\.?\d*)\s*USD"),
    re.compile(r"([\d,]+\.?\d*)\s*BDT"),
    re.compile(r"([\d,]+\.?\d*)\s*INR"),
    re.compile(r"price[:\s]*\$?([\d,]+\.?\d*)", re.IGNORECASE),
    re.compile(r"price[:\s]*₹?([\d,]+\.?\d*)", re.IGNORECASE),
    re.compile(r"from\s*\$?([\d,]+\.?\d*)", re.IGNORECASE),
    re.compile(r"from\s*₹?([\d,]+\.?\d*)", re.IGNORECASE),
]

MODEL_SEPARATORS = re.compile(r"[,\(\)\[\]\-–—/]|\s+\d{4}\s*$")
SPEC_PATTERNS = [
    re.compile(r"(\d+[Gg][Bb])"),
    re.compile(r"(RTX|GTX|RX|Arc)\s*\d+"),
    re.compile(r"(i\d|Ryzen\s*\d|Intel|AMD|Apple\s*M\d)"),
    re.compile(r"(\d+[Kk]\s*(OLED|LCD|IPS|LED)?)"),
]


def extract_price(text: str) -> Optional[float]:
    for pattern in PRICE_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                groups = match.groups()
                price_str = groups[0] if groups else match.group(0)
                price_str = re.sub(r"[^\d.]", "", price_str.replace(",", ""))
                if price_str is not None and float(price_str) >= 0:
                    return float(price_str)
            except (ValueError, IndexError):
                continue
    return None


def classify_merchant(url: str) -> str:
    url_lower = url.lower()
    for domain_key, merchant_name in MERCHANT_DOMAINS.items():
        if domain_key in url_lower:
            return merchant_name

    try:
        from urllib.parse import urlparse
        parsed = urlparse(url_lower)
        domain = parsed.netloc or parsed.path.split("/")[0]
        parts = domain.split(".")
        if len(parts) >= 3 and parts[-1] in {"uk", "au", "jp", "br", "fr", "de", "nz", "kr", "in", "cn"}:
            return parts[-3].title() if len(parts) >= 3 else parts[-2].title()
        if len(parts) >= 2:
            return parts[-2].title()
    except Exception:
        pass
    return "Unknown Merchant"


def extract_model_name(title: str) -> str:
    parts = MODEL_SEPARATORS.split(title)
    if parts and len(parts[0]) >= 3 and len(parts[0]) <= 80:
        return parts[0].strip()
    return title[:60].strip()


def extract_specs(title: str) -> str:
    found = []
    for pattern in SPEC_PATTERNS:
        match = pattern.search(title)
        if match:
            found.append(match.group(0))
    return ", ".join(found) if found else ""


def get_trust_level(merchant: str) -> str:
    return MERCHANT_TRUST.get(merchant, "Low")


def get_priority(merchant: str) -> int:
    return MERCHANT_PRIORITY.get(merchant, 5)


def sort_listings(listings: list[dict]) -> list[dict]:
    return sorted(
        listings,
        key=lambda listing: (
            get_priority(listing.get("merchant", "")),
            listing.get("price") is None,
            listing.get("price") or float("inf"),
        ),
    )


def cluster_listings(listings: list[dict]) -> list[dict]:
    clusters: dict[str, dict] = {}
    for listing in listings:
        model = listing.get("model_name", extract_model_name(listing.get("title", "")))
        if model not in clusters:
            clusters[model] = {
                "model": model,
                "specs": extract_specs(listing.get("title", "")),
                "prices": [],
            }
        price = listing.get("price")
        if price:
            clusters[model]["prices"].append(price)

    result = []
    for data in clusters.values():
        prices = data["prices"]
        if prices:
            lo, hi = min(prices), max(prices)
            data["min_price"] = lo
            if lo == hi:
                data["priceRange"] = f"${lo:,.2f}"
            else:
                data["priceRange"] = f"${lo:,.2f} – ${hi:,.2f}"
        else:
            data["min_price"] = None
            data["priceRange"] = "Price unavailable"
        del data["prices"]
        result.append(data)

    result.sort(key=lambda v: v.get("min_price", float("inf")))
    return result
