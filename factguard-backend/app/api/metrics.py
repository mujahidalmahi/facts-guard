from prometheus_client import Counter, Gauge, generate_latest
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

claims_total = Counter("factguard_claims_total", "Claims submitted", ["mode"])
ai_fallbacks = Counter(
    "factguard_ai_fallbacks_total", "AI provider fallbacks", ["from_provider", "to_provider"]
)
aiml_key_switches = Counter(
    "factguard_aiml_key_switches_total",
    "Times AIML API switched from key 1 to key 2"
)
aiml_keys_exhausted = Counter(
    "factguard_aiml_keys_exhausted_total",
    "Times all AIML API keys were exhausted (triggers next provider)"
)
cache_hits = Counter("factguard_cache_hits_total", "Redis cache hits", ["cache_type"])
active_jobs = Gauge("factguard_active_jobs", "Currently processing jobs")


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return generate_latest()
