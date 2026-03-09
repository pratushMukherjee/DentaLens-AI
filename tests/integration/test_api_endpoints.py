"""Integration tests for FastAPI endpoints using TestClient."""

import pytest

try:
    from fastapi.testclient import TestClient
    from dentalens.api.app import create_app
    _IMPORTS_AVAILABLE = True
except Exception:
    _IMPORTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _IMPORTS_AVAILABLE, reason="ChromaDB incompatible with Python 3.14+")


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_readiness_check(client):
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_list_plans(client):
    response = client.get("/api/v1/benefits/plans")
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 3
    plan_ids = [p["plan_id"] for p in plans]
    assert "DD-PPO-GOLD-2024" in plan_ids


def test_get_plan_by_id(client):
    response = client.get("/api/v1/benefits/plans/DD-PPO-GOLD-2024")
    assert response.status_code == 200
    plan = response.json()
    assert plan["plan_name"] == "Delta Dental PPO Gold"
    assert plan["annual_maximum"] == 2000


def test_get_plan_not_found(client):
    response = client.get("/api/v1/benefits/plans/NONEXISTENT")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_list_claims(client):
    response = client.get("/api/v1/claims?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "claims" in data
    assert len(data["claims"]) <= 10


def test_list_claims_filtered_by_status(client):
    response = client.get("/api/v1/claims?status=denied&limit=5")
    assert response.status_code == 200
    data = response.json()
    for claim in data["claims"]:
        assert claim["claim_status"] == "denied"


def test_claims_summary(client):
    response = client.get("/api/v1/claims/analysis/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_claims"] > 0
    assert "approval_rate" in data
    assert "status_counts" in data


def test_claims_anomalies(client):
    response = client.get("/api/v1/claims/analysis/anomalies")
    assert response.status_code == 200
    anomalies = response.json()
    assert isinstance(anomalies, list)
    if anomalies:
        assert "claim_id" in anomalies[0]
        assert "reason" in anomalies[0]
