import asyncio
import json
from datetime import (
    datetime,
    timezone,
)

from google.api_core.exceptions import (
    InternalServerError,
    ResourceExhausted,
    ServiceUnavailable,
)

from app.dependencies import (
    get_gemini_service,
)
from app.logging_config import (
    get_logger,
)
from app.services.cache import (
    set_progress,
)
from app.utils.search import (
    search_claim,
)

logger = get_logger(
    "gemini"
)

FALLBACK_RESPONSE = {
    "verdict":
        "Unverified",
    "confidence":
        "Low",
    "summary":
        "Could not analyze claim. Please try again.",
    "supports": 0,
    "contradicts": 0,
    "neutral": 0,
    "sources": [],
    "_is_fallback": True,
}

REQUIRED_KEYS = {
    "verdict",
    "confidence",
    "summary",
    "supports",
    "contradicts",
    "neutral",
}


def _validate_response(
    result: dict,
) -> bool:
    missing = (
        REQUIRED_KEYS
        - set(result.keys())
    )

    if missing:
        logger.warning(
            f"LLM response missing required keys: {missing}"
        )
        return False

    return True


async def analyze_claim(
    claim: str,
    job_id:
    str | None = None,
) -> dict:
    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    if job_id:
        await set_progress(
            job_id,
            "Searching via Bright Data...",
        )

    search_results = (
        await search_claim(
            claim
        )
    )

    search_context = ""

    if search_results:
        lines = []

        for i, r in enumerate(
            search_results,
            1,
        ):
            lines.append(
                f'{i}. "{r["title"]}"'
            )
            lines.append(
                f'   URL: {r["url"]}'
            )
            lines.append(
                f'   Snippet: {r["snippet"]}'
            )

        search_context = (
            "\n".join(lines)
        )

    search_section = f"""
Use these live web search results about this claim as your primary evidence.
Base your analysis on these real sources.
Do NOT fabricate sources.

Web Search Results:
{search_context or "No web search results found. Use your best judgment."}
"""

    prompt = f"""
You are FactGuard, an AI misinformation detection system.
Today's date is {today}.

{search_section}

Analyze the following claim carefully.

CLAIM:
"{claim}"

Return ONLY valid JSON.

Rules:
- Do not include markdown
- Do not wrap response in ```json
- Be concise
- Use the web search results above as evidence sources
- stance must be:
  supports | contradicts | neutral
- relevance must be a number 0-10

JSON format:

{{
  "verdict": "Verified | Likely True | Mixed Evidence | Likely Misleading | Unverified",
  "confidence": "Low | Medium | High",
  "summary": "2 sentence explanation",

  "supports": number,
  "contradicts": number,
  "neutral": number,

  "sources": [
    {{
      "title": "source title",
      "url": "https://example.com",
      "author": "organization name",
      "date": "{today}",
      "stance": "contradicts",
      "relevance": 8,
      "summary": "short explanation",
      "quote": "short quote"
    }}
  ]
}}
"""

    gemini_service = (
        get_gemini_service()
    )

    max_retries = len(
        gemini_service.api_keys
    )

    for attempt in range(
        max_retries
    ):
        try:
            if job_id:
                await set_progress(
                    job_id,
                    "Analysing with AI...",
                )

            model = (
                gemini_service.get_model()
            )

            # 30-second timeout fix
            response = (
                await asyncio.wait_for(
                    asyncio.to_thread(
                        model.generate_content,
                        prompt,
                    ),
                    timeout=30.0,
                )
            )

            text = (
                response.text
                .replace(
                    "```json",
                    "",
                )
                .replace(
                    "```",
                    "",
                )
                .strip()
            )

            result = json.loads(
                text
            )

            if not _validate_response(
                result
            ):
                return dict(
                    FALLBACK_RESPONSE
                )

            logger.info(
                "Claim analysis completed successfully"
            )

            return result

        except asyncio.TimeoutError:
            logger.warning(
                f"Gemini timeout on attempt {attempt + 1}"
            )

            remaining = (
                max_retries
                - attempt
                - 1
            )

            if remaining > 0:
                gemini_service.rotate_key()

                await asyncio.sleep(
                    1
                )

                continue

            return {
                **FALLBACK_RESPONSE,
                "summary":
                    "AI analysis timed out.",
            }

        except (
            ResourceExhausted,
            InternalServerError,
            ServiceUnavailable,
        ):
            remaining = (
                max_retries
                - attempt
                - 1
            )

            logger.warning(
                f"Gemini API key exhausted "
                f"(attempt {attempt + 1}/{max_retries}), "
                f"rotating to next key"
            )

            if remaining > 0:
                gemini_service.rotate_key()

                await asyncio.sleep(
                    1
                )

            continue

        except json.JSONDecodeError as e:
            logger.warning(
                f"JSON parsing failed: {str(e)}"
            )

            return dict(
                FALLBACK_RESPONSE
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during analysis: {str(e)}"
            )

            return dict(
                FALLBACK_RESPONSE
            )

    logger.error(
        "All API key retries exhausted"
    )

    return {
        **FALLBACK_RESPONSE,
        "summary":
            "All API keys exhausted. Please try again later.",
    }