"""Trajectory API controller."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import (
    PathPlanningRequest,
    PathPlanningResponse,
    Trajectory,
    TrajectoryListResponse,
    TrajectoryUpdate,
    Waypoint,
)
from app.persistence.database import get_db
from app.services.trajectory_service import TrajectoryService

router = APIRouter(prefix="/api/v1/trajectories", tags=["trajectories"])


def get_trajectory_service(db: Session = Depends(get_db)) -> TrajectoryService:
    return TrajectoryService(db)


@router.post("/plan", response_model=PathPlanningResponse)
def plan_path(
    request: PathPlanningRequest,
    service: TrajectoryService = Depends(get_trajectory_service),
):
    """
    Plan coverage path, store trajectory, and return waypoints with explanation.
    """
    trajectory, explanation = service.plan_and_store_with_explanation(request)
    return PathPlanningResponse(
        trajectory_id=trajectory.id,
        waypoints=trajectory.waypoints,
        coverage_explanation=explanation,
    )


@router.get("", response_model=TrajectoryListResponse)
def list_trajectories(
    skip: int = 0,
    limit: int = 50,
    wall_width: float | None = None,
    wall_height: float | None = None,
    service: TrajectoryService = Depends(get_trajectory_service),
):
    """
    List trajectories with pagination and optional dimension filters.
    """
    items, total = service.list_trajectories(
        skip=skip, limit=limit, wall_width=wall_width, wall_height=wall_height
    )
    return TrajectoryListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{trajectory_id}", response_model=Trajectory)
def get_trajectory(
    trajectory_id: str,
    service: TrajectoryService = Depends(get_trajectory_service),
):
    """Get trajectory by ID."""
    trajectory = service.get_by_id(trajectory_id)
    if not trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")
    return trajectory


@router.put("/{trajectory_id}", response_model=Trajectory)
def update_trajectory(
    trajectory_id: str,
    payload: TrajectoryUpdate,
    service: TrajectoryService = Depends(get_trajectory_service),
):
    """Update trajectory."""
    trajectory = service.update(
        trajectory_id,
        name=payload.name,
        wall_config=payload.wall_config,
        obstacles=payload.obstacles,
    )
    if not trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")
    return trajectory


@router.delete("/{trajectory_id}", status_code=204)
def delete_trajectory(
    trajectory_id: str,
    service: TrajectoryService = Depends(get_trajectory_service),
):
    """Delete trajectory."""
    if not service.delete(trajectory_id):
        raise HTTPException(status_code=404, detail="Trajectory not found")
