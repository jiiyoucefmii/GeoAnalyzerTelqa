# Wilaya Retail And Delivery Coverage MVP

## What is included

- `algeria-retail-logistics-dashboard.html`: a runnable local dashboard with editable places, verification checks, DBSCAN-style clustering, straight-line distance estimates, CSV import/export, GeoJSON export, filters, and layer toggles.
- `postgis_schema.sql`: production-oriented PostgreSQL/PostGIS schema for the editable source of truth, source evidence, verification checks, clusters, cluster members, route distances, ingestion runs, and audit logs.

## How to use the prototype

Open `algeria-retail-logistics-dashboard.html` in a browser. It stores edits in browser `localStorage`, so it behaves like a local admin prototype without requiring a server.

The sample data covers Oran, Alger, and Blida. Choose a wilaya, adjust DBSCAN radius and minimum stores, then recalculate. Use the editor to add, edit, approve, reject, or remove stores and delivery companies.

## Production architecture

Recommended MVP stack:

- Frontend: Next.js or React with Google Maps JavaScript API for Google-derived Places content.
- Backend: FastAPI, Django, or NestJS.
- Database: PostgreSQL plus PostGIS.
- Jobs: Redis plus Celery, BullMQ, or Temporal.
- Processing: Python with GeoPandas, Shapely, scikit-learn DBSCAN, RapidFuzz, and H3 or grid generation.
- APIs: Google Places API, Google Routes API, Overpass API, and allowed website/social checks.

## Data flow

1. Admin selects a wilaya.
2. Backend loads the wilaya boundary polygon.
3. Backend generates overlapping search cells inside the polygon.
4. Google Places Text Search and Nearby Search create candidate records.
5. Candidates are deduplicated by `google_place_id`, location proximity, and fuzzy name match.
6. Verification checks run against allowed sources: Google API fields, OSM/Overpass, website health, social recency, phone/manual checks.
7. Admin approves candidates into the internal editable source of truth.
8. DBSCAN clusters verified clothing stores.
9. Route Matrix calculates cluster-to-delivery driving distances in batches.
10. Dashboard displays clusters, coverage gaps, queue status, exports, and audit history.

## Google Maps rule

Do not scrape Google Maps pages. Use Google Places API as candidate discovery and Google Routes API for route matrices. If Google-derived Places content is displayed on a map, use a Google map. For non-Google maps, display only your own verified records, OSM records, or other properly licensed data.

## Verification scoring

Suggested scoring:

- Google business status operational: strong positive signal.
- Phone number present and reachable: strong positive signal.
- Website or social page active: medium positive signal.
- OSM match within 30 to 50 meters: medium positive signal.
- Manual admin confirmation or field visit: strongest signal.
- Duplicate suspected, inactive page, address mismatch, or closed status: negative signal.

Use status names such as `candidate`, `verified`, `rejected`, and `manually_added` in the database. The UI can present friendlier labels like Unverified candidate, Likely active, Verified active, Temporarily closed, Permanently closed, Duplicate, and Needs manual review.

## Route Matrix batching

Google Routes API Compute Route Matrix has element limits. Batch by:

`origins * destinations <= provider_limit`

For example:

- 25 clusters x 20 delivery companies = 500 route elements, one batch.
- 80 clusters x 50 delivery companies = 4,000 route elements, multiple batches.

Store both `straight_line_distance_m` and provider-calculated `driving_distance_m` / `driving_duration_s`. The prototype estimates driving distance from straight-line distance; production should use the route provider.

## Next implementation step

Create a real backend around `postgis_schema.sql`, then replace localStorage in the HTML prototype with API calls:

- `GET /places?wilaya=Oran`
- `POST /places`
- `PATCH /places/{id}`
- `POST /places/{id}/verification-checks`
- `POST /ingestion/google-places`
- `POST /analysis/recalculate-clusters`
- `POST /analysis/recalculate-distances`
- `GET /exports/places.geojson`
