"""Trajectory service - CRUD logic and validation."""
import json
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.schemas import (
    WallConfig,
    Obstacle,
    Waypoint,
    Trajectory,
    PathPlanningRequest,
)
from app.persistence.trajectory_repository import TrajectoryRepository
from app.services.path_planning_service import PathPlanningService


class TrajectoryService:
    """Trajectory business logic."""

    def __init__(self, db: Session):
        self.repo = TrajectoryRepository(db)
        self.planning_service = PathPlanningService()

    def plan_and_store(self, request: PathPlanningRequest) -> Trajectory:
        """
        Plan path, store trajectory, and return full trajectory.
        """
        waypoints, explanation = self.planning_service.plan_path(
            request.wall_config,
            request.obstacles,
            request.sweep_height,
        )
        trajectory_id = str(uuid.uuid4())
        obstacles_json = json.dumps([o.model_dump() for o in request.obstacles])
        waypoints_json = json.dumps([[w[0], w[1]] for w in waypoints])

        self.repo.create(
            id=trajectory_id,
            name=request.name,
            wall_width=request.wall_config.width,
            wall_height=request.wall_config.height,
            obstacles_json=obstacles_json,
            waypoints_json=waypoints_json,
        )

        return Trajectory(
            id=trajectory_id,
            name=request.name,
            wall_config=request.wall_config,
            obstacles=request.obstacles,
            waypoints=[Waypoint(x=w[0], y=w[1]) for w in waypoints],
            created_at=self.repo.get_by_id(trajectory_id).created_at,
        )

    def plan_and_store_with_explanation(
        self, request: PathPlanningRequest
    ) -> tuple[Trajectory, dict]:
        """Plan, store, and return trajectory plus coverage explanation."""
        
        waypoints, explanation = self.planning_service.plan_path(
            request.wall_config,
            request.obstacles,
            request.sweep_height,
            request.overlap_ratio,
        )

        trajectory_id = str(uuid.uuid4())
        obstacles_json = json.dumps([o.model_dump() for o in request.obstacles])
        waypoints_json = json.dumps([[w[0], w[1]] for w in waypoints])

        self.repo.create(
            id=trajectory_id,
            name=request.name,
            wall_width=request.wall_config.width,
            wall_height=request.wall_config.height,
            obstacles_json=obstacles_json,
            waypoints_json=waypoints_json,
        )

        entity = self.repo.get_by_id(trajectory_id)
        trajectory = self._entity_to_trajectory(entity)
        return trajectory, explanation

    def get_by_id(self, trajectory_id: str) -> Optional[Trajectory]:
        """Get trajectory by ID."""
        entity = self.repo.get_by_id(trajectory_id)
        return self._entity_to_trajectory(entity) if entity else None

    def list_trajectories(
        self,
        skip: int = 0,
        limit: int = 50,
        wall_width: Optional[float] = None,
        wall_height: Optional[float] = None,
    ) -> tuple[list[Trajectory], int]:
        """List trajectories with pagination and optional filters."""
        items, total = self.repo.list_trajectories(skip, limit, wall_width, wall_height)
        trajectories = [self._entity_to_trajectory(e) for e in items]
        return trajectories, total

    def update(
        self,
        trajectory_id: str,
        *,
        name: Optional[str] = None,
        wall_config: Optional[WallConfig] = None,
        obstacles: Optional[list[Obstacle]] = None,
    ) -> Optional[Trajectory]:
        """Update trajectory. Only provided fields are updated."""
        updates: dict = {}
        if name is not None:
            updates["name"] = name
        if wall_config is not None:
            updates["wall_width"] = wall_config.width
            updates["wall_height"] = wall_config.height
        if obstacles is not None:
            obs_data = [o.model_dump() for o in obstacles]
            updates["obstacles_json"] = json.dumps(obs_data)

        if not updates:
            return self.get_by_id(trajectory_id)

        entity = self.repo.update(trajectory_id, **updates)
        return self._entity_to_trajectory(entity) if entity else None

    def delete(self, trajectory_id: str) -> bool:
        """Delete trajectory."""
        return self.repo.delete(trajectory_id)

    def _entity_to_trajectory(self, entity) -> Trajectory:
        """Convert repository entity to API schema."""
        obstacles = [Obstacle(**o) for o in json.loads(entity.obstacles_json)]
        waypoints = [
            Waypoint(x=w[0], y=w[1]) for w in json.loads(entity.waypoints_json)
        ]
        return Trajectory(
            id=entity.id,
            name=entity.name,
            wall_config=WallConfig(width=entity.wall_width, height=entity.wall_height),
            obstacles=obstacles,
            waypoints=waypoints,
            created_at=entity.created_at,
        )
