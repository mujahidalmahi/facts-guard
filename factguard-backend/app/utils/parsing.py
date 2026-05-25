import json
import re
from typing import Any


def strip_scratchpad(text: str) -> str:
    return re.sub(r"<scratchpad>.*?</scratchpad>", "", text, flags=re.DOTALL).strip()


def validate_source_urls(sources: list[dict], original_urls: set[str]) -> list[dict]:
    validated = []
    for src in sources:
        url = src.get("url", "")
        if url not in original_urls:
            src["url"] = ""
            src["credibility"] = "Low"
            src["_hallucinated"] = True
        validated.append(src)
    return validated


def parse_json_response(text: str) -> Any:
    """
    Parse JSON from AI model responses that may contain markdown fences.
    Handles: ```json...``` fences, bare ``` fences, leading/trailing whitespace.
    Also strips CoT scratchpad blocks before parsing.
    Raises json.JSONDecodeError if parsing fails after cleanup.
    """
    cleaned = strip_scratchpad(text)
    cleaned = re.sub(r'```(?:json)?', '', cleaned).strip()
    return json.loads(cleaned)
