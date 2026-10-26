import httpx

from app.llm.base import ProviderConfigError, ProviderError


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
        raise ProviderError(f"{provider}: temporary error (HTTP {code})", retryable=True)
    if code >= 400:
        raise ProviderError(f"{provider}: request rejected (HTTP {code}); check model name and parameters")
    try:
        data = response.json()
    except ValueError as exc:
        raise ProviderError(f"{provider}: response was not valid JSON") from exc
    if not isinstance(data, dict):
        raise ProviderError(f"{provider}: unexpected response format")
    return data
