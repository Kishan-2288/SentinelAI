from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit import append_event
from app.database import get_db
from app.models import ModelConfig
from app.schemas_registry import ModelConfigCreate, ModelConfigOut, ModelConfigPatch, secret_is_configured
from app.security.secrets import SecretConfigurationError, encrypt_secret
from app.security.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/api/v1/model-configs", tags=["model-configs"])


def _out(config: ModelConfig) -> ModelConfigOut:
    return ModelConfigOut(
        id=config.id, provider=config.provider, model=config.model,
        display_name=config.display_name, enabled=config.enabled, base_url=config.base_url,
        settings=config.settings,
        secret_configured=secret_is_configured(config.secret_ref, config.encrypted_secret),
    )


def _get_owned(db: Session, config_id: int, owner_id: str) -> ModelConfig:
    config = db.scalar(select(ModelConfig).where(ModelConfig.id == config_id,
                                                  ModelConfig.owner_id == owner_id))
    if config is None:
        raise HTTPException(status_code=404, detail="Model config not found")
    return config


@router.get("", response_model=list[ModelConfigOut])
def list_model_configs(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    configs = db.scalars(select(ModelConfig).where(ModelConfig.owner_id == user.id)
                         .order_by(ModelConfig.provider, ModelConfig.model)).all()
    return [_out(config) for config in configs]


@router.post("", response_model=ModelConfigOut, status_code=201)
def create_model_config(payload: ModelConfigCreate, db: Session = Depends(get_db),
                        user: CurrentUser = Depends(get_current_user)):
    values = payload.model_dump(exclude={"api_key"})
    if payload.api_key:
        try:
            values["encrypted_secret"] = encrypt_secret(payload.api_key)
        except SecretConfigurationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    config = ModelConfig(owner_id=user.id, **values)
    db.add(config)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Model is already registered for this tenant") from exc
    append_event(db, "model_config_created", {
        "owner_id": user.id, "model_config_id": config.id,
        "fields": sorted(payload.model_fields_set),
    })
    return _out(config)


@router.get("/{config_id}", response_model=ModelConfigOut)
def get_model_config(config_id: int, db: Session = Depends(get_db),
                     user: CurrentUser = Depends(get_current_user)):
    return _out(_get_owned(db, config_id, user.id))


@router.patch("/{config_id}", response_model=ModelConfigOut)
def update_model_config(config_id: int, payload: ModelConfigPatch, db: Session = Depends(get_db),
                        user: CurrentUser = Depends(get_current_user)):
    config = _get_owned(db, config_id, user.id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return _out(config)
    api_key = changes.pop("api_key", None)
    if api_key:
        try:
            changes["encrypted_secret"] = encrypt_secret(api_key)
        except SecretConfigurationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    if "base_url" in changes:
        from app.schemas_registry import _validate_base_url
        changes["base_url"] = _validate_base_url(changes["base_url"], config.provider)
    changes = {field: value for field, value in changes.items()
               if getattr(config, field) != value}
    if not changes:
        return _out(config)
    for field, value in changes.items():
        setattr(config, field, value)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Model config update conflicts with existing data") from exc
    append_event(db, "model_config_updated", {
        "owner_id": user.id, "model_config_id": config.id, "fields": sorted(changes),
    })
    return _out(config)


def _set_enabled(config_id: int, enabled: bool, db: Session, user: CurrentUser) -> ModelConfigOut:
    config = _get_owned(db, config_id, user.id)
    if config.enabled == enabled:
        return _out(config)
    config.enabled = enabled
    append_event(db, "model_config_enabled" if enabled else "model_config_disabled", {
        "owner_id": user.id, "model_config_id": config.id, "fields": ["enabled"],
    })
    return _out(config)


@router.post("/{config_id}/enable", response_model=ModelConfigOut)
def enable_model_config(config_id: int, db: Session = Depends(get_db),
                        user: CurrentUser = Depends(get_current_user)):
    return _set_enabled(config_id, True, db, user)


@router.post("/{config_id}/disable", response_model=ModelConfigOut)
def disable_model_config(config_id: int, db: Session = Depends(get_db),
                         user: CurrentUser = Depends(get_current_user)):
    return _set_enabled(config_id, False, db, user)
