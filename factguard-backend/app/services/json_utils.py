import json
import re


def extract_json(text: str) -> dict | list:
    """Extract the first JSON object or array from any text.

    Strips markdown code fences, XML tags, and leading/trailing text.
    Raises json.JSONDecodeError if no valid JSON is found.
    """
    text = text.strip()
    text = re.sub(r"^.*?(?=[{\[])", "", text, count=1, flags=re.DOTALL)
    text = re.sub(r"(?<=[}\]])[^\]}]*$", "", text, count=1, flags=re.DOTALL)
    text = text.strip()
    return json.loads(text)
