import re

import httpx

from app.llm.base import ProviderConfigError, ProviderError

_SAFE_CODE = re.compile(r"[A-Za-z0-9_.-]{1,60}")


def _error_code(response: httpx.Response) -> str | None:
    """Short machine-readable error code (e.g. model_not_found, NOT_FOUND). Never the free-text
    message, which could echo prompt content."""
    try:
        data = response.json()
    except ValueError:
        return None
    if isinstance(data, list) and data:
        data = data[0]
    error = data.get("error") if isinstance(data, dict) else None
    if not isinstance(error, dict):
        return None
    for key in ("code", "status", "type"):
        value = error.get(key)
        if isinstance(value, str) and not value.isdigit() and _SAFE_CODE.fullmatch(value):
            return value
    return None


def _retry_after(response: httpx.Response) -> float | None:
    try:
        return max(0.0, float(response.headers.get("retry-after", "")))
    except ValueError:
        return None


async def post_json(provider: str, url: str, *, json_body: dict, headers: dict | None = None,
                    timeout: float, transport: httpx.AsyncBaseTransport | None = None) -> dict:
    """POST JSON and translate every failure into a sanitised ProviderError."""
    try:
        async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
            response = await client.post(url, json=json_body, headers=headers)
    except httpx.TimeoutException as exc:
        raise ProviderError(f"{provider}: request timed out", retryable=True) from exc
    except httpx.TransportError as exc:
        raise ProviderError(f"{provider}: connection failed ({type(exc).__name__})", retryable=True) from exc

    code = response.status_code
    if code in (401, 403):
        raise ProviderConfigError(f"{provider}: credentials rejected (HTTP {code})")
    if code == 429 or code >= 500:
        detail = _error_code(response)
        suffix = f", {detail}" if detail else ""
        raise ProviderError(f"{provider}: temporary error (HTTP {code}{suffix})", retryable=True,
                            retry_after=_retry_after(response))
    if code >= 400:
        detail = _error_code(response)
        suffix = f", {detail}" if detail else ""
        raise ProviderError(f"{provider}: request rejected (HTTP {code}{suffix}); check model name and parameters")
    try:
        data = response.json()
    except ValueError as exc:
        raise ProviderError(f"{provider}: response was not valid JSON") from exc
    if not isinstance(data, dict):
        raise ProviderError(f"{provider}: unexpected response format")
    return data
