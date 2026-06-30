import csv
import io
import math
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from psycopg.types.json import Jsonb

from app.config import get_settings
from app.db import get_conn, normalize_record
from app.schemas import PlaceCreate, PlacePatch


PLACE_COLUMNS = [
    "id",
    "name",
    "category",
    "subtype",
    "phone",
    "website",
    "address_text",
    "lat",
    "lng",
    "wilaya",
    "commune",
    "source_status",
    "verification_score",
    "last_verified_at",
    "google_place_id",
    "google_maps_url",
    "created_at",
    "updated_at",
]

CLOTHING_TYPES = {
    "clothing_store",
    "shoe_store",
    "sportswear_store",
    "womens_clothing_store",
    "mens_clothing_store",
    "childrens_clothing_store",
    "fashion_accessories_store",
}

DELIVERY_TYPES = {
    "courier_service",
    "shipping_service",
    "transportation_service",
    "moving_company",
    "post_office",
    "freight_forwarding_service",
    "logistics_service",
}

BLOCKED_TYPES = {
    "restaurant",
    "cafe",
    "food",
    "meal_delivery",
    "meal_takeaway",
    "grocery_store",
    "supermarket",
    "pharmacy",
    "bank",
    "atm",
    "lodging",
}


def list_places(filters: dict[str, Any]) -> list[dict[str, Any]]:
    where = []
    params: dict[str, Any] = {}

    for field in ["wilaya", "commune", "category", "source_status"]:
        value = filters.get(field)
        if value:
            where.append(f"{field} = %({field})s")
            params[field] = value

    if filters.get("q"):
        where.append("lower(name) LIKE %(q)s")
        params["q"] = f"%{filters['q'].lower()}%"

    if filters.get("min_score") is not None:
        where.append("verification_score >= %(min_score)s")
        params["min_score"] = filters["min_score"]

    sql = f"SELECT {', '.join(PLACE_COLUMNS)} FROM places"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY wilaya, category, name LIMIT %(limit)s OFFSET %(offset)s"
    params["limit"] = filters.get("limit", 500)
    params["offset"] = filters.get("offset", 0)

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return normalize_record(rows)


def get_place(place_id: UUID | str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT {', '.join(PLACE_COLUMNS)} FROM places WHERE id = %s",
            (str(place_id),),
        ).fetchone()
    return normalize_record(row) if row else None


