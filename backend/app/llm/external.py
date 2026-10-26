import os
from urllib.parse import urlparse

import httpx
from sqlalchemy import select

from app.config import get_settings
from app.llm.base import LLMResult, ProviderConfigError, ProviderError
from app.llm.http import post_json
from app.models import ModelConfig
from app.security.secrets import SecretConfigurationError, decrypt_secret

GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
_OPENAI_PREFIXES = ("gpt-", "chatgpt", "o1", "o3", "o4")


class ExternalLLMClient:
    """Adapter for OpenAI-compatible chat-completions APIs. The API key stays server-side."""

    def __init__(self, base_url=None, api_key=None, timeout=None,
                 transport: httpx.AsyncBaseTransport | None = None):
        s = get_settings()
        self.base_url = (base_url or s.external_api_base_url).rstrip("/")
        self.api_key = s.external_api_key if api_key is None else api_key
        self.timeout = timeout or s.request_timeout_seconds
        self.transport = transport
        self.temperature: float = 0
        self.max_tokens: int | None = None

    def configure_from_registry(self, db, owner_id: str, model: str) -> None:
        config = db.scalar(select(ModelConfig).where(
            ModelConfig.owner_id == owner_id,
            ModelConfig.provider == "external",
            ModelConfig.model == model,
        ))
        if config is None:
            return
        self.base_url = (config.base_url or self.base_url).rstrip("/")
        # Per-model settings (validated on save by schemas_registry) were previously ignored.
        settings = config.settings if isinstance(config.settings, dict) else {}
        if "temperature" in settings:
            self.temperature = settings["temperature"]
        if "max_tokens" in settings:
            self.max_tokens = settings["max_tokens"]
        if "timeout_seconds" in settings:
            self.timeout = float(settings["timeout_seconds"])
        if config.encrypted_secret:
            try:
                self.api_key = decrypt_secret(config.encrypted_secret)
            except SecretConfigurationError as exc:
                raise ProviderConfigError(str(exc)) from exc
        elif config.secret_ref:
            self.api_key = os.getenv(config.secret_ref, self.api_key)

    def _check_endpoint_matches_model(self, model: str) -> None:
        """Fail before sending a key to the wrong vendor (e.g. a Gemini key to api.openai.com)."""
        host = (urlparse(self.base_url).hostname or "").lower()
        name = model.lower()
        if name.startswith("gemini") and host.endswith("openai.com"):
            raise ProviderConfigError(
                f"external: '{model}' is a Gemini model but base_url points to OpenAI. "
                f"Set base_url to {GEMINI_OPENAI_BASE_URL}")
        if name.startswith(_OPENAI_PREFIXES) and host.endswith("googleapis.com"):
            raise ProviderConfigError(
                f"external: '{model}' is an OpenAI model but base_url points to Google. "
                "Set base_url to https://api.openai.com/v1")

    async def generate(self, prompt: str, model: str | None = None,
                       system_prompt: str | None = None) -> LLMResult:
        chosen = model or get_settings().external_api_model
        if not self.api_key:
            raise ProviderConfigError("external: EXTERNAL_API_KEY is not configured")
        if not chosen:
            raise ProviderConfigError("external: no model configured")
        self._check_endpoint_matches_model(chosen)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = {"model": chosen, "messages": messages, "temperature": self.temperature}
        if self.max_tokens:
            body["max_tokens"] = self.max_tokens
        data = await post_json(
            "external", f"{self.base_url}/chat/completions", timeout=self.timeout, transport=self.transport,
            headers={"Authorization": f"Bearer {self.api_key}"}, json_body=body)
        try:
            choice = data["choices"][0]
            message = choice["message"]
            content = message["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("external: unexpected response format") from exc
        finish = choice.get("finish_reason") if isinstance(choice, dict) else None
        if content is None or (isinstance(content, str) and not content.strip()):
            refusal = message.get("refusal") if isinstance(message, dict) else None
            if isinstance(refusal, str) and refusal.strip():
                content = refusal  # an explicit provider-side refusal is a legitimate model answer
            elif finish == "length":
                raise ProviderError("external: output was cut off before any text "
                                    "(finish_reason=length); raise max_tokens in the model settings")
            elif finish == "content_filter":
                raise ProviderError("external: response blocked by the provider's content filter")
        if not isinstance(content, str):
            raise ProviderError("external: non-text content returned")
        usage = data.get("usage") or {}
        return LLMResult(content, usage.get("prompt_tokens"), usage.get("completion_tokens"))
