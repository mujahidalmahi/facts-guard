import os
import json
import asyncio

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

API_KEYS = [
    k.strip()
    for k in os.getenv(
        "GEMINI_API_KEYS", ""
    ).split(",")
    if k.strip()
]

if not API_KEYS:
    raise RuntimeError(
        "GEMINI_API_KEYS must be set in .env"
    )

_current_key = 0
_model = None


def _configure(key: str):
    global _model
    genai.configure(api_key=key)
    _model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )


def _next_key():
    global _current_key
    key = API_KEYS[_current_key % len(API_KEYS)]
    _current_key += 1
    return key


def _get_model():
    global _model
    if _model is None:
        _configure(_next_key())
    return _model


async def analyze_claim(
    claim: str,
):
    prompt = f"""
You are FactGuard, an AI misinformation detection system.

Analyze the following claim carefully.

CLAIM:
"{claim}"

Return ONLY valid JSON.

Rules:
- Do not include markdown
- Do not wrap response in ```json
- Be concise
- Generate realistic evidence entries
- stance must be:
  supports | contradicts | neutral

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
      "date": "2026-05-23",
      "stance": "contradicts",
      "summary": "short explanation",
      "quote": "short quote"
    }}
  ]
}}
"""

    last_error = None

    for _ in range(len(API_KEYS)):
        try:
            model = _get_model()
            response = await asyncio.to_thread(
                model.generate_content, prompt
            )
        except ResourceExhausted as e:
            last_error = e
            _configure(_next_key())
            continue

        text = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            return json.loads(text)
        except Exception:
            return {
                "verdict":
                    "Unverified",
                "confidence":
                    "Low",
                "summary":
                    "Could not analyze claim.",
                "supports": 0,
                "contradicts": 0,
                "neutral": 0,
                "sources": [],
            }

    return {
        "verdict": "Unverified",
        "confidence": "Low",
        "summary":
            f"All API keys exhausted. "
            f"{last_error}",
        "supports": 0,
        "contradicts": 0,
        "neutral": 0,
        "sources": [],
    }
