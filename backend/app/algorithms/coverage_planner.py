"""Coverage path planning using zigzag (boustrophedon) pattern with obstacle avoidance."""
from dataclasses import dataclass
from typing import Sequence, List, Tuple
import math

@dataclass
class WallConfig:
    """Wall dimensions in meters."""

    width: float
    height: float


@dataclass
class Obstacle:
    """Rectangular obstacle in meters. x,y is bottom-left corner."""

    x: float
    y: float
    width: float
    height: float

    @property
    def x2(self) -> float:
        return self.x + self.width

    @property
    def y2(self) -> float:
        return self.y + self.height


def _segment_intersects_obstacle(
    x1: float, y1: float, x2: float, y2: float, obstacles: Sequence[Obstacle]
) -> bool:
    """Check if horizontal segment (y1 == y2) intersects any obstacle."""
    y = y1
    x_min, x_max = min(x1, x2), max(x1, x2)
    for obs in obstacles:
        # Segment overlaps vertically with obstacle
        if y >= obs.y and y <= obs.y2:
            # Check horizontal overlap
            if x_max > obs.x and x_min < obs.x2:
                return True
    return False


DETOUR_CLEARANCE = 0.01  # meters above obstacle top


def _get_detour_height(
    x_start: float, x_end: float, y: float, obstacles: Sequence[Obstacle]
) -> float:
    """
    Compute minimum safe height above obstacles in the x-range [x_start, x_end]
    that overlap the horizontal strip at y. Returns y + clearance above the highest such obstacle.
    """
    # Optimization: if direct path is clear, don't detour
    if _path_is_clear((x_start, y), (x_end, y), obstacles):
        return y

    x_min, x_max = min(x_start, x_end), max(x_start, x_end)
    max_y2 = y
    for obs in obstacles:
        if y >= obs.y and y <= obs.y2:
            if x_max > obs.x and x_min < obs.x2:
                max_y2 = max(max_y2, obs.y2)
    return max_y2 + DETOUR_CLEARANCE


def _path_is_clear(
    p1: tuple[float, float], p2: tuple[float, float], obstacles: Sequence[Obstacle]
) -> bool:
    """Check if the straight line segment between p1 and p2 intersects any obstacle."""
    # Simple check for now: check if bounding box intersects.
    # For a more robust check, we should do line segment intersection.
    # Here, since moves are either horizontal or vertical-ish detours, we can use a simpler check or the full segment check.
    # Let's use the segment check logic similar to _segment_intersects_obstacle but general.
    x1, y1 = p1
    x2, y2 = p2
    
    # Bounding box of segment
    seg_min_x, seg_max_x = min(x1, x2), max(x1, x2)
    seg_min_y, seg_max_y = min(y1, y2), max(y1, y2)

    for obs in obstacles:
        # Quick bounding box rejection
        if (seg_max_x < obs.x or seg_min_x > obs.x2 or
            seg_max_y < obs.y or seg_min_y > obs.y2):
            continue
            
        # Detailed intersection check could go here if needed.
        # For the specific case of "detour height" vs "direct path", 
        # usually we are moving from (x1, y) to (x2, y) but need to jump over something?
        # Actually _get_detour_height is called when there IS an obstacle between x1 and x2 at height y.
        # But we might be able to go straight if the "obstacle" passed to _get_detour_height isn't actually blocking the line *at that specific y*.
        # Wait, _get_detour_height is called when we know there is a gap.
        
        # Re-reading logic: _get_detour_height is called when we have to move from prev_last_x to first_x
        # and there are obstacles in between (gap detected).
        # But maybe the gap is just empty space?
        # The previous logic assumed if there is a gap in intervals, it MUST be due to an obstacle.
        # That is true because _get_visible_intervals only returns free space.
        # So if there is a gap between free spaces, there is an obstacle.
        
        # HOWEVER, the "detour" might not need to go all the way to max_y2 + clearance
        # if the obstacle is actually *below* the current y?
        # No, the scan line is AT y. so obstacles in the gap definitely overlap y.
        # So we MUST go above (or below) them.
        # The only optimization is if we can go *under*? But the brush is painting at y.
        # We probably shouldn't paint over the obstacle.
        # 
        # Actually, the optimization request says:
        # "Optimizing detour paths to reduce travel distance."
        # "Add a check: if the direct path between two points does not intersect any obstacle, use the direct path."
        # 
        # When does this happen?
        # If we are at (x1, y) and need to go to (x2, y), and there is a "gap" in coverage...
        # The gap implies we CANNOT paint there.
        # But can we MOVE there without painting?
        # If the obstacle is "paintable but shouldn't be painted"? No, obstacle usually means physical obstruction.
        # If it's a window, we can't paint it. Can we move over it?
        # If it's a window, yes, maybe we can move the arm over it without the brush touching.
        # But `Obstacle` usually implies collision object.
        #
        # Let's assume obstacles are physical protrusions we can't touch.
        # But maybe the "gap" is caused by an obstacle that is *short*?
        # No, we check `y >= obs.y and y <= obs.y2`.
        
        # So, if we are at y, and obstacle is at y, we cannot go straight through.
        # We MUST detour.
        #
        # OPTIMIZATION:
        # Maybe the previous logic `max_y2` took the max top of *all* obstacles in the x-range.
        return False

    return True



