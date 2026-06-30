CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'place_category') THEN
    CREATE TYPE place_category AS ENUM ('clothing_store', 'delivery_company');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'source_status') THEN
    CREATE TYPE source_status AS ENUM ('candidate', 'verified', 'rejected', 'manually_added');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'source_type') THEN
    CREATE TYPE source_type AS ENUM ('google_places', 'osm', 'website', 'facebook', 'instagram', 'tiktok', 'manual', 'phone_call', 'field_visit', 'csv_upload');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'verification_check_type') THEN
    CREATE TYPE verification_check_type AS ENUM ('google_business_status', 'osm_match', 'website_active', 'social_recent', 'phone_reachable', 'manual_visit', 'duplicate_review', 'address_match');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'verification_result') THEN
    CREATE TYPE verification_result AS ENUM ('pass', 'fail', 'uncertain');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS places (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  category place_category NOT NULL,
  subtype text,
  phone text,
  website text,
  address_text text,
  lat double precision NOT NULL CHECK (lat BETWEEN -90 AND 90),
  lng double precision NOT NULL CHECK (lng BETWEEN -180 AND 180),
  geom geography(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography) STORED,
  wilaya text NOT NULL,
  commune text,
  source_status source_status NOT NULL DEFAULT 'candidate',
  verification_score integer NOT NULL DEFAULT 0 CHECK (verification_score BETWEEN 0 AND 100),
  last_verified_at timestamptz,
  google_place_id text,
  google_maps_url text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS place_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  place_id uuid NOT NULL REFERENCES places(id) ON DELETE CASCADE,
  source_type source_type NOT NULL,
  source_url text,
  source_confidence numeric(4,3) NOT NULL DEFAULT 0.5 CHECK (source_confidence BETWEEN 0 AND 1),
  raw_reference_id text,
  raw_payload jsonb,
  checked_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (place_id, source_type, raw_reference_id)
);

CREATE TABLE IF NOT EXISTS verification_checks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  place_id uuid NOT NULL REFERENCES places(id) ON DELETE CASCADE,
  check_type verification_check_type NOT NULL,
  result verification_result NOT NULL,
  details text,
  evidence_url text,
  checked_at timestamptz NOT NULL DEFAULT now(),
  checked_by text
);

CREATE TABLE IF NOT EXISTS clusters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  wilaya text NOT NULL,
  algorithm text NOT NULL,
  centroid_lat double precision NOT NULL,
  centroid_lng double precision NOT NULL,
  geom geography(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(centroid_lng, centroid_lat), 4326)::geography) STORED,
  store_count integer NOT NULL,
  radius_m numeric(10,2) NOT NULL,
  density_score numeric(12,3),
  calculated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cluster_members (
  cluster_id uuid NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
  place_id uuid NOT NULL REFERENCES places(id) ON DELETE CASCADE,
  distance_to_centroid_m numeric(10,2),
  PRIMARY KEY (cluster_id, place_id)
);

CREATE TABLE IF NOT EXISTS cluster_delivery_distances (
  cluster_id uuid NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
  delivery_company_id uuid NOT NULL REFERENCES places(id) ON DELETE CASCADE,
  driving_distance_m integer,
  driving_duration_s integer,
  straight_line_distance_m integer NOT NULL,
  route_provider text NOT NULL DEFAULT 'straight_line_estimate',
  route_raw_payload jsonb,
  calculated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (cluster_id, delivery_company_id)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  wilaya text NOT NULL,
  query text NOT NULL,
  provider source_type NOT NULL,
  status text NOT NULL DEFAULT 'running',
  candidates_found integer NOT NULL DEFAULT 0,
  started_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz,
  error_message text
);

CREATE TABLE IF NOT EXISTS audit_log (
  id bigserial PRIMARY KEY,
  actor text,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id uuid,
  before_state jsonb,
  after_state jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_places_geom ON places USING gist (geom);
CREATE INDEX IF NOT EXISTS idx_places_wilaya_category_status ON places (wilaya, category, source_status);
CREATE INDEX IF NOT EXISTS idx_places_google_place_id ON places (google_place_id) WHERE google_place_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_places_name_trgm ON places USING gin (lower(name) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_place_sources_place_id ON place_sources (place_id);
CREATE INDEX IF NOT EXISTS idx_verification_checks_place_id ON verification_checks (place_id);
CREATE INDEX IF NOT EXISTS idx_clusters_geom ON clusters USING gist (geom);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_places_updated_at ON places;
CREATE TRIGGER trg_places_updated_at
BEFORE UPDATE ON places
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE VIEW active_places AS
SELECT *
FROM places
WHERE source_status IN ('verified', 'manually_added');

CREATE OR REPLACE VIEW candidate_review_queue AS
SELECT
  p.id,
  p.name,
  p.category,
  p.subtype,
  p.wilaya,
  p.commune,
  p.verification_score,
  p.source_status,
  p.google_place_id,
  p.google_maps_url,
  max(vc.checked_at) AS last_check_at,
  count(vc.id) AS check_count
FROM places p
LEFT JOIN verification_checks vc ON vc.place_id = p.id
WHERE p.source_status = 'candidate'
GROUP BY p.id;

CREATE OR REPLACE VIEW cluster_coverage_summary AS
SELECT
  c.id AS cluster_id,
  c.wilaya,
  c.algorithm,
  c.store_count,
  c.radius_m,
  c.density_score,
  min(cdd.driving_distance_m) AS nearest_driving_distance_m,
  min(cdd.driving_duration_s) AS nearest_driving_duration_s,
  percentile_disc(0.9) WITHIN GROUP (ORDER BY cdd.driving_distance_m) AS p90_delivery_distance_m
FROM clusters c
LEFT JOIN cluster_delivery_distances cdd ON cdd.cluster_id = c.id
GROUP BY c.id;

-- Straight-line distance query example:
-- SELECT
--   c.id AS cluster_id,
--   p.id AS delivery_company_id,
--   ST_Distance(c.geom, p.geom)::integer AS straight_line_distance_m
-- FROM clusters c
-- JOIN places p
--   ON p.category = 'delivery_company'
--  AND p.source_status IN ('verified', 'manually_added')
--  AND p.wilaya = c.wilaya;
