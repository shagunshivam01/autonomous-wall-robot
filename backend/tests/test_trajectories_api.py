"""API tests for trajectory CRUD and plan endpoints."""
import time
import pytest
from fastapi.testclient import TestClient


def test_plan_path(client: TestClient, sample_plan_request):
    """Test POST /api/v1/trajectories/plan."""
    start = time.perf_counter()
    resp = client.post("/api/v1/trajectories/plan", json=sample_plan_request)
    duration_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code == 200
    data = resp.json()
    assert "trajectory_id" in data
    assert "waypoints" in data
    assert "coverage_explanation" in data
    assert isinstance(data["waypoints"], list)
    assert len(data["waypoints"]) > 0
    assert data["coverage_explanation"]["algorithm"] == "Zigzag (Boustrophedon) Coverage"
    assert duration_ms < 1000


def test_list_trajectories(client: TestClient, sample_plan_request):
    """Test GET /api/v1/trajectories."""
    client.post("/api/v1/trajectories/plan", json=sample_plan_request)

    start = time.perf_counter()
    resp = client.get("/api/v1/trajectories")
    duration_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert duration_ms < 500


def test_get_trajectory(client: TestClient, sample_plan_request):
    """Test GET /api/v1/trajectories/{id}."""
    plan_resp = client.post("/api/v1/trajectories/plan", json=sample_plan_request)
    trajectory_id = plan_resp.json()["trajectory_id"]

    start = time.perf_counter()
    resp = client.get(f"/api/v1/trajectories/{trajectory_id}")
    duration_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == trajectory_id
    assert data["name"] == "Test Trajectory"
    assert "waypoints" in data
    assert "wall_config" in data
    assert duration_ms < 200


def test_get_trajectory_not_found(client: TestClient):
    """Test GET /api/v1/trajectories/{id} for non-existent ID."""
    resp = client.get("/api/v1/trajectories/non-existent-id")
    assert resp.status_code == 404


def test_update_trajectory(client: TestClient, sample_plan_request):
    """Test PUT /api/v1/trajectories/{id}."""
    plan_resp = client.post("/api/v1/trajectories/plan", json=sample_plan_request)
    trajectory_id = plan_resp.json()["trajectory_id"]

    resp = client.put(
        f"/api/v1/trajectories/{trajectory_id}",
        json={"name": "Updated Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


def test_update_trajectory_not_found(client: TestClient):
    """Test PUT /api/v1/trajectories/{id} for non-existent ID."""
    resp = client.put(
        "/api/v1/trajectories/non-existent-id",
        json={"name": "Updated"},
    )
    assert resp.status_code == 404


def test_delete_trajectory(client: TestClient, sample_plan_request):
    """Test DELETE /api/v1/trajectories/{id}."""
    plan_resp = client.post("/api/v1/trajectories/plan", json=sample_plan_request)
    trajectory_id = plan_resp.json()["trajectory_id"]

    resp = client.delete(f"/api/v1/trajectories/{trajectory_id}")
    assert resp.status_code == 204

    get_resp = client.get(f"/api/v1/trajectories/{trajectory_id}")
    assert get_resp.status_code == 404


def test_delete_trajectory_not_found(client: TestClient):
    """Test DELETE /api/v1/trajectories/{id} for non-existent ID."""
    resp = client.delete("/api/v1/trajectories/non-existent-id")
    assert resp.status_code == 404


def test_health(client: TestClient):
    """Test health endpoint."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
