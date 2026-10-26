import asyncio
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.llm.base import LLMClient, LLMResult, ProviderError
from app.llm.external import ExternalLLMClient
from app.models import ModelConfig
from app.llm.ollama import OllamaClient

PROVIDERS = ("ollama", "external")


def get_client(provider: str) -> LLMClient:
    if provider == "ollama":
        return OllamaClient()
    if provider == "external":
        return ExternalLLMClient()
    raise ValueError(f"Unsupported provider: {provider}")


def resolve_run_target(provider: str | None, model: str | None, *,
                       db: Session | None = None, owner_id: str | None = None) -> tuple[str, str]:
    """Validate provider/model BEFORE a run is queued. Raises ValueError with a safe message."""
    s = get_settings()
    provider = provider or s.llm_provider
    if provider == "ollama":
        chosen = model or s.ollama_model
    elif provider == "external":
        chosen = model or s.external_api_model
        if not chosen:
            raise ValueError("External provider needs a model (set EXTERNAL_API_MODEL or pass 'model')")
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    if db is not None and owner_id is not None:
        config = db.scalar(select(ModelConfig).where(
            ModelConfig.owner_id == owner_id,
            ModelConfig.provider == provider,
            ModelConfig.model == chosen,
        ))
        if config is not None:
            if not config.enabled:
                raise ValueError("Registered model is disabled")
            if provider == "external" and not (
                config.encrypted_secret or (config.secret_ref and os.getenv(config.secret_ref))
                or s.external_api_key
            ):
                raise ValueError("External model has no API key configured")
        elif provider == "external" and not s.external_api_key:
            raise ValueError("External provider is not configured (register an API key or set EXTERNAL_API_KEY)")
    return provider, chosen


async def generate_with_retry(client: LLMClient, *, prompt: str, model: str | None,
                              system_prompt: str | None, max_attempts: int,
                              backoff_seconds: float) -> tuple[LLMResult, int]:
    """Retry retryable ProviderErrors with exponential backoff. Returns (result, attempts)."""
    attempt = 0
    while True:
        attempt += 1
        try:
            return await client.generate(prompt, model=model, system_prompt=system_prompt), attempt
        except ProviderError as exc:
            if not exc.retryable or attempt >= max_attempts:
                raise
            await asyncio.sleep(backoff_seconds * (2 ** (attempt - 1)))