def create_place(payload: PlaceCreate, source_type: str = "manual") -> dict[str, Any]:
    data = payload.model_dump(mode="json")
    columns = list(data.keys())
    placeholders = [f"%({column})s" for column in columns]
    sql = f"""
        INSERT INTO places ({", ".join(columns)})
        VALUES ({", ".join(placeholders)})
        RETURNING {", ".join(PLACE_COLUMNS)}
    """
    with get_conn() as conn:
        row = conn.execute(sql, data).fetchone()
        conn.execute(
            """
            INSERT INTO place_sources (place_id, source_type, source_url, source_confidence, raw_reference_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (
                row["id"],
                source_type,
                row.get("google_maps_url") or row.get("website") or "",
                1 if source_type == "manual" else 0.7,
                row.get("google_place_id") or "",
            ),
        )
    return normalize_record(row)


def update_place(place_id: UUID | str, payload: PlacePatch) -> dict[str, Any] | None:
    updates = {key: value for key, value in payload.model_dump(mode="json", exclude_unset=True).items()}
    if not updates:
        return get_place(place_id)

    assignments = [f"{key} = %({key})s" for key in updates]
    updates["id"] = str(place_id)
    with get_conn() as conn:
        row = conn.execute(
            f"""
            UPDATE places
            SET {", ".join(assignments)}
            WHERE id = %(id)s
            RETURNING {", ".join(PLACE_COLUMNS)}
            """,
            updates,
        ).fetchone()
    return normalize_record(row) if row else None


def remove_place(place_id: UUID | str, hard: bool = False) -> bool:
    with get_conn() as conn:
        if hard:
            result = conn.execute("DELETE FROM places WHERE id = %s", (str(place_id),))
        else:
            result = conn.execute(
                "UPDATE places SET source_status = 'rejected' WHERE id = %s",
                (str(place_id),),
            )
    return bool(result.rowcount)


def add_verification_check(place_id: UUID | str, payload) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO verification_checks (place_id, check_type, result, details, evidence_url, checked_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                str(place_id),
                payload.check_type,
                payload.result,
                payload.details,
                payload.evidence_url,
                payload.checked_by,
            ),
        ).fetchone()
        score = compute_place_score(conn, place_id)
        status_sql = ", last_verified_at = now()" if score >= 75 else ""
        conn.execute(
            f"""
            UPDATE places
            SET verification_score = %s,
                source_status = CASE
                    WHEN source_status = 'candidate' AND %s >= 75 THEN 'verified'::source_status
                    ELSE source_status
                END
                {status_sql}
            WHERE id = %s
            """,
            (score, score, str(place_id)),
        )
    return normalize_record(row) if row else None


def compute_place_score(conn, place_id: UUID | str) -> int:
    place = conn.execute("SELECT * FROM places WHERE id = %s", (str(place_id),)).fetchone()
    if not place:
        return 0
    checks = conn.execute(
        """
        SELECT DISTINCT ON (check_type) *
        FROM verification_checks
        WHERE place_id = %s
        ORDER BY check_type, checked_at DESC
        """,
        (str(place_id),),
    ).fetchall()
    score = 20
    if place.get("google_place_id"):
        score += 12
    if place.get("phone"):
        score += 12
    if place.get("website"):
        score += 8
    weights = {
        "google_business_status": 16,
        "osm_match": 14,
        "website_active": 10,
        "social_recent": 8,
        "phone_reachable": 16,
        "manual_visit": 22,
        "duplicate_review": 10,
        "address_match": 10,
    }
    for check in checks:
        delta = weights.get(check["check_type"], 8)
        if check["result"] == "pass":
            score += delta
        elif check["result"] == "uncertain":
            score += round(delta * 0.25)
        elif check["result"] == "fail":
            score -= round(delta * 0.75)
    if place.get("source_status") == "rejected":
        score = min(score, 30)
    return max(0, min(100, score))


def run_verification(wilaya: str | None = None, place_id: UUID | str | None = None) -> dict[str, Any]:
    where = []
    params: list[Any] = []
    if wilaya:
        where.append("wilaya = %s")
        params.append(wilaya)
    if place_id:
        where.append("id = %s")
        params.append(str(place_id))
    sql = f"SELECT {', '.join(PLACE_COLUMNS)} FROM places"
    if where:
        sql += " WHERE " + " AND ".join(where)

    updated = 0
    google_refreshed = 0
    website_checked = 0
    with get_conn() as conn:
        places = conn.execute(sql, params).fetchall()
        for place in places:
            google_details = fetch_google_place_details(place.get("google_place_id"))
            if google_details:
                apply_google_details(conn, place["id"], google_details)
                place = conn.execute(f"SELECT {', '.join(PLACE_COLUMNS)} FROM places WHERE id = %s", (place["id"],)).fetchone()
                google_refreshed += 1
            if place.get("phone"):
                conn.execute(
                    """
                    INSERT INTO verification_checks (place_id, check_type, result, details, checked_by)
                    VALUES (%s, 'phone_reachable', 'uncertain', 'Phone exists; confirm WhatsApp or call manually.', 'auto')
                    """,
                    (place["id"],),
                )
            website_result = check_website_active(place.get("website"))
            if website_result:
                conn.execute(
                    """
                    INSERT INTO verification_checks (place_id, check_type, result, details, evidence_url, checked_by)
                    VALUES (%s, 'website_active', %s, %s, %s, 'auto')
                    """,
                    (place["id"], website_result["result"], website_result["details"], place["website"]),
                )
                website_checked += 1
            score = compute_place_score(conn, place["id"])
            conn.execute(
                """
                UPDATE places
                SET verification_score = %s,
                    source_status = CASE
                        WHEN source_status = 'candidate' AND %s >= 75 THEN 'verified'::source_status
                        ELSE source_status
                    END,
                    last_verified_at = CASE WHEN %s >= 75 THEN now() ELSE last_verified_at END
                WHERE id = %s
                """,
                (score, score, score, place["id"]),
            )
            updated += 1
    return {"updated": updated, "google_refreshed": google_refreshed, "websites_checked": website_checked}


def fetch_google_place_details(google_place_id: str | None) -> dict[str, Any] | None:
    if not google_place_id:
        return None
    settings = get_settings()
    if not settings.places_key:
        return None
    place_name = google_place_id if google_place_id.startswith("places/") else f"places/{google_place_id}"
    field_mask = ",".join(
        [
            "id",
            "displayName",
            "formattedAddress",
            "location",
            "businessStatus",
            "nationalPhoneNumber",
            "websiteUri",
            "googleMapsUri",
            "primaryType",
            "types",
        ]
    )
    headers = {
        "X-Goog-Api-Key": settings.places_key,
        "X-Goog-FieldMask": field_mask,
    }
    try:
        with httpx.Client(timeout=20) as client:
            response = client.get(f"https://places.googleapis.com/v1/{place_name}", headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        return None


def apply_google_details(conn, place_id: UUID | str, details: dict[str, Any]) -> None:
    display_name = (details.get("displayName") or {}).get("text")
    location = details.get("location") or {}
    primary_type = details.get("primaryType") or ""
    types = details.get("types") or []
    business_status = details.get("businessStatus")
    classification = classify_google_place(primary_type, types, display_name or "", "")
    update_fields = {
        "name": display_name,
        "phone": details.get("nationalPhoneNumber"),
        "website": details.get("websiteUri"),
        "address_text": details.get("formattedAddress"),
        "lat": location.get("latitude"),
        "lng": location.get("longitude"),
        "google_maps_url": details.get("googleMapsUri"),
        "category": classification[0] if classification else None,
        "subtype": classification[1] if classification else None,
    }
    assignments = [f"{key} = COALESCE(%({key})s, {key})" for key in update_fields]
    update_fields["id"] = str(place_id)
    conn.execute(
        f"""
        UPDATE places
        SET {", ".join(assignments)}
        WHERE id = %(id)s
        """,
        update_fields,
    )
    result = "uncertain"
    if business_status == "OPERATIONAL":
        result = "pass"
    elif business_status in {"CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY"}:
        result = "fail"
    conn.execute(
        """
        INSERT INTO verification_checks (place_id, check_type, result, details, evidence_url, checked_by)
        VALUES (%s, 'google_business_status', %s, %s, %s, 'google_places')
        """,
        (
            str(place_id),
            result,
            f"Google businessStatus={business_status or 'unknown'}",
            details.get("googleMapsUri"),
        ),
    )
    conn.execute(
        """
        INSERT INTO place_sources (place_id, source_type, source_url, source_confidence, raw_reference_id, raw_payload)
        VALUES (%s, 'google_places', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        (str(place_id), details.get("googleMapsUri"), 0.85, details.get("id") or "", Jsonb(details)),
    )


def check_website_active(website: str | None) -> dict[str, str] | None:
    if not website:
        return None
    try:
        with httpx.Client(timeout=12, follow_redirects=True) as client:
            response = client.head(website)
            if response.status_code in {405, 403}:
                response = client.get(website)
    except httpx.HTTPError as exc:
        return {"result": "uncertain", "details": f"Website check failed: {exc.__class__.__name__}"}
    if 200 <= response.status_code < 400:
        return {"result": "pass", "details": f"Website responded HTTP {response.status_code}"}
    if response.status_code == 404:
        return {"result": "fail", "details": "Website responded HTTP 404"}
    return {"result": "uncertain", "details": f"Website responded HTTP {response.status_code}"}


def discover_google_places(
    wilaya: str,
    queries: list[str] | None = None,
    included_types: list[str] | None = None,
    max_pages_per_query: int = 3,
) -> dict[str, Any]:
    settings = get_settings()
    queries = queries or [
        f"clothing store in {wilaya} Algeria",
        f"boutique vetement in {wilaya} Algeria",
        f"magasin vetements in {wilaya} Algeria",
        f"women clothing store in {wilaya} Algeria",
        f"men clothing store in {wilaya} Algeria",
        f"kids clothing store in {wilaya} Algeria",
        f"shoe store in {wilaya} Algeria",
        f"sportswear store in {wilaya} Algeria",
        f"delivery company in {wilaya} Algeria",
        f"courier service in {wilaya} Algeria",
        f"shipping service in {wilaya} Algeria",
        f"societe de livraison in {wilaya} Algeria",
    ]
    included_types = included_types or []

    with get_conn() as conn:
        run = conn.execute(
            """
            INSERT INTO ingestion_runs (wilaya, query, provider, status)
            VALUES (%s, %s, 'google_places', 'running')
            RETURNING id
            """,
            (wilaya, " | ".join(queries)),
        ).fetchone()
        run_id = run["id"]

    if not settings.places_key:
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE ingestion_runs
                SET status = 'skipped', finished_at = now(), error_message = 'GOOGLE_PLACES_API_KEY is not configured'
                WHERE id = %s
                """,
                (run_id,),
            )
        return {"run_id": str(run_id), "status": "skipped", "reason": "GOOGLE_PLACES_API_KEY is not configured", "candidates_found": 0}

    candidates_found = 0
    error_message = None
    try:
        for query in queries:
            for included_type in included_types or [None]:
                candidates_found += _text_search_google_places(wilaya, query, included_type, max_pages_per_query)
        status = "completed"
    except Exception as exc:  # pragma: no cover - guarded for worker reliability
        status = "failed"
        error_message = str(exc)

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE ingestion_runs
            SET status = %s, candidates_found = %s, finished_at = now(), error_message = %s
            WHERE id = %s
            """,
            (status, candidates_found, error_message, run_id),
        )
    return {"run_id": str(run_id), "status": status, "candidates_found": candidates_found, "error_message": error_message}


