import json

import httpx
import pytest

from app.llm.base import ProviderConfigError, ProviderError
from app.llm.external import ExternalLLMClient
from app.llm.ollama import CONFIDENTIALITY_RULE, OllamaClient
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
    assert seen["messages"][0]["content"].startswith("sys\n\n")
    assert CONFIDENTIALITY_RULE in seen["messages"][0]["content"]
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
