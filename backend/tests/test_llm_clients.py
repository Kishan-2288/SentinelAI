import json

import httpx
import pytest

from app.llm.base import ProviderConfigError, ProviderError
from app.llm.external import ExternalLLMClient
from app.llm.ollama import OllamaClient
from app.llm.registry import generate_with_retry


def transport(handler):
    return httpx.MockTransport(handler)


async def test_ollama_parses_response_and_sends_system_prompt():
    seen = {}

    def handler(request):
        seen.update(json.loads(request.content))
        return httpx.Response(200, json={"message": {"content": "hi"}, "prompt_eval_count": 3, "eval_count": 4})

    r = await OllamaClient(transport=transport(handler)).generate("p", model="m", system_prompt="sys")
    assert (r.text, r.prompt_tokens, r.completion_tokens) == ("hi", 3, 4)
    assert seen["messages"][0]["role"] == "system"
    assert seen["messages"][0]["content"].startswith("sys\n\nConfidentiality rule:")
    assert seen["stream"] is False


async def test_external_parses_usage_and_sends_bearer():
    def handler(request):
        assert request.headers["authorization"] == "Bearer k"
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}],
                                         "usage": {"prompt_tokens": 1, "completion_tokens": 2}})

    r = await ExternalLLMClient(base_url="http://x/v1", api_key="k", transport=transport(handler)).generate("p", model="m")
    assert (r.text, r.prompt_tokens, r.completion_tokens) == ("ok", 1, 2)


async def test_external_requires_key_and_model():
    with pytest.raises(ProviderConfigError):
        await ExternalLLMClient(api_key="", transport=transport(lambda r: httpx.Response(200))).generate("p", model="m")
    with pytest.raises(ProviderConfigError):
        await ExternalLLMClient(api_key="k", transport=transport(lambda r: httpx.Response(200))).generate("p")


@pytest.mark.parametrize("status,retryable,config", [(429, True, False), (503, True, False),
                                                      (400, False, False), (401, False, True)])
async def test_status_mapping(status, retryable, config):
    c = ExternalLLMClient(base_url="http://x", api_key="secret-key", transport=transport(lambda r: httpx.Response(status)))
    with pytest.raises(ProviderError) as ei:
        await c.generate("p", model="m")
    assert ei.value.retryable is retryable and isinstance(ei.value, ProviderConfigError) is config
    assert "secret-key" not in str(ei.value)


async def test_timeout_is_retryable():
    def handler(request):
        raise httpx.ReadTimeout("slow")
    with pytest.raises(ProviderError) as ei:
        await OllamaClient(transport=transport(handler)).generate("p")
    assert ei.value.retryable


async def test_malformed_body():
    c = OllamaClient(transport=transport(lambda r: httpx.Response(200, json={"nope": 1})))
    with pytest.raises(ProviderError):
        await c.generate("p")


async def test_retry_helper_gives_up_after_max_attempts():
    class Always:
        n = 0
        async def generate(self, prompt, model=None, system_prompt=None):
            Always.n += 1
            raise ProviderError("down", retryable=True)
    with pytest.raises(ProviderError):
        await generate_with_retry(Always(), prompt="p", model=None, system_prompt=None, max_attempts=3, backoff_seconds=0)
    assert Always.n == 3


# --- external provider hardening (OpenAI GPT-4.1 mini / Gemini via OpenAI-compatible API) -----
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


async def test_gemini_model_on_openai_url_is_blocked_before_sending_key():
    sent = []
    c = ExternalLLMClient(base_url="https://api.openai.com/v1", api_key="k",
                          transport=transport(lambda r: sent.append(r) or httpx.Response(200)))
    with pytest.raises(ProviderConfigError, match="generativelanguage"):
        await c.generate("p", model="gemini-3.8-flash")
    assert sent == []  # the key never left the server


async def test_openai_model_on_google_url_is_blocked():
    c = ExternalLLMClient(base_url=GEMINI_URL, api_key="k", transport=transport(lambda r: httpx.Response(200)))
    with pytest.raises(ProviderConfigError, match="api.openai.com"):
        await c.generate("p", model="gpt-4.1-mini")


