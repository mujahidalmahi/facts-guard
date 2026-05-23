import asyncio
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(
    Path(__file__).resolve().parent.parent.parent
    / ".env"
)

_url = os.getenv("SUPABASE_URL")
_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

_supabase = None


def _get_client():
    global _supabase
    if _supabase is None:
        _supabase = create_client(_url, _key)
    return _supabase


async def create_claim(claim_text: str, job_id: str) -> str:
    client = _get_client()
    result = await asyncio.to_thread(
        lambda: client.table("claims")
        .insert(
            {
                "claim_text": claim_text,
                "job_id": job_id,
                "status": "processing",
            }
        )
        .execute()
    )
    return result.data[0]["id"]


async def save_result(
    claim_id: str, data: dict[str, Any]
) -> str:
    client = _get_client()
    result = await asyncio.to_thread(
        lambda: client.table("results")
        .insert(
            {
                "claim_id": claim_id,
                "verdict": data["verdict"],
                "confidence": data["confidence"],
                "summary": data["summary"],
                "supports": data.get("supports", 0),
                "contradicts": data.get(
                    "contradicts", 0
                ),
                "neutral": data.get("neutral", 0),
            }
        )
        .execute()
    )
    return result.data[0]["id"]


async def save_sources(
    result_id: str,
    sources: list[dict[str, Any]],
):
    client = _get_client()
    if not sources:
        return
    rows = []
    for s in sources:
        rows.append(
            {
                "result_id": result_id,
                "url": s.get("url", ""),
                "title": s.get("title", ""),
                "author": s.get("author"),
                "published": s.get("date"),
                "stance": s.get("stance", "neutral"),
                "relevance": s.get("relevance", 5),
                "summary": s.get("summary", ""),
                "quote": s.get("quote"),
            }
        )
    await asyncio.to_thread(
        lambda: client.table("sources").insert(rows).execute()
    )


async def update_claim_status(
    claim_id: str, status: str
):
    client = _get_client()
    await asyncio.to_thread(
        lambda: client.table("claims")
        .update({"status": status})
        .eq("id", claim_id)
        .execute()
    )


async def get_full_result(
    job_id: str,
) -> dict[str, Any] | None:
    client = _get_client()
    claim = await asyncio.to_thread(
        lambda: client.table("claims")
        .select("*")
        .eq("job_id", job_id)
        .maybe_single()
        .execute()
    )
    if not claim.data:
        return None

    result = await asyncio.to_thread(
        lambda: client.table("results")
        .select("*")
        .eq("claim_id", claim.data["id"])
        .maybe_single()
        .execute()
    )
    if not result.data:
        return None

    sources = await asyncio.to_thread(
        lambda: client.table("sources")
        .select("*")
        .eq("result_id", result.data["id"])
        .execute()
    )

    return {
        "jobId": claim.data["job_id"],
        "claim": claim.data["claim_text"],
        "createdAt": claim.data["created_at"],
        "verdict": result.data["verdict"],
        "confidence": result.data["confidence"],
        "summary": result.data["summary"],
        "supports": result.data["supports"],
        "contradicts": result.data["contradicts"],
        "neutral": result.data["neutral"],
        "sources": [
            {
                "url": s["url"],
                "title": s["title"],
                "author": s.get("author"),
                "date": s.get("published"),
                "stance": s["stance"],
                "relevance": s.get("relevance", 5),
                "summary": s.get("summary", ""),
                "quote": s.get("quote"),
            }
            for s in sources.data
        ],
    }
