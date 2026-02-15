import { useRef, useEffect } from 'react'
import type { WallConfig, Obstacle, Waypoint } from '../types'

interface PathVisualizerProps {
  wallConfig: WallConfig
  obstacles: Obstacle[]
  waypoints: Waypoint[]
  explanation?: {
    algorithm?: string
    description?: string
    wall_dimensions_m?: { width?: number; height?: number }
    total_area_m2?: number
    obstacle_area_m2?: number
    covered_area_m2?: number
    sweep_height_m?: number
    strip_count?: number
    waypoint_count?: number
  }
}

const CANVAS_SIZE = 500

export default function PathVisualizer({
  wallConfig,
  obstacles,
  waypoints,
  explanation,
}: PathVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const w = wallConfig.width
    const h = wallConfig.height

    // Scale so wall fits in canvas (wall origin: bottom-left, canvas: top-left)
    const scale = Math.min(CANVAS_SIZE / w, CANVAS_SIZE / h)
    const cx = (CANVAS_SIZE - w * scale) / 2
    const cy = (CANVAS_SIZE - h * scale) / 2

    const toCanvas = (x: number, y: number) => ({
      px: cx + x * scale,
      py: cy + (h - y) * scale,
    })

    ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)

    // Wall boundary
    ctx.strokeStyle = '#58a6ff'
    ctx.lineWidth = 2
    ctx.strokeRect(cx, cy, w * scale, h * scale) 

    // Sweep coverage surfaces
    if (explanation?.sweep_rectangles) {
      ctx.fillStyle = 'rgba(63, 197, 94, 0.25)'

      for (const r of explanation.sweep_rectangles) {
        const { px, py } = toCanvas(r.x, r.y + r.height)
        ctx.fillRect(
          px,
          py,
          r.width * scale,
          r.height * scale
        )
      }
    }

    // Obstacles (gray)
    ctx.fillStyle = '#484f58'
    ctx.strokeStyle = '#8b949e'
    ctx.lineWidth = 1
    for (const o of obstacles) {
      const { px, py } = toCanvas(o.x, o.y)
      ctx.fillRect(px, py - o.height * scale, o.width * scale, o.height * scale)
      ctx.strokeRect(px, py - o.height * scale, o.width * scale, o.height * scale)
    }

    // Path
    if (waypoints.length >= 2) {
      ctx.strokeStyle = '#3fb950'
      ctx.lineWidth = 2
      ctx.beginPath()
      const first = toCanvas(waypoints[0].x, waypoints[0].y)
      ctx.moveTo(first.px, first.py)
      for (let i = 1; i < waypoints.length; i++) {
        const { px, py } = toCanvas(waypoints[i].x, waypoints[i].y)
        ctx.lineTo(px, py)
      }
      ctx.stroke()

      // Waypoint dots
      ctx.fillStyle = '#3fb950'
      for (const wp of waypoints) {
        const { px, py } = toCanvas(wp.x, wp.y)
        ctx.beginPath()
        ctx.arc(px, py, 3, 0, Math.PI * 2)
        ctx.fill()
      }
    }
  }, [wallConfig, obstacles, waypoints])

  return (
    <div className="path-visualizer">
      <div className="viz-canvas-wrap">
        <canvas
          ref={canvasRef}
          width={CANVAS_SIZE}
          height={CANVAS_SIZE}
          className="viz-canvas"
        />
      </div>
      {explanation && (
        <div className="explanation-panel">
          <h3>Path Planning Explanation</h3>
          <p className="algorithm">{String(explanation.algorithm)}</p>
          <p className="description">{String(explanation.description)}</p>
          <dl className="stats">
            <dt>Wall</dt>
            <dd>
              {String(explanation.wall_dimensions_m?.width ?? '')}m × {String(explanation.wall_dimensions_m?.height ?? '')}m
            </dd>
            <dt>Total area</dt>
            <dd>{String(explanation.total_area_m2)} m²</dd>
            <dt>Obstacle area</dt>
            <dd>{String(explanation.obstacle_area_m2)} m²</dd>
            <dt>Covered area</dt>
            <dd>{String(explanation.covered_area_m2)} m²</dd>
            <dt>Sweep height</dt>
            <dd>{String(explanation.sweep_height_m)} m</dd>
            <dt>Strips</dt>
            <dd>{String(explanation.strip_count)}</dd>
            <dt>Waypoints</dt>
            <dd>{String(explanation.waypoint_count)}</dd>

            <dt>Coverage</dt>
            <dd>{String(explanation.coverage_percent ?? '')}%</dd>

            <dt>Path length</dt>
            <dd>{String(explanation.total_path_length_m ?? '')} m</dd>

            <dt>Turns</dt>
            <dd>{String(explanation.turn_count ?? '')}</dd>

            <dt>Efficiency</dt>
            <dd>{String(explanation.efficiency_ratio ?? '')} m²/m</dd>
          </dl>
        </div>
      )}
    </div>
  )
}
