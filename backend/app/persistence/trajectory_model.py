"""SQLAlchemy ORM model for trajectories."""
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, Index
from sqlalchemy.sql import func

from app.persistence.database import Base


class TrajectoryModel(Base):
    """Trajectory entity stored in SQLite."""

    __tablename__ = "trajectories"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    wall_width = Column(Float, nullable=False)
    wall_height = Column(Float, nullable=False)
    obstacles_json = Column(Text, nullable=False)
    waypoints_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_trajectories_created_at", "created_at"),
        Index("idx_trajectories_dimensions", "wall_width", "wall_height"),
    )
