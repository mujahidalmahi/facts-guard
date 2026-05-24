# FactGuard Backend - Quick Reference Guide

## 🚀 Quick Start

### Installation
```bash
cd factguard-backend
pip install -r requirements.txt
```

### Configuration
```bash
cp .env.example .env.local
# Edit .env.local with your actual credentials:
# - GEMINI_API_KEYS
# - SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
```

### Running the Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Detailed Health Check
```bash
curl http://localhost:8000/health/detailed
```

#### Verify a Claim (New v1 Endpoint)
```bash
curl -X POST http://localhost:8000/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth is flat"}'
```

#### Get Result by Job ID
```bash
curl http://localhost:8000/api/v1/verify/{job_id}
```

---

## 📚 Module Reference

### Configuration
```python
from app.config import settings

# Access any setting
print(settings.APP_NAME)
print(settings.FRONTEND_URL)
print(settings.GEMINI_MODEL_NAME)
print(settings.LOG_LEVEL)
```

### Logging
```python
from app.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Message", extra_field="value")
logger.error("Error", error_type="critical")
```

### Exceptions
```python
from app.exceptions import (
    ValidationError,
    ClaimNotFoundError,
    AnalysisFailedError,
    DatabaseError,
    GeminiAPIError,
)

raise ValidationError("Invalid input", {"field": "claim"})
raise ClaimNotFoundError(job_id="123")
raise AnalysisFailedError("API timeout")
```

### Dependency Injection
```python
from fastapi import Depends
from app.dependencies import (
    get_gemini_service_instance,
    get_supabase_service_instance,
)

@router.post("/my-endpoint")
async def my_endpoint(
    gemini_service = Depends(get_gemini_service_instance),
    supabase = Depends(get_supabase_service_instance),
):
    model = gemini_service.get_model()
    client = supabase.get_client()
```

### Validators
```python
from app.utils.validators import (
    validate_claim_text,
    validate_job_id,
    sanitize_string,
)

try:
    claim = validate_claim_text(user_input)
except ValidationError as e:
    print(e.details)
```

### Constants
```python
from app.utils.constants import (
    VALID_VERDICTS,
    VALID_CONFIDENCES,
    VALID_STANCES,
    STATUS_PROCESSING,
    STATUS_DONE,
)
```

### Database Service
```python
from app.dependencies import get_supabase_service_instance
from fastapi import Depends

async def my_endpoint(
    supabase_service = Depends(get_supabase_service_instance),
):
    client = supabase_service.get_client()
    
    # Use client directly or use service methods
    claim_id = supabase_service.create_claim(text, job_id)
    result_id = supabase_service.save_result(claim_id, analysis)
    supabase_service.save_sources_batch(result_id, sources)
```

---

## 🏗️ Adding a New Endpoint

### Step 1: Create the endpoint file
Create `app/api/v1/endpoints/my_endpoint.py`:

```python
from fastapi import APIRouter, Depends
from app.dependencies import get_supabase_service_instance
from app.schemas import VerifyRequest, AnalysisResponse
from app.logging_config import get_logger

logger = get_logger("my_endpoint")
router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint(
    supabase_service = Depends(get_supabase_service_instance),
):
    """My endpoint description."""
    try:
        logger.info("Endpoint called")
        return {"message": "success"}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

### Step 2: Register in router
Update `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import my_endpoint

router.include_router(
    my_endpoint.router,
    prefix="/my-endpoint",
    tags=["my-feature"],
)
```

### Step 3: Test
```bash
curl http://localhost:8000/api/v1/my-endpoint
```

---

## 🔍 Debugging

### View Logs
```python
from app.logging_config import get_logger

logger = get_logger("debug")
logger.debug("Debug info", variable=value)
```

### Health Check
```bash
curl http://localhost:8000/health/detailed
# Shows database and Gemini API status
```

### Configuration Check
```python
from app.config import settings
print(settings.model_dump())  # Show all settings
```

---

## 🧪 Testing Pattern

```python
import pytest
from unittest.mock import MagicMock, patch
from app.schemas import VerifyRequest
from app.api.v1.endpoints.verify import verify

@pytest.mark.asyncio
async def test_verify_success():
    mock_gemini = MagicMock()
    mock_supabase = MagicMock()
    
    response = await verify(
        VerifyRequest(claim="test"),
        gemini_service=mock_gemini,
        supabase_service=mock_supabase,
    )
    
    assert response.verdict in ["Verified", "Likely True", "Mixed Evidence"]
```

---

## 🚨 Common Issues & Solutions

### Issue: Configuration Error
```
Configuration Error: Missing required environment variables
```
**Solution**: Copy `.env.example` to `.env.local` and fill in values

### Issue: Gemini API Error
```
Gemini API error: All API keys exhausted
```
**Solution**: Check that `GEMINI_API_KEYS` has valid keys in `.env`

### Issue: Database Connection Error
```
Database error: Failed to connect to Supabase
```
**Solution**: Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`

### Issue: Import Error
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Run from `factguard-backend` directory or install package

---

## 📊 Performance Tips

### For Better Performance:
1. Use batch operations for multiple sources
2. Cache frequently accessed results
3. Use paginated queries for large result sets
4. Monitor database query times in logs

### Database Query Performance:
```python
# Good: Single query
result = supabase.get_full_result_optimized(job_id)

# Bad: Multiple separate queries
claim = supabase.get_claim(job_id)
result = supabase.get_result(claim_id)
sources = supabase.get_sources(result_id)
```

---

## 🔐 Security Checklist

- [ ] `.env` is in `.gitignore` (never commit secrets)
- [ ] `FRONTEND_URL` is set to actual domain in production
- [ ] API keys are rotated regularly
- [ ] Input validation is enabled (it is by default)
- [ ] Error responses don't leak sensitive info (they don't by default)
- [ ] CORS is restricted to allowed origins

---

## 📖 Further Reading

- `PHASE_1_IMPLEMENTATION.md` - Full implementation details
- `app/config.py` - Configuration options
- `app/exceptions.py` - Custom exceptions
- `app/schemas.py` - API contracts
- `app/dependencies.py` - Dependency injection setup

---

## 💡 Pro Tips

1. **Always use dependency injection** - Makes testing easier
2. **Check logs for debugging** - Structured logging provides context
3. **Use validators** - Prevent bad data early
4. **Handle exceptions explicitly** - Custom exceptions are provided
5. **Type hint everything** - Catches errors at development time
6. **Use constants** - No magic strings in code

---

## 🎯 Hackathon Showcase Points

✨ **Show judges**:
- Clean modular architecture (app/ structure)
- Comprehensive error handling (try-catch everywhere)
- Production-ready configuration (app/config.py)
- Proper logging system (structured JSON logs)
- Type-safe operations (Pydantic everywhere)
- API versioning support (api/v1/)
- Performance optimizations (database batch operations)

---

Generated: 2026-05-24
Last Updated: Phase 1 Complete
