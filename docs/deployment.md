# LogiSense-AI Deployment Guide

## Docker Compose
To run the entire stack (backend + frontend):
```bash
docker-compose up --build
```

The services will be available at:
- Frontend: `http://localhost:3000` (or `http://localhost:80`depending on port mapping)
- Backend: `http://localhost:8000` (Swagger docs at `/docs`)

## Local Development
1. Backend:
```bash
python -m uvicorn backend.app.main:app --reload
```

2. Frontend:
```bash
cd frontend
npm run dev
```
