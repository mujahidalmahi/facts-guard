import json
import re
from datetime import datetime, timezone

from app.logging_config import get_logger

logger = get_logger("credibility")

CREDIBILITY_SYSTEM_PROMPT = """You are a source credibility evaluator for FactGuard.
Given a list of URLs and titles, assign each a credibility tier.

## CREDIBILITY TIERS
High — Government (.gov), academic (.edu, peer-reviewed journals), major wire services (Reuters, AP, AFP), established broadcast/print (BBC, NYT, FT, WSJ, Guardian).
Medium — Established digital media (The Verge, Ars Technica, etc.), regional newspapers, recognised industry publications.
Low — Blogs, forums, social media, sites with no identifiable editorial standards, unknown domains, sites known for misinformation.

## OUTPUT CONTRACT
Return ONLY valid JSON array. No markdown.
[
  { "index": 0, "credibility": "High|Medium|Low", "reason": "One sentence." },
  ...
]"""

CREDIBILITY_USER_PROMPT = """Rate the credibility of each source:
{sources_list}
Return the JSON array."""


# Domain authority scoring — static heuristic
HIGH_DOMAIN_KEYWORDS = [".gov", ".edu", ".mil", ".int"]
HIGH_OUTLET_NAMES = [
    "reuters", "ap.org", "apnews", "associated press",
    "bbc", "bbc.com", "nytimes", "wsj", "ft.com",
    "theguardian", "bloomberg", "npr", "washington post",
    "wapo", "economist", "nature.com", "science.org",
    "pnas.org", "nejm", "thelancet", "cell.com",
]
LOW_DOMAIN_KEYWORDS = [
    ".blogspot", ".wordpress", ".medium.com",
    "reddit", "twitter", "x.com", "facebook",
    "tiktok", "instagram", "substack.com",
]


def _domain_authority_score(url: str) -> float:
    """Score 0.0-1.0 for domain authority."""
    url_lower = url.lower()
    for kw in HIGH_DOMAIN_KEYWORDS:
        if kw in url_lower:
            return 1.0
    for name in HIGH_OUTLET_NAMES:
        if name in url_lower:
            return 0.95
    for kw in LOW_DOMAIN_KEYWORDS:
        if kw in url_lower:
            return 0.2
    return 0.5


def _temporal_freshness_score(date_str: str | None) -> float:
    """Score 0.0-1.0: recent = higher."""
    if not date_str:
        return 0.3
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}", date_str):
            pub_date = datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        elif re.match(r"^\d{4}", date_str):
            pub_date = datetime.strptime(date_str[:4], "%Y").replace(tzinfo=timezone.utc)
        else:
            return 0.3
        days_old = (datetime.now(timezone.utc) - pub_date).days
        if days_old < 30:
            return 1.0
        if days_old < 183:
            return 0.9
        if days_old < 365:
            return 0.7
        if days_old < 730:
            return 0.5
        return 0.3
    except (ValueError, TypeError):
        return 0.3


async def evaluate_source_credibility(
    sources: list[dict],
    claim: str | None = None,
) -> list[dict]:
    """
    Enhanced credibility evaluation with:
    - Domain authority scoring
    - Temporal freshness weighting
    - AI-based tier classification (fallback to heuristic)
    """
    if not sources:
        return []

    from app.dependencies import get_gemini_service
    import asyncio

    sources_lines = []
    for i, s in enumerate(sources):
        sources_lines.append(
            f"[{i}] Title: {s.get('title', '')} | URL: {s.get('url', '')}"
        )
    sources_list_str = "\n".join(sources_lines)

    user_prompt = CREDIBILITY_USER_PROMPT.format(
        sources_list=sources_list_str,
    )

    try:
        gemini_service = get_gemini_service()
        model = gemini_service.get_model()
        if model is None:
            raise ValueError("Gemini model not initialized")

        response = await asyncio.wait_for(
            asyncio.to_thread(
                model.generate_content,
                user_prompt,
            ),
            timeout=10.0,
        )

        text = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        ratings = json.loads(text)

        for rating in ratings:
            idx = rating.get("index")
            if idx is not None and idx < len(sources):
                sources[idx]["credibility"] = (
                    rating.get("credibility", "Medium")
                )
                sources[idx]["credibility_reason"] = (
                    rating.get("reason", "")
                )

        return _enrich_with_scoring(sources)

    except Exception as e:
        logger.warning(
            f"Credibility AI evaluation failed: "
            f"{e}, falling back to heuristic"
        )
        sources = _heuristic_credibility(sources)
        return _enrich_with_scoring(sources)


def _enrich_with_scoring(sources: list[dict]) -> list[dict]:
    """Add domain authority, temporal freshness, and composite scores."""
    for s in sources:
        url = s.get("url", "")
        domain_score = _domain_authority_score(url)
        temporal_score = _temporal_freshness_score(s.get("date"))
        base_score = {"High": 0.9, "Medium": 0.5, "Low": 0.2}.get(s.get("credibility", "Medium"), 0.5)
        composite = (base_score * 0.4) + (domain_score * 0.35) + (temporal_score * 0.25)

        s["domain_authority_score"] = round(domain_score, 2)
        s["temporal_freshness_score"] = round(temporal_score, 2)
        s["credibility_score"] = round(composite, 2)

        if composite >= 0.75:
            s["credibility"] = "High"
        elif composite >= 0.4:
            s["credibility"] = "Medium"
        else:
            s["credibility"] = "Low"

    return sources


def _heuristic_credibility(
    sources: list[dict],
) -> list[dict]:
    for s in sources:
        url = s.get("url", "").lower()
        title = s.get("title", "").lower()

        if any(
            domain in url
            for domain in [
                ".gov",
                ".edu",
                ".mil",
            ]
        ):
            s["credibility"] = "High"
            s["credibility_reason"] = (
                "Government or educational domain."
            )
        elif any(
            name in url or name in title
            for name in [
                "reuters",
                "ap.org",
                "apnews",
                "bbc",
                "nytimes",
                "wsj",
                "ft.com",
                "theguardian",
                "bloomberg",
                "npr",
            ]
        ):
            s["credibility"] = "High"
            s["credibility_reason"] = (
                "Major news organisation."
            )
        elif any(
            domain in url
            for domain in [
                ".blogspot",
                ".wordpress",
                ".medium.com",
                "reddit",
                "twitter",
                "x.com",
                "facebook",
            ]
        ):
            s["credibility"] = "Low"
            s["credibility_reason"] = (
                "Blog or social media platform."
            )
        else:
            s["credibility"] = "Medium"
            s["credibility_reason"] = (
                "Standard web source."
            )

    return sources
