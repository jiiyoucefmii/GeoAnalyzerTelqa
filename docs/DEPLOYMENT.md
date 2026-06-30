# Deployment Guide

This platform has three production parts:

- Static dashboard frontend: deploy on Vercel.
- FastAPI backend: deploy on Render, Railway, Fly.io, or a VPS.
- Data services: PostgreSQL with PostGIS plus Redis.

Vercel alone is not the right home for the whole app because the backend needs a normal API service, a worker, a scheduler, PostGIS, and Redis. Use Vercel for the browser dashboard and a backend platform for the API.

## Required Google Cloud setup

Create or reuse the Google Cloud project, enable billing, then enable:

- Maps JavaScript API
- Places API
- Routes API
- Geocoding API

Restrict keys before production:

- Browser Maps key: HTTP referrers only, limited to your Vercel domain.
- Places, Routes, Geocoding keys: server-side only if your host supports IP restrictions. Do not expose these to the browser.

## Backend environment variables

Set these on your backend host:

```bash
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
REDIS_URL=redis://HOST:6379/0
GOOGLE_PLACES_API_KEY=your_server_places_key
GOOGLE_ROUTES_API_KEY=your_server_routes_key
GOOGLE_GEOCODING_API_KEY=your_server_geocoding_key
GOOGLE_MAPS_API_KEY=
GOOGLE_PLACES_LANGUAGE=fr
API_CORS_ORIGINS=https://your-vercel-app.vercel.app
DEFAULT_WILAYA=Oran
```

## Frontend environment variables

Set these on Vercel:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-api.example.com
NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY=your_browser_maps_key
```

## Database setup

Use PostgreSQL with PostGIS enabled. Then run:

```bash
psql "$DATABASE_URL" -f database/init/001_schema.sql
psql "$DATABASE_URL" -f database/init/002_seed.sql
```

If the host blocks `CREATE EXTENSION`, enable PostGIS, pgcrypto, pg_trgm, and unaccent from the provider dashboard first.

## Backend deployment

Deploy the `backend` folder as a Docker service or Python web service.

Web command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Worker command:

```bash
celery -A app.worker.celery_app worker --loglevel=INFO
```

Scheduler command:

```bash
celery -A app.worker.celery_app beat --loglevel=INFO
```

Health check:

```bash
GET /health
```

## Frontend deployment on Vercel

Import the `frontend` directory as the Vercel project root.

Use:

```bash
npm run build
```

Vercel will serve the static files from `frontend/app`.

## First production run

1. Open the Vercel dashboard URL.
2. Type a wilaya, for example `Alger`, `Oran`, `Setif`, or `Constantine`.
3. Click Google Candidates.
4. Click Verify.
5. Approve/reject candidates as needed.
6. Click Clusters.
7. Click Distances.

The map should show only your internal clothing store and delivery company records. Google base-map business POIs are hidden in the dashboard.

## Automation

For automatic refresh, keep the Celery worker and beat scheduler running. The scheduled task discovers Google candidates, verifies them, recalculates clusters, and recalculates Google Routes distances for the default wilaya.
