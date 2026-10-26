import os
import re
from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

RegistryProvider = Literal["ollama", "external"]
_SECRET_REF = re.compile(r"^[A-Z_][A-Z0-9_]*$")
_SETTING_TYPES = {
    "temperature": (int, float),
    "max_tokens": (int,),
    "timeout_seconds": (int, float),
}


def _validate_base_url(value: str | None, provider: str) -> str | None:
    if value is None:
        return None
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("base_url must be an absolute URL without credentials")
    if provider == "external" and parsed.scheme != "https":
        raise ValueError("External base_url must use https")
    return value


def _validate_settings(value: dict[str, Any]) -> dict[str, Any]:
    unknown = set(value) - set(_SETTING_TYPES)
    if unknown:
        raise ValueError(f"Unsupported settings: {', '.join(sorted(unknown))}")
    for name, setting in value.items():
        if isinstance(setting, bool) or not isinstance(setting, _SETTING_TYPES[name]):
            raise ValueError(f"{name} has an invalid value")
        if name == "temperature" and not 0 <= setting <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if name in ("max_tokens", "timeout_seconds") and setting <= 0:
            raise ValueError(f"{name} must be greater than 0")
    return value


class ModelConfigCreate(BaseModel):
    provider: RegistryProvider
    model: str = Field(min_length=1, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)
    enabled: bool = True
    base_url: str | None = Field(default=None, max_length=500)
    api_key: str | None = Field(default=None, min_length=1, max_length=5000, repr=False)
    secret_ref: str | None = Field(default=None, max_length=200)
    settings: dict[str, Any] = Field(default_factory=dict)

    @field_validator("secret_ref")
    @classmethod
    def validate_secret_ref(cls, value: str | None) -> str | None:
        if value is not None and (not _SECRET_REF.fullmatch(value) or value.startswith("SK-")):
            raise ValueError("secret_ref must be an environment variable name, not a raw secret")
        return value

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("api_key cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_configuration(self):
        _validate_base_url(self.base_url, self.provider)
        _validate_settings(self.settings)
        if self.api_key is not None and self.provider != "external":
            raise ValueError("api_key is only supported for the external provider")
        return self


class ModelConfigPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    display_name: str | None = Field(default=None, max_length=200)
    enabled: bool | None = None
    base_url: str | None = Field(default=None, max_length=500)
    api_key: str | None = Field(default=None, min_length=1, max_length=5000, repr=False)
    secret_ref: str | None = Field(default=None, max_length=200)
    settings: dict[str, Any] | None = None

    @field_validator("secret_ref")
    @classmethod
    def validate_secret_ref(cls, value: str | None) -> str | None:
        if value is not None and not _SECRET_REF.fullmatch(value):
            raise ValueError("secret_ref must be an environment variable name, not a raw secret")
        return value

    @field_validator("settings")
    @classmethod
    def validate_settings(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        return None if value is None else _validate_settings(value)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("api_key cannot be blank")
        return value


class ModelConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider: RegistryProvider
    model: str
    display_name: str | None
    enabled: bool
    base_url: str | None
    settings: dict[str, Any]
    secret_configured: bool


class ModelListItem(ModelConfigOut):
    source: Literal["registry", "live", "environment"]
    available: bool | None
    default: bool


class ModelListOut(BaseModel):
    models: list[ModelListItem]
    warnings: list[str]


def secret_is_configured(secret_ref: str | None, encrypted_secret: str | None = None) -> bool:
    return bool(encrypted_secret or (secret_ref and os.getenv(secret_ref)))
