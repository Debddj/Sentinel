# Architecture Decision Record: Tech Stack

## Decision: FastAPI + PostgreSQL + Redis + React

### Context
Sentinel is an ML monitoring platform requiring:
- Real-time drift detection
- Async computation (SHAP, drift checks)
- WebSocket support for live alerts
- Modern UI with real-time updates

### Decision
We chose:
- **Backend**: FastAPI (async, fast, great OpenAPI docs)
- **Database**: PostgreSQL (JSONB for feature stats, mature)
- **Caching/Messaging**: Redis (pub/sub, fast cache)
- **Task Queue**: Celery with Redis broker
- **Frontend**: React 18 + TypeScript + Tailwind

### Rationale
- FastAPI enables async handlers for concurrent drift detection
- PostgreSQL JSONB columns store feature statistics and SHAP values
- Redis enables fast threshold tracking and pub/sub for alerts
- Celery allows background computation (SHAP) without blocking API
- React provides reactive UI updates via WebSocket

### Consequences
- Operational complexity: Managing Celery workers
- Learning curve: Async/await patterns in FastAPI
- Trade-off: Complexity vs. performance

## Alternatives Considered
1. **Django + Channels**: More batteries included, but slower
2. **Node.js/Express**: Excellent for real-time, but weaker ML ecosystem
3. **Go backend**: Simpler concurrency, but slower to develop

## Status: Accepted
