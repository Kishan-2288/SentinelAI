import httpx
import os
from sqlalchemy import select

from app.config import get_settings
from app.llm.base import LLMResult, ProviderConfigError, ProviderError
from app.llm.http import post_json
from app.models import ModelConfig
from app.security.secrets import SecretConfigurationError, decrypt_secret


class ExternalLLMClient:
    """Adapter for OpenAI-compatible chat-completions APIs. The API key stays server-side."""

    def __init__(self, base_url=None, api_key=None, timeout=None,
                 transport: httpx.AsyncBaseTransport | None = None):
        s = get_settings()
        self.base_url = (base_url or s.external_api_base_url).rstrip("/")
        self.api_key = s.external_api_key if api_key is None else api_key
        self.timeout = timeout or s.request_timeout_seconds
        self.transport = transport

    def configure_from_registry(self, db, owner_id: str, model: str) -> None:
        config = db.scalar(select(ModelConfig).where(
            ModelConfig.owner_id == owner_id,
            ModelConfig.provider == "external",
            ModelConfig.model == model,
        ))
        if config is None:
            return
        self.base_url = (config.base_url or self.base_url).rstrip("/")
        if config.encrypted_secret:
            try:
                self.api_key = decrypt_secret(config.encrypted_secret)
            except SecretConfigurationError as exc:
                raise ProviderConfigError(str(exc)) from exc
        elif config.secret_ref:
            self.api_key = os.getenv(config.secret_ref, self.api_key)

    async def generate(self, prompt: str, model: str | None = None,
                       system_prompt: str | None = None) -> LLMResult:
        chosen = model or get_settings().external_api_model
        if not self.api_key:
            raise ProviderConfigError("external: EXTERNAL_API_KEY is not configured")
        if not chosen:
            raise ProviderConfigError("external: no model configured")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        data = await post_json(
            "external", f"{self.base_url}/chat/completions", timeout=self.timeout, transport=self.transport,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json_body={"model": chosen, "messages": messages, "temperature": 0})
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("external: unexpected response format") from exc
        if not isinstance(content, str):
            raise ProviderError("external: non-text content returned")
        usage = data.get("usage") or {}
        return LLMResult(content, usage.get("prompt_tokens"), usage.get("completion_tokens"))
