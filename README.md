# Autonomous Wall-Finishing Robot Control System

A coverage path planning system for autonomous wall-finishing robots. Implements zigzag (boustrophedon) path planning with obstacle avoidance, trajectory storage in SQLite, and a React-based 2D visualization with trajectory playback.

## Features

- **Coverage Planning**: Zigzag (boustrophedon) pattern for rectangular walls with rectangular obstacles
- **Backend API**: FastAPI with layered architecture (model, controller, service, persistence)
- **Database**: SQLite with WAL mode, indexing for efficient trajectory queries
- **Frontend**: React + TypeScript with 2D canvas visualization and trajectory playback
- **Testing**: pytest API and algorithm tests

## Project Structure

```
autonomous-wall-robot/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── algorithms/   # Coverage path planning
│   │   ├── controllers/  # API routes
│   │   ├── core/         # Config, logging
│   │   ├── models/       # Pydantic schemas
│   │   ├── persistence/  # SQLAlchemy, repositories
│   │   └── services/     # Business logic
│   ├── tests/
│   └── main.py
├── frontend/         # React + Vite frontend
│   └── src/
└── README.md
```

## Quick Start

### Backend

```bash
cd autonomous-wall-robot/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd autonomous-wall-robot/frontend
npm install
npm run dev
```

Open http://localhost:5173

### Run Tests

```bash
cd autonomous-wall-robot/backend
source venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

## Sample Case

- **Wall**: 5m × 5m
- **Obstacle**: Window 25cm × 25cm (default position 2.5m, 2.5m)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/trajectories/plan` | Plan path, store trajectory |
| GET | `/api/v1/trajectories` | List trajectories |
| GET | `/api/v1/trajectories/{id}` | Get trajectory |
| PUT | `/api/v1/trajectories/{id}` | Update trajectory |
| DELETE | `/api/v1/trajectories/{id}` | Delete trajectory |

## Environment

Copy `backend/.env.example` to `backend/.env` to override defaults (optional).
