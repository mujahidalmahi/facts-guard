from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.verify import (
    router as verify_router,
)

app = FastAPI(
    title="FactGuard API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    verify_router
)


@app.get("/")
async def root():
    return {
        "message":
        "FactGuard backend running"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }