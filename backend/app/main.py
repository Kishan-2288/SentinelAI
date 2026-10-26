import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import audit, dashboard, meta, model_configs, runs
from app.config import get_settings
from app.database import SessionLocal
from app.services.run_service import recover_interrupted_runs

log = logging.getLogger("sentinelai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        recovered = recover_interrupted_runs(app.state.session_factory)
        if recovered:
            log.warning("Marked %d interrupted run(s) as failed", recovered)
    except Exception as exc:  # e.g. migrations not applied yet
        log.error("Startup recovery skipped (%s). Did you run `alembic upgrade head`?", type(exc).__name__)
    yield


app = FastAPI(title="SentinelAI API", description="LLM adversarial safety testing backend",
              version="0.3.0", lifespan=lifespan)
app.state.session_factory = SessionLocal


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Return field errors without echoing submitted provider credentials."""
    errors = []
    for error in exc.errors():
        item = dict(error)
        location = item.get("loc", ())
        if any(field in location for field in ("api_key", "secret_ref")):
            item["input"] = "[redacted]"
        elif isinstance(item.get("input"), dict) and any(
            field in item["input"] for field in ("api_key", "secret_ref")
        ):
            safe_input = dict(item["input"])
            for field in ("api_key", "secret_ref"):
                if field in safe_input:
                    safe_input[field] = "[redacted]"
            item["input"] = safe_input
        errors.append(item)
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": errors}))


app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origin_list,
                   allow_methods=["*"], allow_headers=["*"])
for router in (meta.router, model_configs.router, runs.router, dashboard.router, audit.router):
    app.include_router(router)
