"""Unit tests for coverage path planning algorithm."""
import pytest
from app.algorithms.coverage_planner import (
    WallConfig,
    Obstacle,
    plan_coverage_path,
    get_coverage_explanation,
    _get_visible_intervals,
)


def _segment_intersects_any_obstacle(
    x1: float, y1: float, x2: float, y2: float, obstacles: list
) -> bool:
    """Check if axis-aligned segment (x1,y1)-(x2,y2) intersects any obstacle."""
    eps = 1e-9
    for obs in obstacles:
        seg_x_lo, seg_x_hi = min(x1, x2), max(x1, x2)
        seg_y_lo, seg_y_hi = min(y1, y2), max(y1, y2)
        x_overlap = seg_x_hi >= obs.x - eps and seg_x_lo <= obs.x2 + eps
        y_overlap = seg_y_hi >= obs.y - eps and seg_y_lo <= obs.y2 + eps
        if x_overlap and y_overlap:
            return True
    return False


def test_empty_wall():
    """Path on empty wall should cover entire area with zigzag."""
    wall = WallConfig(width=5.0, height=5.0)
    waypoints, _ = plan_coverage_path(wall, [], sweep_height=0.25)
    assert len(waypoints) > 0
    # First point at left or right edge
    assert 0 <= waypoints[0][0] <= 5.0
    assert 0 <= waypoints[0][1] <= 5.0
    # All points within bounds
    for x, y in waypoints:
        assert 0 <= x <= 5.0
        assert 0 <= y <= 5.0


def test_wall_with_obstacle():
    """Path should avoid obstacle (25cm x 25cm window)."""
    wall = WallConfig(width=5.0, height=5.0)
    obstacle = Obstacle(x=2.0, y=2.0, width=0.25, height=0.25)
    waypoints, _ = plan_coverage_path(wall, [obstacle], sweep_height=0.25)

    # No waypoint inside obstacle
    for x, y in waypoints:
        in_obs = (
            obstacle.x <= x <= obstacle.x + obstacle.width
            and obstacle.y <= y <= obstacle.y + obstacle.height
        )
        assert not in_obs


def test_coverage_explanation():
    """Explanation should contain expected keys."""
    wall = WallConfig(width=5.0, height=5.0)
    obstacle = Obstacle(x=2.0, y=2.0, width=0.25, height=0.25)
    waypoints, _ = plan_coverage_path(wall, [obstacle])
    explanation = get_coverage_explanation(wall, [obstacle], waypoints)

    assert explanation["algorithm"] == "Zigzag (Boustrophedon) Coverage"
    assert explanation["total_area_m2"] == 25.0
    assert explanation["obstacle_area_m2"] == 0.0625
    assert explanation["covered_area_m2"] == pytest.approx(24.9375)
    assert explanation["waypoint_count"] == len(waypoints)
    assert "strip_count" in explanation


def test_visible_intervals_no_obstacles():
    """Free line with no obstacles returns full interval."""
    intervals = _get_visible_intervals(1.0, 5.0, [])
    assert intervals == [(0.0, 5.0)]


def test_visible_intervals_with_obstacle():
    """Obstacle in middle splits line into two intervals."""
    obstacle = Obstacle(x=2.0, y=0.5, width=1.0, height=1.0)
    intervals = _get_visible_intervals(1.0, 5.0, [obstacle])
    assert len(intervals) == 2
    assert intervals[0][0] == pytest.approx(0.0)
    assert intervals[0][1] == pytest.approx(2.0, abs=1e-5)
    assert intervals[1][0] == pytest.approx(3.0, abs=1e-5)
    assert intervals[1][1] == pytest.approx(5.0)


def test_no_path_segment_intersects_obstacle():
    """No line segment between consecutive waypoints should intersect any obstacle."""
    wall = WallConfig(width=5.0, height=5.0)
    obstacle = Obstacle(x=2.5, y=2.5, width=0.25, height=0.25)
    waypoints, _ = plan_coverage_path(wall, [obstacle], sweep_height=0.25)

    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        assert not _segment_intersects_any_obstacle(
            x1, y1, x2, y2, [obstacle]
        ), f"Segment ({x1},{y1})-({x2},{y2}) intersects obstacle"


def test_sample_case():
    """Sample case: 5m x 5m wall, 25cm x 25cm obstacle."""
    wall = WallConfig(width=5.0, height=5.0)
    obstacle = Obstacle(x=2.5, y=2.5, width=0.25, height=0.25)
    waypoints, _ = plan_coverage_path(wall, [obstacle], sweep_height=0.25)

    assert len(waypoints) > 10
    total_area = 5 * 5
    obs_area = 0.25 * 0.25
    expected_covered = total_area - obs_area
    explanation = get_coverage_explanation(wall, [obstacle], waypoints)
    assert explanation["covered_area_m2"] == pytest.approx(expected_covered)
