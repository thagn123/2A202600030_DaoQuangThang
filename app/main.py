"""
Production AI Agent — Main Entry Point
Checks:
  ✅ Config from environment
  ✅ Structured JSON logging
  ✅ Auth, Rate Limiting, Cost Guard (Modular)
  ✅ Health check + Readiness probe
  ✅ Graceful shutdown
"""
import time
import asyncio
import signal
import logging
import json
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from app.config import settings
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit
from app.cost_guard import check_and_record_cost, get_current_cost

# Mock LLM
try:
    from utils.mock_llm import ask as llm_ask
except ImportError:
    # Fallback if utils is not in the path correct context
    def llm_ask(q): return f"Mock response to: {q}"

# Logging - JSON structured
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
logger.info(f"--- Application started at {datetime.now(timezone.utc)} ---")
logger.info(f"--- Config: ENV={settings.environment}, PORT={settings.port} ---")
_is_ready = False
_request_count = 0
_error_count = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(json.dumps({
        "event": "startup",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }))
    await asyncio.sleep(0.1)  # simulate init
    _is_ready = True
    yield
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global _request_count, _error_count
    start = time.time()
    _request_count += 1
    try:
        response: Response = await call_next(request)
        duration = round((time.time() - start) * 1000, 1)
        logger.info(json.dumps({
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "ms": duration,
        }))
        return response
    except Exception as e:
        _error_count += 1
        logger.error(json.dumps({"event": "error", "error": str(e)}))
        raise

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    timestamp: str

@app.get("/")
def root():
    return {"app": settings.app_name, "status": "running"}

@app.post("/ask", response_model=AskResponse)
async def ask_agent(
    body: AskRequest,
    request: Request,
    _key: str = Depends(verify_api_key),
):
    # Rate limit per API key (using first 8 chars as bucket)
    check_rate_limit(_key[:8])

    # Budget check (input tokens approx)
    input_tokens = len(body.question.split()) * 2
    check_and_record_cost(input_tokens, 0)

    answer = llm_ask(body.question)

    # Output tokens approx
    output_tokens = len(answer.split()) * 2
    check_and_record_cost(0, output_tokens)

    return AskResponse(
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/ready")
def ready():
    if not _is_ready:
        from fastapi import HTTPException
        raise HTTPException(503, "Not ready")
    return {"ready": True}

@app.get("/metrics")
def metrics(_key: str = Depends(verify_api_key)):
    return {
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
        "error_count": _error_count,
        "daily_cost_usd": round(get_current_cost(), 4),
    }

def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))

signal.signal(signal.SIGTERM, _handle_signal)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
