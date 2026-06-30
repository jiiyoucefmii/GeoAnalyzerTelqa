# Deployment And Data Feeds

## Components

- `db`: PostgreSQL with PostGIS, initialized from `database/init`.
- `redis`: broker for background jobs.
- `backend`: FastAPI API.
- `worker`: Celery job worker.
- `scheduler`: Celery Beat nightly automation.
- `frontend`: static admin dashboard served by Nginx.

## Feeding Data

### Manual

Use the dashboard editor to create or update places. Manual records are saved as `manually_added` or whichever status you choose.

### CSV

Upload a CSV in the dashboard or call:

```bash
curl -X POST http://localhost:8000/imports/places.csv \
  -F "file=@places.csv"
```

Minimum columns:

```csv
name,category,lat,lng,wilaya
```

Recommended columns:

```csv
name,category,subtype,phone,website,address_text,lat,lng,wilaya,commune,source_status,verification_score,google_place_id,google_maps_url
```

### Google Places

Configure:

```env
GOOGLE_PLACES_API_KEY=your_places_server_key
GOOGLE_ROUTES_API_KEY=your_routes_server_key
GOOGLE_GEOCODING_API_KEY=your_geocoding_server_key
NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY=your_maps_javascript_browser_key
```

Use `GOOGLE_MAPS_API_KEY` only as a fallback shared server key. For production, separate browser and server keys are safer.

Then run:

```bash
curl -X POST http://localhost:8000/ingestion/google-places \
  -H "Content-Type: application/json" \
  -d '{"wilaya":"Oran","queries":["clothing store in Oran Algeria","delivery company in Oran Algeria"],"max_pages_per_query":1}'
```

The backend stores Google results as `candidate` records and inserts evidence into `place_sources` and `verification_checks`.

## Automatic Feed

The scheduler service runs `nightly_refresh_task` each night:

```txt
discover candidates
-> run verification pass
-> recalculate DBSCAN clusters
-> recalculate cluster-to-delivery distances
```

To add several wilayas, add more entries to `celery_app.conf.beat_schedule` in `backend/app/worker.py`.

## Production Hardening

- Add login/auth before exposing admin endpoints.
- Restrict the browser key to your deployed frontend domain.
- Restrict server keys to server IPs and only the APIs they need.
- Use HTTPS.
- Use managed backups for Postgres.
- Monitor worker failures and ingestion cost.
- Start with one wilaya, then expand after reviewing cost and candidate quality.
