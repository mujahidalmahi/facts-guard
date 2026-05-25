import json

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


async def evaluate_source_credibility(
    sources: list[dict],
) -> list[dict]:
    """
    Pre-process search results to assign credibility tiers.
    Takes a list of {title, url} dicts, returns same list with
    'credibility' and 'credibility_reason' fields added.
    Falls back to rule-based heuristic if AI call fails.
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
    sources_list = "\n".join(sources_lines)

    user_prompt = CREDIBILITY_USER_PROMPT.format(
        sources_list=sources_list,
    )

    try:
        gemini_service = get_gemini_service()
        model = gemini_service.get_model()

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

        return sources

    except Exception as e:
        logger.warning(
            f"Credibility AI evaluation failed: "
            f"{e}, falling back to heuristic"
        )
        return _heuristic_credibility(sources)


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
