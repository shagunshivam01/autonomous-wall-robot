"""Repository for trajectory CRUD operations."""
import json
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.persistence.trajectory_model import TrajectoryModel


class TrajectoryRepository:
    """Persistence layer for trajectories."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        id: str,
        name: str,
        wall_width: float,
        wall_height: float,
        obstacles_json: str,
        waypoints_json: str,
    ) -> TrajectoryModel:
        """Create a new trajectory."""
        entity = TrajectoryModel(
            id=id,
            name=name,
            wall_width=wall_width,
            wall_height=wall_height,
            obstacles_json=obstacles_json,
            waypoints_json=waypoints_json,
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_by_id(self, trajectory_id: str) -> Optional[TrajectoryModel]:
        """Get trajectory by ID."""
        return self.db.query(TrajectoryModel).filter(TrajectoryModel.id == trajectory_id).first()

    def list_trajectories(
        self,
        skip: int = 0,
        limit: int = 50,
        wall_width: Optional[float] = None,
        wall_height: Optional[float] = None,
    ) -> tuple[list[TrajectoryModel], int]:
        """List trajectories with optional filters and pagination."""
        query = self.db.query(TrajectoryModel)
        if wall_width is not None:
            query = query.filter(TrajectoryModel.wall_width == wall_width)
        if wall_height is not None:
            query = query.filter(TrajectoryModel.wall_height == wall_height)
        total = query.count()
        items = query.order_by(desc(TrajectoryModel.created_at)).offset(skip).limit(limit).all()
        return items, total

    def update(
        self,
        trajectory_id: str,
        *,
        name: Optional[str] = None,
        wall_width: Optional[float] = None,
        wall_height: Optional[float] = None,
        obstacles_json: Optional[str] = None,
        waypoints_json: Optional[str] = None,
    ) -> Optional[TrajectoryModel]:
        """Update a trajectory."""
        entity = self.get_by_id(trajectory_id)
        if not entity:
            return None
        if name is not None:
            entity.name = name
        if wall_width is not None:
            entity.wall_width = wall_width
        if wall_height is not None:
            entity.wall_height = wall_height
        if obstacles_json is not None:
            entity.obstacles_json = obstacles_json
        if waypoints_json is not None:
            entity.waypoints_json = waypoints_json
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, trajectory_id: str) -> bool:
        """Delete a trajectory. Returns True if deleted."""
        entity = self.get_by_id(trajectory_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
