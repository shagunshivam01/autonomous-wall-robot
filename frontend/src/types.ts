export interface WallConfig {
  width: number
  height: number
}

export interface Obstacle {
  x: number
  y: number
  width: number
  height: number
}

export interface Waypoint {
  x: number
  y: number
}

export interface SweepRectangle {
  x: number
  y: number
  width: number
  height: number
}

export interface PathPlanningRequest {
  wall_config: WallConfig
  obstacles: Obstacle[]
  name?: string
  sweep_height?: number
}

export interface PathPlanningResponse {
  trajectory_id: string
  waypoints: Waypoint[]
  coverage_explanation: CoverageExplanation
}

export interface CoverageExplanation {
  algorithm: string
  description: string
  wall_dimensions_m: { width: number; height: number }
  total_area_m2: number
  obstacle_area_m2: number
  covered_area_m2: number
  sweep_height_m: number
  strip_count: number
  waypoint_count: number

  coverage_percent?: number
  total_path_length_m?: number
  turn_count?: number
  efficiency_ratio?: number
  
  sweep_rectangles?: SweepRectangle[]
}

export interface Trajectory {
  id: string
  name: string
  wall_config: WallConfig
  obstacles: Obstacle[]
  waypoints: Waypoint[]
  created_at: string
}

export interface TrajectoryListResponse {
  items: Trajectory[]
  total: number
  skip: number
  limit: number
}
