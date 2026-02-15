"""Pytest fixtures for API and algorithm tests."""
import os

import pytest
from fastapi.testclient import TestClient

# Use in-memory SQLite for tests before app import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app
from app.persistence.database import SessionLocal, get_db
from app.persistence.trajectory_model import TrajectoryModel


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Test client with test database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_plan_request():
    """Sample path planning request (5m x 5m wall, 25cm x 25cm obstacle)."""
    return {
        "wall_config": {"width": 5.0, "height": 5.0},
        "obstacles": [{"x": 2.0, "y": 2.0, "width": 0.25, "height": 0.25}],
        "name": "Test Trajectory",
        "sweep_height": 0.25,
    }