def _get_visible_intervals(
    y: float, wall_width: float, obstacles: Sequence[Obstacle]
) -> list[tuple[float, float]]:
    """
    For a horizontal line at y, return list of (start_x, end_x) intervals
    that are free of obstacles. Obstacles occlude parts of the line.
    """
    occlusions: list[tuple[float, float]] = []
    for obs in obstacles:
        if y >= obs.y and y <= obs.y2:
            occlusions.append((obs.x, obs.x2))
    if not occlusions:
        return [(0.0, wall_width)]

    # Sort by x and merge overlapping; use small epsilon to exclude boundary
    eps = 1e-6
    occlusions.sort(key=lambda t: t[0])
    merged: list[tuple[float, float]] = [occlusions[0]]
    for a, b in occlusions[1:]:
        if a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))

    # Invert to get free intervals; exclude obstacle boundaries
    intervals: list[tuple[float, float]] = []
    cur = 0.0
    for a, b in merged:
        if cur < a - eps and cur < wall_width:
            end = min(a - eps, wall_width)
            if end > cur:
                intervals.append((cur, end))
        cur = max(cur, b + eps)
    if cur < wall_width:
        intervals.append((cur, wall_width))
    return intervals


def _calculate_interruptions(
    wall: WallConfig,
    obstacles: Sequence[Obstacle],
    sweep_height: float,
    overlap_ratio: float,
    vertical: bool = False
) -> int:
    """
    Simulate the path and count how many times the sweep is interrupted by obstacles.
    """
    effective_step = sweep_height * (1 - overlap_ratio)
    effective_step = max(effective_step, 1e-6)
    
    if vertical:
        # Transpose logic: width become height, height becomes width
        search_limit = wall.width
        check_limit = wall.height
    else:
        search_limit = wall.height
        check_limit = wall.width

    num_strips = math.ceil(search_limit / effective_step)
    interruptions = 0

    for strip_index in range(num_strips):
        pos = (strip_index * effective_step) + sweep_height / 2
        
        if pos > search_limit:
            break
            
        relevant_obstacles = []
        for obs in obstacles:
            if vertical:
                # Vertical scan: pos is x-coordinate. Check if obs overlaps x.
                if pos >= obs.x and pos <= obs.x2:
                    relevant_obstacles.append(obs)
            else:
                # Horizontal scan: pos is y-coordinate. Check if obs overlaps y.
                if pos >= obs.y and pos <= obs.y2:
                    relevant_obstacles.append(obs)
        
        if not relevant_obstacles:
            continue

        occlusions = []
        for obs in relevant_obstacles:
            if vertical:
                occlusions.append((obs.y, obs.y2))
            else:
                occlusions.append((obs.x, obs.x2))
        
        if not occlusions:
            continue
            
        occlusions.sort(key=lambda t: t[0])
        merged = [occlusions[0]]
        for a, b in occlusions[1:]:
            if a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else:
                merged.append((a, b))
        
        segments = 0
        current_pos = 0.0
        eps = 1e-6
        limit = check_limit
        
        for a, b in merged:
            if a > current_pos + eps:
                segments += 1
            current_pos = max(current_pos, b)
            
        if current_pos < limit - eps:
            segments += 1
            
        interruptions += segments

    return interruptions


