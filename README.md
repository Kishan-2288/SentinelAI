# SentinelAI

SentinelAI is a full-stack application for adversarial LLM safety testing.

- **Backend**: FastAPI service for run orchestration, evaluation, findings, model registry, audit events, and migrations.
- **Frontend**: React + TypeScript + Vite dashboard for creating runs, reviewing results, and managing models.

## Project structure

```text
SentinelAI/
├─ backend/   # FastAPI backend
└─ frontend/  # React frontend
```

## Prerequisites

- Python 3.11+ (3.12 recommended)
- Node.js 18+ and npm

## Backend setup (`backend/`)

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

- API docs: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/health`

## Frontend setup (`frontend/`)

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

- Dev server: `http://localhost:5173`
- Set `VITE_API_BASE_URL` to your backend API base URL (default is `http://127.0.0.1:8000/api/v1`).

## Typical local workflow

1. Start backend from `backend/`.
2. Start frontend from `frontend/`.
3. Open frontend in browser and create/evaluate runs.

## Notes

- Do **not** commit secrets from `.env` files.
- Run backend tests:

```powershell
cd backend
pytest -q
```