def _text_search_google_places(wilaya: str, query: str, included_type: str | None, max_pages_per_query: int) -> int:
    settings = get_settings()
    url = "https://places.googleapis.com/v1/places:searchText"
    field_mask = ",".join(
        [
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.businessStatus",
            "places.nationalPhoneNumber",
            "places.websiteUri",
            "places.googleMapsUri",
            "places.primaryType",
            "places.types",
        ]
    )
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.places_key,
        "X-Goog-FieldMask": field_mask,
    }
    body: dict[str, Any] = {
        "textQuery": query,
        "languageCode": settings.google_places_language,
        "regionCode": "DZ",
        "pageSize": 20,
    }
    if included_type:
        body["includedType"] = included_type

    total = 0
    page_token = None
    with httpx.Client(timeout=30) as client:
        for _ in range(max_pages_per_query):
            if page_token:
                body["pageToken"] = page_token
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("places", []):
                if upsert_google_candidate(wilaya, item, query):
                    total += 1
            page_token = payload.get("nextPageToken")
            if not page_token:
                break
    return total


def upsert_google_candidate(wilaya: str, item: dict[str, Any], query: str = "") -> bool:
    google_place_id = item.get("id")
    display_name = (item.get("displayName") or {}).get("text") or "Unnamed place"
    location = item.get("location") or {}
    primary_type = item.get("primaryType") or ""
    types = item.get("types") or []
    classification = classify_google_place(primary_type, types, display_name, query)
    if not classification:
        return False
    category, subtype = classification
    phone = item.get("nationalPhoneNumber")
    website = item.get("websiteUri")
    maps_url = item.get("googleMapsUri")
    business_status = item.get("businessStatus")
    score = 20 + (16 if business_status == "OPERATIONAL" else 0) + (12 if phone else 0) + (8 if website else 0)

    with get_conn() as conn:
        existing = None
        if google_place_id:
            existing = conn.execute("SELECT id FROM places WHERE google_place_id = %s", (google_place_id,)).fetchone()
        if existing:
            place_id = existing["id"]
            conn.execute(
                """
                UPDATE places
                SET name = %s, phone = COALESCE(%s, phone), website = COALESCE(%s, website),
                    address_text = COALESCE(%s, address_text), lat = %s, lng = %s,
                    google_maps_url = COALESCE(%s, google_maps_url), verification_score = GREATEST(verification_score, %s)
                WHERE id = %s
                """,
                (
                    display_name,
                    phone,
                    website,
                    item.get("formattedAddress"),
                    location.get("latitude"),
                    location.get("longitude"),
                    maps_url,
                    score,
                    place_id,
                ),
            )
        else:
            place_id = conn.execute(
                """
                INSERT INTO places (
                  name, category, subtype, phone, website, address_text, lat, lng, wilaya, source_status,
                  verification_score, google_place_id, google_maps_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'candidate', %s, %s, %s)
                RETURNING id
                """,
                (
                    display_name,
                    category,
                    subtype,
                    phone,
                    website,
                    item.get("formattedAddress"),
                    location.get("latitude"),
                    location.get("longitude"),
                    wilaya,
                    score,
                    google_place_id,
                    maps_url,
                ),
            ).fetchone()["id"]
        conn.execute(
            """
            INSERT INTO place_sources (place_id, source_type, source_url, source_confidence, raw_reference_id, raw_payload)
            VALUES (%s, 'google_places', %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (place_id, maps_url, 0.75, google_place_id or "", Jsonb(item)),
        )
        conn.execute(
            """
            INSERT INTO verification_checks (place_id, check_type, result, details, checked_by)
            VALUES (%s, 'google_business_status', %s, %s, 'google_places')
            """,
            (
                place_id,
                "pass" if business_status == "OPERATIONAL" else "uncertain",
                f"Google businessStatus={business_status or 'unknown'}",
            ),
        )
    return True


def classify_google_place(primary_type: str, types: list[str], name: str = "", query: str = "") -> tuple[str, str] | None:
    all_types = {primary_type, *types}
    if all_types & BLOCKED_TYPES:
        return None
    if all_types & DELIVERY_TYPES:
        subtype = primary_type if primary_type in DELIVERY_TYPES else next(iter(all_types & DELIVERY_TYPES))
        return "delivery_company", subtype
    if all_types & CLOTHING_TYPES:
        subtype = primary_type if primary_type in CLOTHING_TYPES else next(iter(all_types & CLOTHING_TYPES))
        return "clothing_store", subtype
    searchable = f"{name} {query}".lower()
    clothing_terms = [
        "clothing",
        "vetement",
        "vetements",
        "vêtement",
        "vêtements",
        "boutique",
        "mode",
        "fashion",
        "chaussure",
        "shoes",
        "sportswear",
        "kids clothing",
        "women clothing",
        "men clothing",
    ]
    delivery_terms = ["delivery", "livraison", "courier", "shipping", "transport", "logistique", "logistics"]
    generic_place_types = {"store", "point_of_interest", "establishment"}
    if all_types & generic_place_types and any(term in searchable for term in delivery_terms):
        return "delivery_company", "delivery_service"
    if all_types & generic_place_types and any(term in searchable for term in clothing_terms):
        return "clothing_store", "clothing_store"
    return None


def recalculate_clusters(wilaya: str, eps_m: int = 750, min_samples: int = 3) -> dict[str, Any]:
    with get_conn() as conn:
        stores = conn.execute(
            """
            SELECT id, name, lat, lng
            FROM places
            WHERE wilaya = %s
              AND category = 'clothing_store'
              AND source_status IN ('verified', 'manually_added')
            """,
            (wilaya,),
        ).fetchall()
        conn.execute(
            "DELETE FROM clusters WHERE wilaya = %s AND algorithm LIKE %s",
            (wilaya, "dbscan_%"),
        )

        summaries = run_dbscan(stores, eps_m, min_samples)
        for summary in summaries:
            cluster = conn.execute(
                """
                INSERT INTO clusters (wilaya, algorithm, centroid_lat, centroid_lng, store_count, radius_m, density_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    wilaya,
                    f"dbscan_eps_{eps_m}_min_{min_samples}",
                    summary["centroid_lat"],
                    summary["centroid_lng"],
                    summary["store_count"],
                    summary["radius_m"],
                    summary["density_score"],
                ),
            ).fetchone()
            for member in summary["stores"]:
                conn.execute(
                    """
                    INSERT INTO cluster_members (cluster_id, place_id, distance_to_centroid_m)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        cluster["id"],
                        member["id"],
                        round(haversine_m(summary["centroid_lat"], summary["centroid_lng"], member["lat"], member["lng"]), 2),
                    ),
                )
    return {"clusters": len(summaries), "stores_considered": len(stores)}


def list_clusters(wilaya: str | None = None) -> list[dict[str, Any]]:
    params: list[Any] = []
    sql = "SELECT * FROM clusters"
    if wilaya:
        sql += " WHERE wilaya = %s"
        params.append(wilaya)
    sql += " ORDER BY calculated_at DESC, store_count DESC"
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return normalize_record(rows)


def recalculate_distances(wilaya: str, use_google_routes: bool = False) -> dict[str, Any]:
    settings = get_settings()
    with get_conn() as conn:
        clusters = conn.execute("SELECT * FROM clusters WHERE wilaya = %s", (wilaya,)).fetchall()
        deliveries = conn.execute(
            """
            SELECT *
            FROM places
            WHERE wilaya = %s
              AND category = 'delivery_company'
              AND source_status IN ('verified', 'manually_added', 'candidate')
            """,
            (wilaya,),
        ).fetchall()
        conn.execute(
            """
            DELETE FROM cluster_delivery_distances
            WHERE cluster_id IN (SELECT id FROM clusters WHERE wilaya = %s)
            """,
            (wilaya,),
        )

        inserted = 0
        for cluster in clusters:
            for delivery in deliveries:
                straight = round(haversine_m(cluster["centroid_lat"], cluster["centroid_lng"], delivery["lat"], delivery["lng"]))
                driving = round(straight * 1.28)
                duration = round((driving / 1000) / 26 * 3600)
                provider = "straight_line_estimate"
                raw_payload = None
                if use_google_routes and settings.routes_key:
                    route = compute_google_route(cluster, delivery)
                    if route:
                        driving = route["distance_m"]
                        duration = route["duration_s"]
                        provider = "google_routes"
                        raw_payload = route.get("raw")
                conn.execute(
                    """
                    INSERT INTO cluster_delivery_distances (
                      cluster_id, delivery_company_id, driving_distance_m, driving_duration_s,
                      straight_line_distance_m, route_provider, route_raw_payload
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cluster_id, delivery_company_id) DO UPDATE
                    SET driving_distance_m = EXCLUDED.driving_distance_m,
                        driving_duration_s = EXCLUDED.driving_duration_s,
                        straight_line_distance_m = EXCLUDED.straight_line_distance_m,
                        route_provider = EXCLUDED.route_provider,
                        route_raw_payload = EXCLUDED.route_raw_payload,
                        calculated_at = now()
                    """,
                    (cluster["id"], delivery["id"], driving, duration, straight, provider, Jsonb(raw_payload) if raw_payload else None),
                )
                inserted += 1
    return {"distances": inserted, "clusters": len(clusters), "delivery_companies": len(deliveries)}


def compute_google_route(cluster: dict[str, Any], delivery: dict[str, Any]) -> dict[str, Any] | None:
    settings = get_settings()
    url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.routes_key,
        "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status,condition",
    }
    body = {
        "origins": [{"waypoint": {"location": {"latLng": {"latitude": cluster["centroid_lat"], "longitude": cluster["centroid_lng"]}}}}],
        "destinations": [{"waypoint": {"location": {"latLng": {"latitude": delivery["lat"], "longitude": delivery["lng"]}}}}],
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_UNAWARE",
    }
    with httpx.Client(timeout=30) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        rows = response.json()
    if not rows:
        return None
    row = rows[0]
    duration_text = row.get("duration", "0s")
    return {
        "distance_m": int(row.get("distanceMeters") or 0),
        "duration_s": parse_google_duration(duration_text),
        "raw": row,
    }


def list_cluster_distances(wilaya: str | None = None) -> list[dict[str, Any]]:
    params: list[Any] = []
    sql = """
      SELECT
        c.id AS cluster_id,
        c.wilaya,
        c.store_count,
        c.radius_m,
        c.density_score,
        c.centroid_lat,
        c.centroid_lng,
        p.id AS delivery_company_id,
        p.name AS delivery_company_name,
        cdd.driving_distance_m,
        cdd.driving_duration_s,
        cdd.straight_line_distance_m,
        cdd.route_provider,
        cdd.calculated_at
      FROM cluster_delivery_distances cdd
      JOIN clusters c ON c.id = cdd.cluster_id
      JOIN places p ON p.id = cdd.delivery_company_id
    """
    if wilaya:
        sql += " WHERE c.wilaya = %s"
        params.append(wilaya)
    sql += " ORDER BY c.store_count DESC, cdd.driving_distance_m ASC"
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return normalize_record(rows)


def export_places_csv(filters: dict[str, Any]) -> str:
    rows = list_places(filters)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=PLACE_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def export_places_geojson(filters: dict[str, Any]) -> dict[str, Any]:
    rows = list_places(filters)
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row["lng"], row["lat"]]},
                "properties": {key: value for key, value in row.items() if key not in ["lat", "lng"]},
            }
            for row in rows
        ],
    }


def import_places_csv(content: bytes) -> dict[str, Any]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    added = 0
    skipped = 0
    for record in reader:
        try:
            payload = PlaceCreate(
                name=record["name"],
                category=record.get("category") or "clothing_store",
                subtype=record.get("subtype") or None,
                phone=record.get("phone") or None,
                website=record.get("website") or None,
                address_text=record.get("address_text") or None,
                lat=float(record["lat"]),
                lng=float(record["lng"]),
                wilaya=record.get("wilaya") or "Oran",
                commune=record.get("commune") or None,
                source_status=record.get("source_status") or "candidate",
                verification_score=int(record.get("verification_score") or 35),
                google_place_id=record.get("google_place_id") or None,
                google_maps_url=record.get("google_maps_url") or None,
            )
            create_place(payload, source_type="csv_upload")
            added += 1
        except Exception:
            skipped += 1
    return {"added": added, "skipped": skipped}


def run_dbscan(points: list[dict[str, Any]], eps_m: int, min_samples: int) -> list[dict[str, Any]]:
    visited: set[Any] = set()
    clustered: set[Any] = set()
    clusters: list[list[dict[str, Any]]] = []

    for point in points:
        if point["id"] in visited:
            continue
        visited.add(point["id"])
        neighbors = region_query(points, point, eps_m)
        if len(neighbors) < min_samples:
            continue
        cluster: list[dict[str, Any]] = []
        expand_cluster(points, point, neighbors, cluster, visited, clustered, eps_m, min_samples)
        clusters.append(cluster)
    return [cluster_summary(cluster) for cluster in clusters]


def expand_cluster(points, point, neighbors, cluster, visited, clustered, eps_m, min_samples) -> None:
    cluster.append(point)
    clustered.add(point["id"])
    queue = list(neighbors)
    while queue:
        current = queue.pop(0)
        if current["id"] not in visited:
            visited.add(current["id"])
            current_neighbors = region_query(points, current, eps_m)
            if len(current_neighbors) >= min_samples:
                for neighbor in current_neighbors:
                    if neighbor not in queue:
                        queue.append(neighbor)
        if current["id"] not in clustered:
            cluster.append(current)
            clustered.add(current["id"])


def region_query(points, point, eps_m: int) -> list[dict[str, Any]]:
    return [candidate for candidate in points if haversine_m(point["lat"], point["lng"], candidate["lat"], candidate["lng"]) <= eps_m]


def cluster_summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    centroid_lat = sum(point["lat"] for point in points) / len(points)
    centroid_lng = sum(point["lng"] for point in points) / len(points)
    distances = [haversine_m(centroid_lat, centroid_lng, point["lat"], point["lng"]) for point in points]
    radius_m = max(distances) if distances else 0
    area_km2 = math.pi * max(radius_m / 1000, 0.001) ** 2
    return {
        "centroid_lat": centroid_lat,
        "centroid_lng": centroid_lng,
        "store_count": len(points),
        "radius_m": round(radius_m, 2),
        "density_score": round(len(points) / max(area_km2, 0.01), 3),
        "stores": points,
    }


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371000
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_google_duration(value: str) -> int:
    if value.endswith("s"):
        return int(float(value[:-1]))
    return 0
