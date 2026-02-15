
import pytest
from app.algorithms.coverage_planner import (
    WallConfig,
    Obstacle,
    plan_coverage_path,
    _get_detour_height,
    _path_is_clear
)

def test_vertical_preference():
    """
    Test that the planner chooses vertical sweep when it results in fewer interruptions.
    Setup: 
    - Wall 10x10.
    - Long horizontal obstacle (blocker) in the middle.
    - Horizontal sweep would be broken into 2 parts for many strips.
    - Vertical sweep would only be broken for the few strips overlapping the obstacle's width (but here height).
    
    Obstacle: x=1, y=4, width=8, height=1.
    Horizontal sweep (y from 0 to 10):
       y=4 to 5 intersects obstacle.
       If sweep_height=0.25, that's 4 strips interrupted.
       Wait, 8x1 obstacle.
       Horizontal: At y=4...5, the scan line (width 10) is blocked by obstacle (x=[1,9]).
       So line goes 0..1, gap, 9..10.
       It is interrupted in every strip from y=4 to y=5.
    
    Vertical sweep (x from 0 to 10):
       Scan lines are vertical.
       Obstacle is x=[1,9].
       It interrupts vertical strips from x=1 to x=9.
       That's many strips!
       
    Wait.
    Long horizontal obstacle.
    Horizontal sweep:
       Strips at y=4.0, 4.25, 4.5, 4.75 are interrupted. (4 strips).
       Other strips are clear.
    Vertical sweep:
       Strips at x=1.0, 1.25, ..., 9.0 are interrupted. (32 strips!).
    
    So for a LONG HORIZONTAL obstacle, Horizontal sweep is interrupted FEW times (only when y overlaps height 1).
    Vertical sweep is interrupted MANY times (when x overlaps width 8).
    
    So a Long Horizontal Obstacle favors HORIZONTAL sweep?
    No.
    Horizontal sweep:
       Scan line y.
       If obstacle overlaps y, line is broken.
       So for y in [4, 5], lines are broken.
       Total broken lines = height / sweep_height = 1 / 0.25 = 4.
    
    Vertical sweep:
       Scan line x.
       If obstacle overlaps x, line is broken.
       Obstacle x in [1, 9].
       Total broken lines = width / sweep_height = 8 / 0.25 = 32.
       
    So Horizontal is BETTER for Horizontal Obstacle.
    
    To force Vertical, we need a TALL VERTICAL obstacle.
    Obstacle: x=4, y=1, width=1, height=8.
    Horizontal sweep:
       Interrupted for y in [1, 9]. (8/0.25 = 32 strips).
    Vertical sweep:
       Interrupted for x in [4, 5]. (1/0.25 = 4 strips).
       
    So TALL obstacle -> Vertical sweep is better.
    """
    wall = WallConfig(10, 10)
    # Tall obstacle
    obs = Obstacle(x=4.5, y=1, width=1, height=8)
    
    waypoints, strips = plan_coverage_path(wall, [obs], sweep_height=1.0)
    
    # Check if vertical was chosen.
    # Vertical strips have width ~ sweep_height, height ~ wall.height
    first_strip = strips[0]
    
    # In vertical mode:
    # We transpose wall -> width=10, height=10.
    # We scan "x".
    # Strip rect: "x" is scan_pos.
    # width = strip_max - strip_min (approx sweep_height).
    # height = check_limit (wall.height).
    
    # In horizontal mode:
    # width = check_limit (wall.width).
    # height = strip_max - strip_min.
    
    # If vertical chosen: width should be small (1.0), height large (10.0).
    # If horizontal chosen: width large (10.0), height small (1.0).
    
    assert first_strip["width"] < 2.0
    assert first_strip["height"] > 9.0

def test_horizontal_preference():
    """
    Test that the planner chooses horizontal sweep for wide obstacles.
    """
    wall = WallConfig(10, 10)
    # Wide obstacle
    obs = Obstacle(x=1, y=4.5, width=8, height=1)
    
    waypoints, strips = plan_coverage_path(wall, [obs], sweep_height=1.0)
    
    # Expect horizontal
    first_strip = strips[0]
    assert first_strip["width"] > 9.0
    assert first_strip["height"] < 2.0

def test_detour_optimization_direct_call():
    """
    Verify _get_detour_height returns y if path is clear.
    """
    wall = WallConfig(10, 10)
    obstacles = [Obstacle(x=2, y=2, width=1, height=1)]
    
    # Path far above obstacle
    y = 5.0
    # _path_is_clear((0,5), (10,5), obs) -> True
    
    detour = _get_detour_height(0, 10, y, obstacles)
    assert detour == y
    
    # Path blocked by obstacle
    y = 2.5 # Middle of obstacle
    # _path_is_clear -> False
    # Should lift to obstacle top (3.0) + clearance (0.01)
    
    detour = _get_detour_height(0, 10, y, obstacles)
    assert detour == pytest.approx(3.01)
