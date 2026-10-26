import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["EXTERNAL_API_KEY"] = ""
os.environ["EXTERNAL_API_MODEL"] = ""
os.environ["LLM_RETRY_BACKOFF_SECONDS"] = "0"
os.environ["LLM_MAX_ATTEMPTS"] = "3"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.llm.base import LLMResult, ProviderError
from app.main import app
from app.security.auth import CurrentUser, get_current_user


@pytest.fixture()
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path/'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    yield factory
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="local-dev",
    )
    app.state.session_factory = session_factory
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class FakeClient:
    """Scriptable LLM. `script` maps a substring of the prompt to a str or Exception (or list of them,
    consumed in order, the last item repeating)."""
    def __init__(self, script=None, default="A database index helps find rows efficiently."):
        self.script, self.default, self.calls = script or {}, default, {}

    async def generate(self, prompt, model=None, system_prompt=None):
        for key, behaviour in self.script.items():
            if key in prompt:
                n = self.calls.get(key, 0)
                self.calls[key] = n + 1
                if isinstance(behaviour, list):
                    behaviour = behaviour[min(n, len(behaviour) - 1)]
                if isinstance(behaviour, Exception):
                    raise behaviour
                return LLMResult(behaviour, 5, 7)
        return LLMResult(self.default, 5, 7)


@pytest.fixture()
def use_fake(monkeypatch):
    def _use(fake):
        monkeypatch.setattr("app.services.run_service.get_client", lambda provider: fake)
        return fake
    return _use


__all__ = ["FakeClient", "ProviderError"]
