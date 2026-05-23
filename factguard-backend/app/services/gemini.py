import os
import json

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


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
  "verdict": "Likely True | Likely False | Misleading | Unverified",
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

    response = model.generate_content(
        prompt
    )

    text = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(
            text
        )

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