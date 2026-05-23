from fastapi import APIRouter

from app.services.cache import get_cached_history

router = APIRouter()


@router.get("/history")
async def history():
    claims = await get_cached_history()
    return {"claims": claims or []}
