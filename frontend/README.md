# SentinelAI frontend

React + TypeScript + Vite UI for the SentinelAI backend.

    cd frontend
    npm install
    npm run dev        # http://localhost:5173

Set `VITE_API_BASE_URL` in `.env` (default `http://127.0.0.1:8000/api/v1`).
Allow the dev origin in FastAPI CORS: `http://localhost:5173`.

## Endpoints the UI calls (adjust in src/services/ to match your backend)
GET /health, GET /dashboard/summary, GET|POST /runs, GET /runs/{id}, POST /runs/{id}/cancel,
GET /test-suites, GET /findings, PATCH /findings/{id}/review, GET /models, PATCH /models/{id},
GET /audit/events, GET /audit/events/{id}, GET /audit/verify
