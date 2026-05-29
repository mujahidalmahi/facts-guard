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
    Parse JSON from AI model responses that may contain markdown fences,
    text wrapping, XML tags, or CoT scratchpad blocks.

    Strategy:
    1. Strip <scratchpad> blocks
    2. Strip markdown code fences (```json, ```)
    3. Find first '{' or '[' and match to the corresponding closing bracket
    4. Try json.loads on the extracted substring
    Raises json.JSONDecodeError if parsing fails after cleanup.
    """
    cleaned = strip_scratchpad(text)
    cleaned = re.sub(r"```(?:json)?", "", cleaned)
    cleaned = cleaned.strip()

    obj_start = cleaned.find("{")
    arr_start = cleaned.find("[")
    start = -1
    if obj_start >= 0 and (arr_start < 0 or obj_start < arr_start):
        start = obj_start
        brace_depth = 0
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    return json.loads(cleaned[start : i + 1])
    elif arr_start >= 0:
        start = arr_start
        brace_depth = 0
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if ch == "[":
                brace_depth += 1
            elif ch == "]":
                brace_depth -= 1
                if brace_depth == 0:
                    return json.loads(cleaned[start : i + 1])

    raise json.JSONDecodeError(
        "No valid JSON found", cleaned, 0
    )
