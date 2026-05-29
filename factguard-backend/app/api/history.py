from fastapi import (
    APIRouter,
)

from app.logging_config import (
    get_logger,
)

from app.services.cache import (
    get_cached_history,
)

logger = get_logger("history")

router = APIRouter()


def _enrich_claim(claim: dict) -> dict:
    text = claim.get("claim_text", "") or claim.get("claim", "")
    if text.startswith("[FINANCIAL]"):
        mode = "financial"
        display = text.replace("[FINANCIAL] ", "")
    elif text.startswith("[CART]"):
        mode = "cart"
        display = text.replace("[CART] ", "")
    elif text.startswith("[FIN]"):
        mode = "financial"
        display = text.replace("[FIN] ", "")
    else:
        mode = "verify"
        display = text
    return {**claim, "mode": mode, "display_text": display}


@router.get("/history")
async def history():
    try:
        claims = await get_cached_history()

        return {"claims": [_enrich_claim(c) for c in (claims or [])]}

    except Exception as e:
        logger.error(f"History fetch failed: {str(e)}")

        # Fallback instead
        # of breaking frontend
        return {"claims": []}
