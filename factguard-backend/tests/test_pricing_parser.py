from app.utils.pricing_parser import (
    classify_merchant,
    extract_price,
    get_trust_level,
)


def test_extract_price_dollar():
    assert extract_price("Only $299 today") == 299.0
    assert extract_price("Price: $49.99") == 49.99


def test_extract_price_euro():
    assert extract_price("€39.99") == 39.99


def test_extract_price_no_price():
    assert extract_price("Free shipping") is None


def test_classify_merchant_amazon():
    assert classify_merchant("https://www.amazon.com/dp/123") == "Amazon"


def test_classify_merchant_ebay():
    assert classify_merchant("https://ebay.com/itm/456") == "eBay"


def test_classify_trust_level():
    assert get_trust_level("Amazon") == "High"
    assert get_trust_level("eBay") == "Medium"
    assert get_trust_level("Wish") == "Low"
    assert get_trust_level("Unknown") == "Low"
