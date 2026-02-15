import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listTrajectories, deleteTrajectory } from '../services/api'
import type { Trajectory } from '../types'

export default function HistoryPage() {
  const navigate = useNavigate()
  const [trajectories, setTrajectories] = useState<Trajectory[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listTrajectories()
      .then((res) => setTrajectories(res.items))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  const handleDelete = async (id: string) => {
    try {
      await deleteTrajectory(id)
      setTrajectories((prev) => prev.filter((t) => t.id !== id))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete')
    }
  }

  if (loading) return <p>Loading...</p>
  if (error) return <p className="error">{error}</p>

  return (
    <div className="history-page">
      <h1>Trajectory History</h1>
      <ul className="trajectory-list">
        {trajectories.map((t) => (
          <li key={t.id} className="trajectory-item">
            <div>
              <strong>{t.name}</strong>
              <span>
                {t.wall_config.width}m × {t.wall_config.height}m
              </span>
              <span>{t.waypoints.length} waypoints</span>
              <span>{new Date(t.created_at).toLocaleString()}</span>
            </div>
            <div className="trajectory-actions">
              <button
                type="button"
                onClick={() => navigate(`/visualize/${t.id}`)}
              >
                View
              </button>
              <button type="button" onClick={() => handleDelete(t.id)}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
      {trajectories.length === 0 && (
        <p>No trajectories yet. Plan a path from the home page.</p>
      )}
    </div>
  )
}
