from dataclasses import dataclass
from typing import Protocol


class ProviderError(Exception):
    """A provider call failed. Messages are sanitised (never contain keys or prompts)."""
    def __init__(self, message: str, retryable: bool = False, retry_after: float | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.retry_after = retry_after  # seconds requested by the provider (Retry-After), if any


class ProviderConfigError(ProviderError):
    """Misconfiguration or rejected credentials: retrying cannot help and the run should abort."""
    def __init__(self, message: str):
        super().__init__(message, retryable=False)


@dataclass
class LLMResult:
    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class LLMClient(Protocol):
    async def generate(self, prompt: str, model: str | None = None,
                       system_prompt: str | None = None) -> LLMResult: ...
