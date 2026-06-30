# Wilaya Retail And Delivery Coverage

Deployable MVP for mapping clothing stores and delivery companies by Algerian wilaya, verifying candidate listings, clustering verified stores, and calculating cluster-to-delivery coverage.

## Run Locally

1. Copy `.env.example` to `.env`.
2. Add Google keys when you are ready for real maps, Places, and Routes calls. Use `NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY` for the frontend map, and `GOOGLE_PLACES_API_KEY`, `GOOGLE_ROUTES_API_KEY`, and `GOOGLE_GEOCODING_API_KEY` for server-side API calls. Leave them empty for demo/manual mode.
3. Start the stack:

```bash
docker compose up --build
```

Open:

- Frontend: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

The database is initialized from `database/init/001_schema.sql` and `database/init/002_seed.sql`.

## Map Display

The deployed dashboard uses Google Maps JavaScript API when `NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY` is configured.

It displays:

- Clothing store markers.
- Candidate store markers.
- Delivery company markers.
- DBSCAN cluster markers.
- Cluster-to-nearest-delivery coverage lines.

If the browser key is missing or blocked by domain restrictions, the frontend falls back to a local map renderer so the rest of the dashboard still works.

## Data Sources

The app treats Google Places as candidate discovery only. Candidates become part of the internal editable source of truth after verification/manual approval. Do not scrape Google Maps pages.

Supported feeds:

- Manual admin CRUD from the dashboard.
- CSV import through `POST /imports/places.csv`.
- Google Places discovery through `POST /ingestion/google-places`.
- Scheduled refresh through Celery Beat.

CSV columns:

```csv
name,category,subtype,phone,website,address_text,lat,lng,wilaya,commune,source_status,verification_score,google_place_id,google_maps_url
Boutique El Bahia,clothing_store,women,+213...,https://example.com,Rue Larbi Ben M'hidi,35.6993,-0.6352,Oran,Oran,manually_added,80,,
Yalidine Oran,delivery_company,courier,+213...,https://yalidine.com,Oran logistics zone,35.691,-0.6159,Oran,Oran,verified,92,,
```

Google Places ingestion example:

```bash
curl -X POST http://localhost:8000/ingestion/google-places \
  -H "Content-Type: application/json" \
  -d '{
    "wilaya": "Oran",
    "queries": [
      "clothing store in Oran Algeria",
      "women clothing store in Oran Algeria",
      "delivery company in Oran Algeria",
      "courier service in Oran Algeria"
    ],
    "max_pages_per_query": 1,
    "enqueue": false
  }'
```

If `GOOGLE_PLACES_API_KEY` and `GOOGLE_MAPS_API_KEY` are empty, ingestion is skipped safely and the app remains usable with manual and CSV data.

## Automatic Data Refresh

The `scheduler` service runs a nightly pipeline at 02:15 Africa/Algiers:

1. Google Places candidate discovery for the default wilaya.
2. Verification scoring pass.
3. DBSCAN cluster recalculation.
4. Cluster-to-delivery distance recalculation.

Set the default wilaya in `.env`:

```env
DEFAULT_WILAYA=Oran
```

Trigger the same pipeline manually:

```bash
curl -X POST "http://localhost:8000/ingestion/nightly-refresh?wilaya=Oran&enqueue=true"
```

For multiple wilayas, create one scheduler entry per wilaya in `backend/app/worker.py`, or call the endpoint from your own cron/job runner.

## Main API

- `GET /places`
- `POST /places`
- `PATCH /places/{id}`
- `DELETE /places/{id}`
- `POST /places/{id}/verification-checks`
- `POST /ingestion/google-places`
- `POST /verification/run`
- `POST /analysis/clusters/recalculate`
- `POST /analysis/distances/recalculate`
- `GET /exports/places.csv`
- `GET /exports/places.geojson`

## Deployment Options

### VPS or DigitalOcean

Use the included Docker Compose file:

```bash
docker compose up -d --build
```

Put Caddy, Traefik, or Nginx Proxy Manager in front for HTTPS.

### Railway, Render, Fly.io

Deploy the services separately:

- PostgreSQL with PostGIS enabled.
- Redis.
- Backend web service from `backend/Dockerfile`.
- Worker service from `backend/Dockerfile` with command `celery -A app.worker.celery_app worker --loglevel=INFO`.
- Scheduler service from `backend/Dockerfile` with command `celery -A app.worker.celery_app beat --loglevel=INFO`.
- Frontend static service from `frontend/Dockerfile`.

Set the same environment variables from `.env.example`.

## Production Notes

- Use managed Postgres with PostGIS or keep the included Docker PostGIS service on a VPS.
- Put the backend behind HTTPS.
- Restrict browser Google Maps keys by website referrer.
- Restrict server Google API keys by server IP and enabled APIs.
- Use Google Maps JavaScript API when displaying Google-derived candidate content on a map.
- Add auth before exposing admin CRUD publicly.
- Keep Google Places as candidate discovery, not a copied permanent Google directory. Approved internal records are your editable source of truth.
