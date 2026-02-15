import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { WallConfig, Obstacle, PathPlanningRequest } from '../types'
import { planPath } from '../services/api'
import PathVisualizer from '../components/PathVisualizer'
import PlaybackControls from '../components/PlaybackControls'

export default function PlanningPage() {
  const navigate = useNavigate()
  const [wallWidth, setWallWidth] = useState(5)
  const [wallHeight, setWallHeight] = useState(5)
  const [obstacles, setObstacles] = useState<Obstacle[]>([
    { x: 2.5, y: 2.5, width: 0.25, height: 0.25 },
  ])
  const [name, setName] = useState('Untitled Trajectory')
  const [sweepHeight, setSweepHeight] = useState(0.25)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<{
    trajectoryId: string
    waypoints: { x: number; y: number }[]
    explanation: { algorithm?: string; description?: string; wall_dimensions_m?: { width?: number; height?: number }; total_area_m2?: number; obstacle_area_m2?: number; covered_area_m2?: number; sweep_height_m?: number; strip_count?: number; waypoint_count?: number }
  } | null>(null)

  const handlePlan = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const req: PathPlanningRequest = {
        wall_config: { width: wallWidth, height: wallHeight },
        obstacles,
        name,
        sweep_height: sweepHeight,
      }
      const res = await planPath(req)
      setResult({
        trajectoryId: res.trajectory_id,
        waypoints: res.waypoints,
        explanation: res.coverage_explanation,
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to plan path')
    } finally {
      setLoading(false)
    }
  }

  const addObstacle = () => {
    setObstacles([
      ...obstacles,
      { x: 0, y: 0, width: 0.25, height: 0.25 },
    ])
  }

  const updateObstacle = (i: number, o: Obstacle) => {
    const next = [...obstacles]
    next[i] = o
    setObstacles(next)
  }

  const removeObstacle = (i: number) => {
    setObstacles(obstacles.filter((_, j) => j !== i))
  }

  const wallConfig: WallConfig = { width: wallWidth, height: wallHeight }

  return (
    <div className="planning-page">
      <h1>Coverage Path Planning</h1>

      <section className="form-section">
        <h2>Wall Dimensions (meters)</h2>
        <div className="form-row">
          <label>
            Width (m)
            <input
              type="number"
              min={0.1}
              step={0.1}
              value={wallWidth}
              onChange={(e) => setWallWidth(Number(e.target.value))}
            />
          </label>
          <label>
            Height (m)
            <input
              type="number"
              min={0.1}
              step={0.1}
              value={wallHeight}
              onChange={(e) => setWallHeight(Number(e.target.value))}
            />
          </label>
        </div>

        <h2>Obstacles (rectangular, meters)</h2>
        {obstacles.map((o, i) => (
          <div key={i} className="obstacle-row">
            <label>Obstacle {i + 1}</label>
            <input
              placeholder="x"
              type="number"
              step={0.01}
              value={o.x}
              onChange={(e) => updateObstacle(i, { ...o, x: Number(e.target.value) })}
            />
            <input
              placeholder="y"
              type="number"
              step={0.01}
              value={o.y}
              onChange={(e) => updateObstacle(i, { ...o, y: Number(e.target.value) })}
            />
            <input
              placeholder="width"
              type="number"
              step={0.01}
              value={o.width}
              onChange={(e) => updateObstacle(i, { ...o, width: Number(e.target.value) })}
            />
            <input
              placeholder="height"
              type="number"
              step={0.01}
              value={o.height}
              onChange={(e) => updateObstacle(i, { ...o, height: Number(e.target.value) })}
            />
            <button type="button" onClick={() => removeObstacle(i)}>
              Remove
            </button>
          </div>
        ))}
        <button type="button" onClick={addObstacle} className="add-btn">
          + Add Obstacle
        </button>

        <div className="form-row">
          <label>
            Sweep height (m)
            <input
              type="number"
              min={0.01}
              step={0.01}
              value={sweepHeight}
              onChange={(e) => setSweepHeight(Number(e.target.value))}
            />
          </label>
          <label>
            Trajectory name
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Untitled Trajectory"
            />
          </label>
        </div>

        <button
          type="button"
          onClick={handlePlan}
          disabled={loading}
          className="plan-btn"
        >
          {loading ? 'Planning...' : 'Plan Path'}
        </button>

        {error && <p className="error">{error}</p>}
      </section>

      {result && (
        <section className="result-section">
          <h2>Path Planning Result</h2>
          <div className="viz-layout">
            <PathVisualizer
              wallConfig={wallConfig}
              obstacles={obstacles}
              waypoints={result.waypoints}
              explanation={result.explanation}
            />
          </div>
          <div className="playback-section">
            <PlaybackControls
              waypoints={result.waypoints}
              wallConfig={wallConfig}
              obstacles={obstacles}
            />
          </div>
          <button
            type="button"
            onClick={() => navigate(`/visualize/${result.trajectoryId}`)}
            className="view-btn"
          >
            View Full Screen
          </button>
        </section>
      )}
    </div>
  )
}