async def test_gemini_url_with_trailing_slash_hits_chat_completions():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    await ExternalLLMClient(base_url=GEMINI_URL, api_key="k", transport=transport(handler)).generate(
        "p", model="gemini-3.8-flash")
    assert seen["url"] == GEMINI_URL.rstrip("/") + "/chat/completions"


async def test_registered_model_settings_are_sent():
    seen = {}

    def handler(request):
        seen.update(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    c = ExternalLLMClient(base_url="http://x/v1", api_key="k", transport=transport(handler))
    c.temperature, c.max_tokens = 1, 512
    await c.generate("p", model="gpt-4.1-mini")
    assert seen["temperature"] == 1 and seen["max_tokens"] == 512


async def test_default_request_has_temperature_zero_and_no_max_tokens():
    seen = {}

    def handler(request):
        seen.update(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    await ExternalLLMClient(base_url="http://x/v1", api_key="k", transport=transport(handler)).generate("p", model="m")
    assert seen["temperature"] == 0 and "max_tokens" not in seen


@pytest.mark.parametrize("body,expected", [
    ({"error": {"code": "model_not_found", "message": "secret prompt text"}}, "model_not_found"),
    ([{"error": {"code": 404, "status": "NOT_FOUND", "message": "x"}}], "NOT_FOUND"),
])
async def test_400_series_error_includes_safe_code_but_not_message(body, expected):
    c = ExternalLLMClient(base_url="http://x/v1", api_key="k",
                          transport=transport(lambda r: httpx.Response(404, json=body)))
    with pytest.raises(ProviderError) as ei:
        await c.generate("p", model="m")
    assert expected in str(ei.value) and "secret prompt text" not in str(ei.value)
    assert not ei.value.retryable


@pytest.mark.parametrize("finish,needle", [("length", "max_tokens"), ("content_filter", "content filter")])
async def test_empty_content_gets_actionable_error(finish, needle):
    body = {"choices": [{"message": {"content": None}, "finish_reason": finish}]}
    c = ExternalLLMClient(base_url="http://x/v1", api_key="k", transport=transport(lambda r: httpx.Response(200, json=body)))
    with pytest.raises(ProviderError, match=needle):
        await c.generate("p", model="m")


async def test_provider_refusal_field_is_returned_as_the_answer():
    body = {"choices": [{"message": {"content": None, "refusal": "I'm sorry, I can't assist with that."}}]}
    c = ExternalLLMClient(base_url="http://x/v1", api_key="k", transport=transport(lambda r: httpx.Response(200, json=body)))
    assert (await c.generate("p", model="m")).text.startswith("I'm sorry")


async def test_retry_after_header_is_honoured(monkeypatch):
    c = ExternalLLMClient(base_url="http://x/v1", api_key="k",
                          transport=transport(lambda r: httpx.Response(429, headers={"retry-after": "7"})))
    with pytest.raises(ProviderError) as ei:
        await c.generate("p", model="m")
    assert ei.value.retryable and ei.value.retry_after == 7.0

    slept = []

    async def fake_sleep(seconds):
        slept.append(seconds)

    monkeypatch.setattr("app.llm.registry.asyncio.sleep", fake_sleep)
    with pytest.raises(ProviderError):
        await generate_with_retry(c, prompt="p", model="m", system_prompt=None, max_attempts=2, backoff_seconds=0)
    assert slept == [7.0]


def test_configure_from_registry_applies_base_url_and_settings(session_factory):
    from app.models import ModelConfig
    with session_factory() as db:
        db.add(ModelConfig(owner_id="u1", provider="external", model="gemini-3.8-flash", enabled=True,
                           base_url=GEMINI_URL, settings={"temperature": 1, "max_tokens": 2048, "timeout_seconds": 90}))
        db.commit()
        client = ExternalLLMClient(api_key="k")
        client.configure_from_registry(db, "u1", "gemini-3.8-flash")
    assert client.base_url == GEMINI_URL.rstrip("/")
    assert (client.temperature, client.max_tokens, client.timeout) == (1, 2048, 90.0)
