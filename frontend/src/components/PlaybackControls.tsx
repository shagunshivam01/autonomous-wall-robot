import { useState, useRef, useEffect } from 'react'
import type { WallConfig, Obstacle, Waypoint } from '../types'

interface PlaybackControlsProps {
  waypoints: Waypoint[]
  wallConfig: WallConfig
  obstacles: Obstacle[]
}

const CANVAS_SIZE = 400

export default function PlaybackControls({
  waypoints,
  wallConfig,
  obstacles,
}: PlaybackControlsProps) {
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [progress, setProgress] = useState(0)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const frameRef = useRef(0)

  const maxFrame = Math.max(0, waypoints.length - 1)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || waypoints.length === 0) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const w = wallConfig.width
    const h = wallConfig.height
    const scale = Math.min(CANVAS_SIZE / w, CANVAS_SIZE / h)
    const cx = (CANVAS_SIZE - w * scale) / 2
    const cy = (CANVAS_SIZE - h * scale) / 2

    const toCanvas = (x: number, y: number) => ({
      px: cx + x * scale,
      py: cy + (h - y) * scale,
    })

    const draw = (idx: number) => {
      ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)

      // Wall
      ctx.strokeStyle = '#58a6ff'
      ctx.lineWidth = 1
      ctx.strokeRect(cx, cy, w * scale, h * scale)

      // Obstacles
      ctx.fillStyle = '#484f58'
      for (const o of obstacles) {
        const { px, py } = toCanvas(o.x, o.y)
        ctx.fillRect(px, py - o.height * scale, o.width * scale, o.height * scale)
      }

      // Path (past)
      if (waypoints.length >= 2 && idx > 0) {
        ctx.strokeStyle = '#3fb950'
        ctx.lineWidth = 2
        ctx.beginPath()
        const first = toCanvas(waypoints[0].x, waypoints[0].y)
        ctx.moveTo(first.px, first.py)
        for (let i = 1; i <= idx; i++) {
          const { px, py } = toCanvas(waypoints[i].x, waypoints[i].y)
          ctx.lineTo(px, py)
        }
        ctx.stroke()
      }

      // Robot marker
      const wp = waypoints[idx]
      if (wp) {
        const { px, py } = toCanvas(wp.x, wp.y)
        ctx.fillStyle = '#f85149'
        ctx.beginPath()
        ctx.arc(px, py, 8, 0, Math.PI * 2)
        ctx.fill()
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 2
        ctx.stroke()
      }
    }

    draw(frameRef.current)
  }, [waypoints, wallConfig, obstacles, progress])

  useEffect(() => {
    if (!playing || waypoints.length <= 1) return

    const intervalMs = 80 / speed
    const start = Date.now()
    let rafId: number

    const tick = () => {
      const elapsed = Date.now() - start
      const nextFrame = Math.min(
        maxFrame,
        Math.floor(elapsed / intervalMs)
      )
      frameRef.current = nextFrame
      setProgress(maxFrame > 0 ? (nextFrame / maxFrame) * 100 : 100)
      if (nextFrame >= maxFrame) {
        setPlaying(false)
        return
      }
      rafId = requestAnimationFrame(tick)
    }

    rafId = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafId)
  }, [playing, speed, waypoints.length, maxFrame])

  const handlePlay = () => {
    if (frameRef.current >= maxFrame) {
      frameRef.current = 0
      setProgress(0)
    }
    setPlaying(true)
  }

  const handlePause = () => setPlaying(false)

  const handleRestart = () => {
    setPlaying(false)
    frameRef.current = 0
    setProgress(0)
  }

  return (
    <div className="playback-controls">
      <h3>Trajectory Playback</h3>
      <canvas
        ref={canvasRef}
        width={CANVAS_SIZE}
        height={CANVAS_SIZE}
        className="playback-canvas"
      />
      <div className="controls">
        <button type="button" onClick={playing ? handlePause : handlePlay}>
          {playing ? 'Pause' : 'Play'}
        </button>
        <button type="button" onClick={handleRestart}>
          Restart
        </button>
        <label>
          Speed
          <select
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={4}>4x</option>
          </select>
        </label>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
    </div>
  )
}
