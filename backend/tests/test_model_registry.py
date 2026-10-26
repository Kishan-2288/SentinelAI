from app.models import AuditEvent


def test_model_config_crud_toggle_and_disabled_run(client):
    body = {
        "provider": "ollama",
        "model": "registry-model",
        "display_name": "Registry model",
        "base_url": "http://localhost:11434",
        "secret_ref": "OLLAMA_TOKEN",
        "settings": {"temperature": 0.2, "max_tokens": 100},
    }
    created = client.post("/api/v1/model-configs", json=body)
    assert created.status_code == 201
    config = created.json()
    assert config["secret_configured"] is False
    assert "secret_ref" not in config

    disabled = client.post(f"/api/v1/model-configs/{config['id']}/disable")
    assert disabled.status_code == 200 and disabled.json()["enabled"] is False
    run = client.post("/api/v1/runs", json={
        "provider": "ollama", "model": "registry-model",
        "test_cases": [{"id": "case", "prompt": "hello"}],
    })
    assert run.status_code == 400 and "disabled" in run.json()["detail"]

    enabled = client.post(f"/api/v1/model-configs/{config['id']}/enable")
    assert enabled.status_code == 200 and enabled.json()["enabled"] is True
    assert client.get("/api/v1/models", params={"enabled_only": True}).status_code == 200


def test_model_config_rejects_raw_secrets_and_unsafe_urls(client):
    raw_secret = client.post("/api/v1/model-configs", json={
        "provider": "external", "model": "gpt", "secret_ref": "sk-raw-key",
    })
    assert raw_secret.status_code == 422
    insecure_url = client.post("/api/v1/model-configs", json={
        "provider": "external", "model": "gpt", "base_url": "http://api.example.com",
    })
    assert insecure_url.status_code == 422
    credentials_url = client.post("/api/v1/model-configs", json={
        "provider": "ollama", "model": "x", "base_url": "http://user:pass@localhost:11434",
    })
    assert credentials_url.status_code == 422


def test_model_config_audit_does_not_store_values(client, session_factory):
    response = client.post("/api/v1/model-configs", json={
        "provider": "ollama", "model": "audit-model", "secret_ref": "OPENAI_API_KEY",
    })
    assert response.status_code == 201
    with session_factory() as db:
        event = db.query(AuditEvent).filter_by(event_type="model_config_created").one()
        assert "OPENAI_API_KEY" not in str(event.payload)
        assert event.payload["fields"] == ["model", "provider", "secret_ref"]
