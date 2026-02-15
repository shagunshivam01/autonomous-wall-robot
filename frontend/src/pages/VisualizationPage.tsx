import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTrajectory } from '../services/api'
import PathVisualizer from '../components/PathVisualizer'
import PlaybackControls from '../components/PlaybackControls'

export default function VisualizationPage() {
  const { trajectoryId } = useParams<{ trajectoryId: string }>()
  const navigate = useNavigate()
  const [trajectory, setTrajectory] = useState<{
    wall_config: { width: number; height: number }
    obstacles: { x: number; y: number; width: number; height: number }[]
    waypoints: { x: number; y: number }[]
    name: string
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!trajectoryId) return
    getTrajectory(trajectoryId)
      .then(setTrajectory)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [trajectoryId])

  if (loading) return <p>Loading...</p>
  if (error) return <p className="error">{error}</p>
  if (!trajectory) return <p>Trajectory not found</p>

  const explanation = {
    algorithm: 'Zigzag (Boustrophedon) Coverage',
    wall_dimensions_m: trajectory.wall_config,
    waypoint_count: trajectory.waypoints.length,
  }

  return (
    <div className="visualization-page">
      <h1>{trajectory.name}</h1>
      <button type="button" onClick={() => navigate(-1)}>
        Back
      </button>
      <div className="viz-full-layout">
        <PathVisualizer
          wallConfig={trajectory.wall_config}
          obstacles={trajectory.obstacles}
          waypoints={trajectory.waypoints}
          explanation={explanation}
        />
      </div>
      <div className="playback-full">
        <PlaybackControls
          waypoints={trajectory.waypoints}
          wallConfig={trajectory.wall_config}
          obstacles={trajectory.obstacles}
        />
      </div>
    </div>
  )
}
