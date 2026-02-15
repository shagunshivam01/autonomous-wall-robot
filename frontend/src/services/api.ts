import type {
  PathPlanningRequest,
  PathPlanningResponse,
  Trajectory,
  TrajectoryListResponse,
} from '../types'

const API_BASE = '/api/v1'

async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export async function planPath(req: PathPlanningRequest): Promise<PathPlanningResponse> {
  return fetchApi<PathPlanningResponse>('/trajectories/plan', {
    method: 'POST',
    body: JSON.stringify({
      wall_config: req.wall_config,
      obstacles: req.obstacles,
      name: req.name ?? 'Untitled Trajectory',
      sweep_height: req.sweep_height ?? 0.25,
    }),
  })
}

export async function listTrajectories(skip = 0, limit = 50): Promise<TrajectoryListResponse> {
  return fetchApi<TrajectoryListResponse>(
    `/trajectories?skip=${skip}&limit=${limit}`
  )
}

export async function getTrajectory(id: string): Promise<Trajectory> {
  return fetchApi<Trajectory>(`/trajectories/${id}`)
}

export async function updateTrajectory(id: string, data: { name?: string }): Promise<Trajectory> {
  return fetchApi<Trajectory>(`/trajectories/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteTrajectory(id: string): Promise<void> {
  return fetchApi<void>(`/trajectories/${id}`, { method: 'DELETE' })
}
