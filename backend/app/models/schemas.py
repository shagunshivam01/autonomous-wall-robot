"""Pydantic schemas for API request/response."""
from datetime import datetime
from pydantic import BaseModel, Field


class WallConfig(BaseModel):
    """Wall dimensions in meters."""

    width: float = Field(gt=0, le=100, description="Wall width in meters")
    height: float = Field(gt=0, le=100, description="Wall height in meters")


class Obstacle(BaseModel):
    """Rectangular obstacle in meters. x,y is bottom-left corner."""

    x: float = Field(ge=0, description="X position (left edge)")
    y: float = Field(ge=0, description="Y position (bottom edge)")
    width: float = Field(gt=0, description="Obstacle width in meters")
    height: float = Field(gt=0, description="Obstacle height in meters")


class PathPlanningRequest(BaseModel):
    """Request body for path planning."""

    wall_config: WallConfig
    obstacles: list[Obstacle] = Field(default_factory=list)
    name: str = Field(default="Untitled Trajectory", max_length=255)
    sweep_height: float = Field(
        default=0.25,
        gt=0.01,
        le=1.0,
        description="Sweep height in meters"
    )
    overlap_ratio: float = Field(
        default=0.0,
        ge=0.0,
        lt=0.5,
        description="Fractional overlap between strips (e.g., 0.1 = 10%)"
    )


class Waypoint(BaseModel):
    """Single waypoint (x, y) in meters."""

    x: float
    y: float


class PathPlanningResponse(BaseModel):
    """Response from path planning endpoint."""

    trajectory_id: str
    waypoints: list[Waypoint]
    coverage_explanation: dict


class Trajectory(BaseModel):
    """Trajectory entity for API responses."""

    id: str
    name: str
    wall_config: WallConfig
    obstacles: list[Obstacle]
    waypoints: list[Waypoint]
    created_at: datetime


class TrajectoryListResponse(BaseModel):
    """Paginated list of trajectories."""

    items: list[Trajectory]
    total: int
    skip: int
    limit: int


class TrajectoryUpdate(BaseModel):
    """Request body for updating a trajectory."""

    name: str | None = Field(default=None, max_length=255)
    wall_config: WallConfig | None = None
    obstacles: list[Obstacle] | None = None
