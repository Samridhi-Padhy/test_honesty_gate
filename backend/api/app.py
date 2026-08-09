"""FastAPI application for the test-honesty gate.

Exposes one endpoint that returns the final contract JSON shape. A
mock-mode flag (env var ``MOCK_MODE`` or query param ``mock=true``) returns
static mocked contract JSON without touching gate_service or the LLM at
all — this is the permanent fallback for frontend dev when the real chain
is unavailable.

The default (non-mock) path runs the REAL end-to-end chain:
mutation_engine applies all 5 mutants -> gate_service aggregates the
results -> llm_explainer fills in explanations for surviving mutants.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from fastapi.responses import JSONResponse
from gate_service.gate import run_gate
from llm_explainer.mock_input import mock_contract
from llm_explainer.service import explain_surviving_mutants

app = FastAPI(title="Test-Honesty Gate API", version="0.1.0")

# CORS configuration
allowed_origins_str = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [
    origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": True, "detail": str(exc)},
    )


def _mock_mode_enabled(mock_param: bool | None) -> bool:
    """Resolve mock mode from query param, falling back to env var."""
    if mock_param is not None:
        return mock_param
    return os.environ.get("MOCK_MODE", "false").lower() in ("1", "true", "yes")


@app.get("/gate")
def get_gate_contract(
    mock: bool | None = Query(default=None, description="Force mock mode"),
) -> dict[str, Any]:
    """Return the final contract JSON shape.

    In mock mode, returns static mocked contract JSON with zero backend
    dependencies (permanent fallback for frontend dev). Otherwise, runs the
    real end-to-end chain: mutation_engine -> gate_service -> llm_explainer.
    """
    if _mock_mode_enabled(mock):
        return mock_contract()

    # Real chain: mutation_engine applies all 5 mutants, gate_service
    # aggregates into the locked contract shape, llm_explainer fills in
    # explanations for surviving mutants.
    contract = run_gate("local")
    return explain_surviving_mutants(contract)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple liveness probe for CI / orchestration."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint so GET / doesn't 404."""
    return {"message": "Test Honesty Gate API is running. Check /gate or /health."}
