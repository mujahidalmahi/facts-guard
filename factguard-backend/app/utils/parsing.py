import json
import re
from typing import Any


def parse_json_response(text: str) -> Any:
    """
    Parse JSON from AI model responses that may contain markdown fences.
    Handles: ```json...``` fences, bare ``` fences, leading/trailing whitespace.
    Raises json.JSONDecodeError if parsing fails after cleanup.
    """
    cleaned = re.sub(r'```(?:json)?', '', text).strip()
    return json.loads(cleaned)
