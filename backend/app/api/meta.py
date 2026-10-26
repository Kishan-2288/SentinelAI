
import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.llm.ollama import OllamaClient
from app.models import ModelConfig
from app.schemas_registry import secret_is_configured
from app.security.auth import CurrentUser, get_current_user

router = APIRouter(tags=["meta"])


@router.get("/health")
@router.get("/api/v1/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "unavailable"

    return {
        "status": "ok" if database == "ok" else "degraded",
        "service": "sentinelai-api",
        "database": database,
    }


@router.get("/api/v1/providers")
def providers(user: CurrentUser = Depends(get_current_user)):
    s = get_settings()

    return {
        "configured_default": s.llm_provider,
        "providers": [
            {
                "id": "ollama",
                "kind": "internal",
                "configured": True,
                "base_url": s.ollama_base_url,
                "default_model": s.ollama_model,
                "sends_data_off_machine": False,
            },
            {
                "id": "external",
                "kind": "external",
                "configured": bool(
                    s.external_api_key and s.external_api_model
                ),
                "base_url": s.external_api_base_url,
                "default_model": s.external_api_model or None,
                "sends_data_off_machine": True,
            },
        ],
    }


@router.get("/api/v1/models")
async def models(
    enabled_only: bool = Query(False),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    s = get_settings()
    items = []
    warnings = []

    # Discover Ollama models live. A discovery failure should not prevent
    # saved model configurations from being returned.
    live_ollama_models = set()

    try:
        live_ollama_models = set(await OllamaClient().list_models())
    except (httpx.HTTPError, ValueError, KeyError):
        warnings.append("Could not reach Ollama; is it running?")

    # Load persistent configurations from Supabase through SQLAlchemy.
    saved_query = db.query(ModelConfig).filter(ModelConfig.owner_id == user.id)
    if enabled_only:
        saved_query = saved_query.filter(ModelConfig.enabled.is_(True))
    saved_models = saved_query.order_by(ModelConfig.provider, ModelConfig.model).all()

    # Use provider + model as the identity to avoid duplicate entries.
    saved_keys = set()

    for config in saved_models:
        key = (config.provider, config.model)
        saved_keys.add(key)

        is_default = (
            config.provider == s.llm_provider
            and (
                (
                    config.provider == "ollama"
                    and config.model == s.ollama_model
                )
                or (
                    config.provider == "external"
                    and config.model == s.external_api_model
                )
            )
        )

        item = {
            "id": config.id,
            "provider": config.provider,
            "model": config.model,
            "display_name": config.display_name,
            "enabled": config.enabled,
            "base_url": config.base_url,
            "default": is_default,
            "source": "registry",
            "secret_configured": secret_is_configured(config.secret_ref, config.encrypted_secret),
        }

        if config.provider == "ollama":
            item["available"] = config.model in live_ollama_models
        else:
            item["available"] = None

        # Never return secret_ref, API keys, or settings that may contain
        # private configuration values.
        items.append(item)

    # Include live Ollama models that haven't been saved in the registry.
    for name in sorted(live_ollama_models):
        if ("ollama", name) in saved_keys:
            continue

        items.append(
            {
                "id": None,
                "provider": "ollama",
                "model": name,
                "display_name": None,
                "enabled": True,
                "base_url": s.ollama_base_url,
                "default": (
                    s.llm_provider == "ollama"
                    and name == s.ollama_model
                ),
                "source": "live",
                "available": True,
                "secret_configured": False,
            }
        )

    # Keep environment-configured external models visible even when they
    # have not yet been saved in the registry.
    if s.external_api_key and s.external_api_model:
        if ("external", s.external_api_model) not in saved_keys:
            items.append(
                {
                    "id": None,
                    "provider": "external",
                    "model": s.external_api_model,
                    "display_name": None,
                    "enabled": True,
                    "base_url": s.external_api_base_url,
                    "default": s.llm_provider == "external",
                    "source": "environment",
                    "available": None,
                    "secret_configured": True,
                }
            )

    return {"models": items, "warnings": warnings}