def plan_coverage_path(
    wall: WallConfig,
    obstacles: Sequence[Obstacle],
    sweep_height: float = 0.25,
    overlap_ratio: float = 0.0,
) -> tuple[list[tuple[float, float]], list[dict]]:
    """
    Plan coverage path using zigzag (boustrophedon) pattern.

    Args:
        wall: Wall dimensions in meters
        obstacles: List of rectangular obstacles
        sweep_height: Vertical spacing between strips in meters (default 25cm)

    Returns:
        Ordered list of (x, y) waypoints
    """
    waypoints: list[tuple[float, float]] = []
    strip_rectangles: list[dict] = []

    effective_step = sweep_height * (1 - overlap_ratio)
    effective_step = max(effective_step, 1e-6)  # prevent zero step

    # 1. Decide direction
    # Calculate interruptions for horizontal scan
    h_interruptions = _calculate_interruptions(wall, obstacles, sweep_height, overlap_ratio, vertical=False)
    # Calculate interruptions for vertical scan
    v_interruptions = _calculate_interruptions(wall, obstacles, sweep_height, overlap_ratio, vertical=True)
    
    use_vertical = v_interruptions < h_interruptions

    # If vertical, transpose the problem space
    if use_vertical:
        # Swap wall dimensions
        search_limit = wall.width
        check_limit = wall.height
        # Transpose obstacles: x<->y, w<->h
        transposed_obstacles = [
            Obstacle(x=obs.y, y=obs.x, width=obs.height, height=obs.width)
            for obs in obstacles
        ]
        active_obstacles = transposed_obstacles
    else:
        search_limit = wall.height
        check_limit = wall.width
        active_obstacles = obstacles

    num_strips = math.ceil(search_limit / effective_step)

    left_to_right = True 
    for strip_index in range(num_strips):
        scan_pos = (strip_index * effective_step) + sweep_height / 2
        
        strip_min = max(0.0, scan_pos - sweep_height / 2)
        strip_max = min(search_limit, scan_pos + sweep_height / 2)

        # Record the strip area (for visualization/debugging)
        if use_vertical:
             strip_rectangles.append({
                "x": strip_min,
                "y": 0.0,
                "width": strip_max - strip_min,
                "height": check_limit,
            })
        else:
            strip_rectangles.append({
                "x": 0.0,
                "y": strip_min,
                "width": check_limit,
                "height": strip_max - strip_min,
            })

        if scan_pos > search_limit:
            break

        intervals = _get_visible_intervals(scan_pos, check_limit, active_obstacles)
        if not intervals:
            continue

        strip_waypoints: list[tuple[float, float]] = []
        ordered = intervals if left_to_right else list(reversed(intervals))
        prev_last_t: float | None = None # 't' is the traverse coordinate (x for Horiz, y for Vert)

        for start_t, end_t in ordered:
            if left_to_right:
                first_t, last_t = start_t, end_t
                gap = prev_last_t is not None and prev_last_t < start_t
            else:
                first_t, last_t = end_t, start_t
                gap = prev_last_t is not None and prev_last_t > end_t

            if gap and prev_last_t is not None:
                # Calculate detour in the traverse dimension
                # The 'scan_pos' is constant. We need to move from prev_last_t to first_t
                # avoiding obstacles that block 'scan_pos'.
                detour_level = _get_detour_height(prev_last_t, first_t, scan_pos, active_obstacles)
                
                if use_vertical:
                     # Vertical mode: scan_pos is X, traverse is Y.
                     # detour_level is "height" in the X dimension (the scan dimension).
                     # Wait, _get_detour_height returns "y + clearance".
                     # In transposed world:
                     # _get_detour_height computes max "y2" (which is actually x2) + clearance.
                     # So it gives us a safe X coordinate.
                     strip_waypoints.append((detour_level, prev_last_t))
                     strip_waypoints.append((detour_level, first_t))
                else:
                    strip_waypoints.append((prev_last_t, detour_level))
                    strip_waypoints.append((first_t, detour_level))

            if use_vertical:
                strip_waypoints.append((scan_pos, start_t) if left_to_right else (scan_pos, end_t))
                strip_waypoints.append((scan_pos, end_t) if left_to_right else (scan_pos, start_t))
            else:
                strip_waypoints.append((start_t, scan_pos) if left_to_right else (end_t, scan_pos))
                strip_waypoints.append((end_t, scan_pos) if left_to_right else (start_t, scan_pos))

            prev_last_t = last_t

        if strip_waypoints:
            if waypoints and waypoints[-1] != strip_waypoints[0]:
                waypoints.append(strip_waypoints[0])
            for i in range(1, len(strip_waypoints)):
                waypoints.append(strip_waypoints[i])
            left_to_right = not left_to_right 
    
    return waypoints, strip_rectangles


