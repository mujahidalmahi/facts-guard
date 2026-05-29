import json
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import get_logger
from app.services.db import insert

logger = get_logger("audit")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Read body BEFORE calling next — the stream can only be consumed once.
        # We cache it so the downstream handler can still read it.
        try:
            body_bytes = await request.body()
            body = json.loads(body_bytes) if body_bytes else {}
        except (json.JSONDecodeError, RuntimeError):
            body = {}

        response = await call_next(request)

        if request.url.path.startswith("/health"):
            return response

        try:
            await insert(
                "audit_logs",
                {
                    "id": str(uuid.uuid4()),
                    "user_id": request.headers.get("x-user-id"),
                    "action": f"{request.method} {request.url.path}",
                    "api_endpoint": request.url.path,
                    "request_body": body if body else None,
                    "response_status": response.status_code,
                    "ip_address": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to write audit log: {e}")

        return response
