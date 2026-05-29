import asyncio

from app.logging_config import get_logger
from app.services.brightdata import serp_search, proxy_request
from app.utils.duckduckgo import search as _duckduckgo_search

logger = get_logger("threat_monitor")

TRUSTED_NEWS_DOMAINS = [
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "nytimes.com",
    "wsj.com",
    "ft.com",
    "bloomberg.com",
    "theguardian.com",
    "npr.org",
    "washingtonpost.com",
    "economist.com",
    "cnbc.com",
    "republicworld.com",
    "timesofindia.indiatimes.com",
    "thehindu.com",
]

RISK_KEYWORDS = {
    "brand": [
        "breach",
        "vulnerability",
        "ransomware",
        "data leak",
        "cyber attack",
        "hacked",
        "security incident",
        "product defect",
        "recall",
        "lawsuit",
        "fraud",
        "scandal",
        "misconduct",
        "investigation",
    ],
    "regulatory": [
        "regulation",
        "compliance",
        "fine",
        "penalty",
        "regulatory",
        "SEC",
        "GDPR",
        "CCPA",
        "sanction",
        "oversight",
        "legislation",
        "policy change",
    ],
    "vendor": [
        "supplier",
        "vendor",
        "insolvency",
        "bankruptcy",
        "layoff",
        "restructuring",
        "acquisition",
        "merger",
        "downgrade",
        "default",
        "credit rating",
    ],
    "disinformation": [
        "misinformation",
        "disinformation",
        "fake news",
        "deepfake",
        "coordinated",
        "bot network",
        "propaganda",
        "false claim",
        "hoax",
    ],
}


async def scan_for_threats(
    query: str | None = None,
    domains: list[str] | None = None,
) -> list[dict]:
    """Scan news domains for potential threats matching risk categories."""
    threats = []
    search_queries = []

    if query:
        search_queries = [query]
    else:
        search_queries = [
            "security breach news",
            "regulatory compliance update",
            "vendor risk alert",
            "disinformation campaign",
        ]

    for q in search_queries:
        try:
            results = await serp_search(q, max_results=5)
            if not results:
                results = await asyncio.to_thread(_duckduckgo_search, q, 5)

            for r in results:
                threat = _classify_threat(r)
                if threat:
                    if threat["threat_type"] in ("brand", "regulatory"):
                        try:
                            body_text = await proxy_request(
                                threat["source_url"],
                                country="us",
                            )
                            if body_text:
                                threat["body_preview"] = body_text[:500]
                                threat["bright_data_product"] = "Residential Proxies"
                        except Exception:
                            pass
                    threats.append(threat)
        except Exception as e:
            logger.warning(f"Threat scan query '{q}' failed: {e}")

    logger.info(f"Threat scan found {len(threats)} potential threats")
    return threats


def _classify_threat(result: dict) -> dict | None:
    """Classify a search result into a threat category if it matches."""
    title = (result.get("title", "") + " " + result.get("snippet", "")).lower()
    url = result.get("url", "").lower()

    scores = {}
    for category, keywords in RISK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in title)
        if score > 0:
            scores[category] = score

    if not scores:
        return None

    best_category: str = max(
        (k for k in scores),
        key=lambda k: scores.get(k, 0),
    )
    severity = "low"
    if scores[best_category] >= 3:
        severity = "high"
    elif scores[best_category] >= 2:
        severity = "medium"

    return {
        "threat_type": best_category,
        "severity": severity,
        "title": result.get("title", ""),
        "description": result.get("snippet", ""),
        "source_url": result.get("url", ""),
        "source_domain": url.split("/")[2] if "//" in url else "unknown",
        "confidence": min(1.0, scores[best_category] / 5),
        "alert_status": "new",
    }


async def generate_compliance_report(threats: list[dict]) -> str:
    """Generate a timestamped compliance report from threats."""
    from datetime import datetime, timezone

    report_lines = [
        "=== FACTGUARD COMPLIANCE REPORT ===",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Total threats: {len(threats)}",
        "",
    ]

    for i, t in enumerate(threats, 1):
        report_lines.extend(
            [
                f"--- Threat #{i} ---",
                f"Type: {t.get('threat_type', 'unknown')}",
                f"Severity: {t.get('severity', 'unknown')}",
                f"Title: {t.get('title', 'N/A')}",
                f"Source: {t.get('source_url', 'N/A')}",
                f"Description: {t.get('description', 'N/A')}",
                f"Confidence: {t.get('confidence', 0)}",
                "",
            ]
        )

    return "\n".join(report_lines)
