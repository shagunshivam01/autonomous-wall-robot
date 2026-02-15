"""Path planning service - orchestrates algorithm and explanation."""
import json
import uuid
from typing import Any

from app.algorithms.coverage_planner import (
    WallConfig as AlgoWallConfig,
    Obstacle as AlgoObstacle,
    plan_coverage_path,
    get_coverage_explanation,
)
from app.models.schemas import WallConfig, Obstacle


class PathPlanningService:
    """Orchestrates coverage path planning and explanation generation."""

    def plan_path(
        self,
        wall_config: WallConfig,
        obstacles: list[Obstacle],
        sweep_height: float = 0.25,
        overlap_ratio: float = 0.0,
    ) -> tuple[list[tuple[float, float]], dict[str, Any]]:

        """
        Plan coverage path and return waypoints plus explanation.

        Returns:
            (waypoints, explanation_dict)
        """
        algo_wall = AlgoWallConfig(width=wall_config.width, height=wall_config.height)
        algo_obstacles = [
            AlgoObstacle(x=o.x, y=o.y, width=o.width, height=o.height) for o in obstacles
        ]
        waypoints, strip_rectangles = plan_coverage_path(
            algo_wall,
            algo_obstacles,
            sweep_height,
            overlap_ratio=overlap_ratio,
        )
        
        explanation = get_coverage_explanation(
            algo_wall,
            algo_obstacles,
            waypoints,
            sweep_height,
            overlap_ratio,
        )
        explanation["sweep_rectangles"] = strip_rectangles

        return waypoints, explanation