def get_coverage_explanation(
    wall: WallConfig,
    obstacles: Sequence[Obstacle],
    waypoints: list[tuple[float, float]],
    sweep_height: float = 0.25,
    overlap_ratio: float = 0.0,
) -> dict:

    """
    Generate human-readable explanation of the path planning.
    """
    effective_step = sweep_height * (1 - overlap_ratio)
    effective_step = max(effective_step, 1e-6)
    num_strips = math.ceil(wall.height / effective_step)

    total_path_length = 0.0
    for i in range(1, len(waypoints)):
        total_path_length += math.dist(waypoints[i], waypoints[i - 1])

    turn_count = 0
    for i in range(2, len(waypoints)):
        dx1 = waypoints[i - 1][0] - waypoints[i - 2][0]
        dy1 = waypoints[i - 1][1] - waypoints[i - 2][1]
        dx2 = waypoints[i][0] - waypoints[i - 1][0]
        dy2 = waypoints[i][1] - waypoints[i - 1][1]

        # if direction changed
        if (dx1, dy1) != (dx2, dy2):
            turn_count += 1
    total_area = wall.width * wall.height
    obstacle_area = sum(o.width * o.height for o in obstacles)

    covered_area = total_area - obstacle_area
    net_paintable_area = covered_area

    coverage_percent = (
        100.0 if net_paintable_area > 0 else 0.0
    )

    efficiency_ratio = (
        net_paintable_area / total_path_length
        if total_path_length > 0 else 0.0
    )

    return {
        "algorithm": "Zigzag (Boustrophedon) Coverage",
        "description": (
            "The path uses horizontal strips alternating left-to-right and right-to-left. "
            "Each strip is divided into visible intervals where obstacles are avoided."
        ),
        "wall_dimensions_m": {"width": wall.width, "height": wall.height},
        "total_area_m2": round(total_area, 4),
        "obstacle_area_m2": round(obstacle_area, 4),
        "covered_area_m2": round(covered_area, 4),
        "sweep_height_m": sweep_height,
        "strip_count": num_strips,
        "waypoint_count": len(waypoints),        
        "coverage_percent": round(coverage_percent, 2),
        "total_path_length_m": round(total_path_length, 3),
        "turn_count": turn_count,
        "efficiency_ratio": round(efficiency_ratio, 4),
    }
