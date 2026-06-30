from __future__ import annotations

import csv
import io
import json
import math
import os
import mimetypes
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlparse
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend" / "app"
DATA_FILE = ROOT / "work" / "local_demo_data.json"
PORT = int(os.environ.get("PORT", "8000"))

WILAYA_CENTERS = {
    "Adrar": (27.874, -0.293), "Chlef": (36.165, 1.334), "Laghouat": (33.806, 2.881),
    "Oum El Bouaghi": (35.877, 7.113), "Batna": (35.555, 6.174), "Bejaia": (36.752, 5.056),
    "Béjaïa": (36.752, 5.056), "Biskra": (34.848, 5.728), "Bechar": (31.617, -2.220),
    "Béchar": (31.617, -2.220), "Blida": (36.472, 2.833), "Bouira": (36.374, 3.902),
    "Tamanrasset": (22.785, 5.522), "Tebessa": (35.405, 8.120), "Tébessa": (35.405, 8.120),
    "Tlemcen": (34.882, -1.316), "Tiaret": (35.371, 1.317), "Tizi Ouzou": (36.717, 4.050),
    "Alger": (36.754, 3.059), "Djelfa": (34.672, 3.263), "Jijel": (36.821, 5.767),
    "Setif": (36.191, 5.414), "Sétif": (36.191, 5.414), "Saida": (34.841, 0.148),
    "Saïda": (34.841, 0.148), "Skikda": (36.879, 6.907), "Sidi Bel Abbes": (35.193, -0.641),
    "Sidi Bel Abbès": (35.193, -0.641), "Annaba": (36.900, 7.766), "Guelma": (36.462, 7.428),
    "Constantine": (36.365, 6.615), "Medea": (36.264, 2.753), "Médéa": (36.264, 2.753),
    "Mostaganem": (35.933, 0.090), "Msila": (35.705, 4.541), "M'Sila": (35.705, 4.541),
    "Mascara": (35.397, 0.140), "Ouargla": (31.953, 5.325), "Oran": (35.697, -0.631),
    "El Bayadh": (33.684, 1.020), "Illizi": (26.483, 8.467), "Bordj Bou Arreridj": (36.073, 4.761),
    "Boumerdes": (36.758, 3.477), "Boumerdès": (36.758, 3.477), "El Tarf": (36.767, 8.313),
    "Tindouf": (27.671, -8.148), "Tissemsilt": (35.607, 1.811), "El Oued": (33.371, 6.867),
    "Khenchela": (35.435, 7.143), "Souk Ahras": (36.286, 7.951), "Tipaza": (36.590, 2.449),
    "Mila": (36.451, 6.264), "Ain Defla": (36.264, 1.968), "Aïn Defla": (36.264, 1.968),
    "Naama": (33.267, -0.313), "Naâma": (33.267, -0.313), "Ain Temouchent": (35.300, -1.140),
    "Aïn Témouchent": (35.300, -1.140), "Ghardaia": (32.490, 3.673), "Ghardaïa": (32.490, 3.673),
    "Relizane": (35.738, 0.556), "Timimoun": (29.263, 0.231), "Bordj Badji Mokhtar": (21.327, 0.946),
    "Ouled Djellal": (34.426, 5.065), "Beni Abbes": (30.133, -2.167), "Béni Abbès": (30.133, -2.167),
    "In Salah": (27.193, 2.461), "In Guezzam": (19.568, 5.772), "Touggourt": (33.105, 6.057),
    "Djanet": (24.555, 9.485), "El Meghaier": (33.954, 5.922), "El Meniaa": (30.583, 2.883),
}

WILAYA_ALIASES = {
    "algeries": "Alger",
    "algiers": "Alger",
    "algeria": "Alger",
    "alger": "Alger",
    "setif": "Setif",
    "sétif": "Setif",
    "oran": "Oran",
}

CLOTHING_TYPES = {
    "clothing_store",
    "shoe_store",
    "sportswear_store",
    "womens_clothing_store",
    "mens_clothing_store",
    "childrens_clothing_store",
    "fashion_accessories_store",
    "store",
    "point_of_interest",
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


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_data() -> dict:
    places = [
        place("Mode El Bahia", "clothing_store", "women", 35.6993, -0.6352, "Oran", "Oran", "verified", 86, "+213 41 22 10 01"),
        place("Boutique Jasmin", "clothing_store", "women", 35.7011, -0.6331, "Oran", "Oran", "verified", 74, "+213 41 22 10 02"),
        place("City Wear Oran", "clothing_store", "men", 35.6968, -0.6370, "Oran", "Oran", "candidate", 58, "+213 41 22 10 03"),
        place("Kids Corner Oran", "clothing_store", "kids", 35.6936, -0.6287, "Oran", "Oran", "verified", 68, ""),
        place("Sport Mode Akid", "clothing_store", "sportswear", 35.7302, -0.5564, "Oran", "Bir El Djir", "verified", 82, "+213 41 22 10 06"),
        place("Boutique Narjess", "clothing_store", "women", 35.7281, -0.5596, "Oran", "Bir El Djir", "candidate", 52, ""),
        place("Urban Shoes Oran", "clothing_store", "shoe_store", 35.7270, -0.5535, "Oran", "Bir El Djir", "verified", 77, "+213 41 22 10 08"),
        place("Es Senia Fashion", "clothing_store", "general", 35.6512, -0.6243, "Oran", "Es Senia", "verified", 81, "+213 41 22 10 09"),
        place("Boutique Salam", "clothing_store", "men", 35.6539, -0.6206, "Oran", "Es Senia", "candidate", 47, ""),
        place("Yalidine Oran Hub", "delivery_company", "courier", 35.6910, -0.6159, "Oran", "Oran", "verified", 92, "+213 41 55 10 01"),
        place("ZR Express Oran", "delivery_company", "last_mile", 35.7234, -0.5682, "Oran", "Bir El Djir", "verified", 88, "+213 41 55 10 02"),
        place("Nord Ouest Livraison", "delivery_company", "shipping", 35.6628, -0.6125, "Oran", "Es Senia", "candidate", 61, "+213 41 55 10 03"),
    ]
    return {"places": places, "checks": [], "clusters": [], "distances": []}


def place(name, category, subtype, lat, lng, wilaya, commune, status, score, phone):
    ts = now()
    return {
        "id": str(uuid4()),
        "name": name,
        "category": category,
        "subtype": subtype,
        "phone": phone or None,
        "website": None,
        "address_text": commune,
        "lat": lat,
        "lng": lng,
        "wilaya": wilaya,
        "commune": commune,
        "source_status": status,
        "verification_score": score,
        "last_verified_at": ts if status == "verified" else None,
        "google_place_id": f"demo-{name.lower().replace(' ', '-')}",
        "google_maps_url": f"https://maps.google.com/?q={name.replace(' ', '+')}",
        "created_at": ts,
        "updated_at": ts,
    }


def load_data() -> dict:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_data(seed_data())
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def env_value(key: str, default: str = "") -> str:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return default
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip()
    return default


class QuietThreadingHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        exc_type, _, _ = sys.exc_info()
        if exc_type in (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            return
        super().handle_error(request, client_address)


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.add_cors_headers()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self.json({"ok": True, "service": "local-demo-api"})
        if parsed.path == "/places":
            return self.json(filter_places(load_data()["places"], parse_qs(parsed.query)))
        if parsed.path == "/clusters":
            data = load_data()
            wilaya = parse_qs(parsed.query).get("wilaya", [None])[0]
            rows = [c for c in data["clusters"] if not wilaya or c["wilaya"] == wilaya]
            return self.json(rows)
        if parsed.path == "/cluster-distances":
            data = load_data()
            wilaya = parse_qs(parsed.query).get("wilaya", [None])[0]
            rows = [d for d in data["distances"] if not wilaya or d["wilaya"] == wilaya]
            return self.json(rows)
        if parsed.path == "/exports/places.csv":
            return self.csv_export(filter_places(load_data()["places"], parse_qs(parsed.query)))
        if parsed.path == "/exports/places.geojson":
            return self.geojson_export(filter_places(load_data()["places"], parse_qs(parsed.query)))
        return self.static_file(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/places":
            body = self.read_json()
            data = load_data()
            body.update({"id": str(uuid4()), "created_at": now(), "updated_at": now(), "last_verified_at": now() if body.get("source_status") == "verified" else None})
            data["places"].append(body)
            save_data(data)
            return self.json(body, status=201)
        if parsed.path.endswith("/verification-checks"):
            place_id = parsed.path.split("/")[2]
            data = load_data()
            check = self.read_json()
            check.update({"id": str(uuid4()), "place_id": place_id, "checked_at": now()})
            data["checks"].append(check)
            for p in data["places"]:
                if p["id"] == place_id:
                    p["verification_score"] = min(100, p.get("verification_score", 0) + (15 if check.get("result") == "pass" else 3))
                    if p["verification_score"] >= 75 and p["source_status"] == "candidate":
                        p["source_status"] = "verified"
                        p["last_verified_at"] = now()
                    p["updated_at"] = now()
            save_data(data)
            return self.json({"ok": True, "message": "Verification check added", "data": {"check": check}})
        if parsed.path == "/verification/run":
            data = load_data()
            body = self.read_json()
            count = 0
            for p in data["places"]:
                if body.get("wilaya") and p["wilaya"] != body["wilaya"]:
                    continue
                if p.get("phone"):
                    p["verification_score"] = min(100, p.get("verification_score", 0) + 5)
                if p["verification_score"] >= 75 and p["source_status"] == "candidate":
                    p["source_status"] = "verified"
                    p["last_verified_at"] = now()
                p["updated_at"] = now()
                count += 1
            save_data(data)
            return self.json({"ok": True, "message": "Verification pass completed", "data": {"updated": count}})
        if parsed.path == "/ingestion/google-places":
            return self.google_places_ingestion()
        if parsed.path == "/analysis/clusters/recalculate":
            body = self.read_json()
            return self.recalculate_clusters(body.get("wilaya", "Oran"), int(body.get("eps_m", 750)), int(body.get("min_samples", 3)))
        if parsed.path == "/analysis/distances/recalculate":
            body = self.read_json()
            return self.recalculate_distances(body.get("wilaya", "Oran"))
        if parsed.path == "/ingestion/nightly-refresh":
            qs = parse_qs(parsed.query)
            wilaya = qs.get("wilaya", ["Oran"])[0]
            self.demo_ingestion(wilaya=wilaya, save=True)
            self.recalculate_clusters_raw(wilaya, 750, 3)
            result = self.recalculate_distances_raw(wilaya)
            return self.json({"ok": True, "message": "Nightly refresh finished", "data": result})
        if parsed.path == "/imports/places.csv":
            return self.json({"ok": False, "message": "CSV upload is available in Docker/FastAPI mode; use manual add in local demo."}, status=501)
        return self.not_found()

    def do_PATCH(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/places/"):
            place_id = parsed.path.split("/")[2]
            body = self.read_json()
            data = load_data()
            for p in data["places"]:
                if p["id"] == place_id:
                    p.update(body)
                    p["updated_at"] = now()
                    save_data(data)
                    return self.json(p)
        return self.not_found()

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/places/"):
            place_id = parsed.path.split("/")[2]
            data = load_data()
            for p in data["places"]:
                if p["id"] == place_id:
                    p["source_status"] = "rejected"
                    p["updated_at"] = now()
                    save_data(data)
                    return self.json({"ok": True, "message": "Place rejected/deactivated"})
        return self.not_found()

    def recalculate_clusters(self, wilaya, eps_m, min_samples):
        result = self.recalculate_clusters_raw(wilaya, eps_m, min_samples)
        return self.json({"ok": True, "message": "Clusters recalculated", "data": result})

    def recalculate_clusters_raw(self, wilaya, eps_m, min_samples):
        data = load_data()
        stores = [p for p in data["places"] if p["wilaya"] == wilaya and p["category"] == "clothing_store" and p["source_status"] in ["verified", "manually_added"]]
        if not stores:
            stores = [p for p in data["places"] if p["wilaya"] == wilaya and p["category"] == "clothing_store" and p["source_status"] == "candidate"]
        clusters = run_dbscan(stores, eps_m, min_samples)
        data["clusters"] = [c for c in data["clusters"] if c["wilaya"] != wilaya] + clusters
        save_data(data)
        return {"clusters": len(clusters), "stores_considered": len(stores)}

    def recalculate_distances(self, wilaya):
        result = self.recalculate_distances_raw(wilaya)
        return self.json({"ok": True, "message": "Cluster delivery distances recalculated", "data": result})

    def recalculate_distances_raw(self, wilaya):
        data = load_data()
        clusters = [c for c in data["clusters"] if c["wilaya"] == wilaya]
        deliveries = [p for p in data["places"] if p["wilaya"] == wilaya and p["category"] == "delivery_company" and p["source_status"] != "rejected"]
        rows = []
        for c in clusters:
            for d in deliveries:
                straight = round(haversine(c["centroid_lat"], c["centroid_lng"], d["lat"], d["lng"]))
                driving = round(straight * 1.28)
                rows.append({
                    "cluster_id": c["id"],
                    "wilaya": wilaya,
                    "store_count": c["store_count"],
                    "radius_m": c["radius_m"],
                    "density_score": c["density_score"],
                    "centroid_lat": c["centroid_lat"],
                    "centroid_lng": c["centroid_lng"],
                    "delivery_company_id": d["id"],
                    "delivery_company_name": d["name"],
                    "driving_distance_m": driving,
                    "driving_duration_s": round((driving / 1000) / 26 * 3600),
                    "straight_line_distance_m": straight,
                    "route_provider": "local_demo_estimate",
                    "calculated_at": now(),
                })
        data["distances"] = [r for r in data["distances"] if r["wilaya"] != wilaya] + rows
        save_data(data)
        return {"distances": len(rows), "clusters": len(clusters), "delivery_companies": len(deliveries)}

    def google_places_ingestion(self):
        body = self.read_json()
        raw_wilaya = body.get("wilaya") or "Oran"
        wilaya = resolve_wilaya_name(raw_wilaya)
        queries = body.get("queries") or default_queries(wilaya)
        max_pages = min(max(int(body.get("max_pages_per_query") or 1), 1), 3)
        key = env_value("GOOGLE_PLACES_API_KEY") or env_value("GOOGLE_MAPS_API_KEY")
        if key:
            try:
                result = ingest_real_google_places(wilaya, queries, max_pages, key)
                return self.json({"ok": True, "message": "Google Places ingestion finished", "data": result})
            except Exception as exc:
                result = self.demo_ingestion(wilaya=wilaya, save=True, reason=f"Google API failed: {exc}")
                return self.json({"ok": True, "message": "Google Places fallback demo finished", "data": result})
        result = self.demo_ingestion(wilaya=wilaya, save=True, reason="GOOGLE_PLACES_API_KEY missing")
        return self.json({"ok": True, "message": "Google Places fallback demo finished", "data": result})

    def demo_ingestion(self, wilaya=None, save=True, reason="local_demo"):
        if wilaya is None:
            body = self.read_json()
            wilaya = resolve_wilaya_name(body.get("wilaya") or "Oran")
        data = load_data()
        lat, lng = center_for_wilaya(wilaya)
        index = len([p for p in data["places"] if p.get("wilaya") == wilaya]) + 1
        store_specs = [
            ("Mode", "women", 0.002, 0.002),
            ("Boutique", "general", 0.006, -0.004),
            ("Kids Wear", "kids", -0.003, 0.004),
            ("Men Style", "men", -0.006, -0.003),
            ("Shoes", "shoe_store", 0.010, 0.006),
            ("Sportswear", "sportswear", -0.009, 0.008),
            ("Fashion", "women", 0.014, -0.007),
            ("Outlet", "general", -0.013, -0.009),
        ]
        delivery_specs = [
            ("Livraison", "courier", -0.004, 0.005),
            ("Express", "last_mile", 0.012, -0.012),
            ("Shipping", "shipping", -0.014, 0.013),
        ]
        candidates = [
            place(f"{wilaya} {label} Candidate {index + offset}", "clothing_store", subtype, lat + dlat, lng + dlng, wilaya, wilaya, "candidate", 45 + (offset % 4), "")
            for offset, (label, subtype, dlat, dlng) in enumerate(store_specs, start=1)
        ]
        candidates.extend(
            place(f"{wilaya} {label} Candidate {index + len(store_specs) + offset}", "delivery_company", subtype, lat + dlat, lng + dlng, wilaya, wilaya, "candidate", 55 + (offset % 5), "")
            for offset, (label, subtype, dlat, dlng) in enumerate(delivery_specs, start=1)
        )
        data["places"].extend(candidates)
        if save:
            save_data(data)
        return {"status": "local_demo", "reason": reason, "wilaya": wilaya, "candidates_found": len(candidates)}

    def read_json(self):
        length = int(self.headers.get("content-length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    def json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.add_cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def add_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "false")

    def static_file(self, path):
        if path in ["", "/"]:
            path = "/index.html"
        file_path = (FRONTEND / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(FRONTEND.resolve())) or not file_path.exists():
            return self.not_found()
        body = file_path.read_bytes()
        if file_path.name == "config.js":
            browser_key = env_value("NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY")
            body = f'window.APP_CONFIG = {{ apiUrl: "", googleMapsApiKey: "{browser_key}" }};\n'.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def csv_export(self, rows):
        output = io.StringIO()
        fieldnames = list(rows[0].keys()) if rows else ["id", "name", "category", "lat", "lng", "wilaya"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        body = output.getvalue().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv")
        self.send_header("Content-Disposition", 'attachment; filename="places.csv"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def geojson_export(self, rows):
        return self.json({
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": {"type": "Point", "coordinates": [p["lng"], p["lat"]]}, "properties": {k: v for k, v in p.items() if k not in ["lat", "lng"]}}
                for p in rows
            ],
        })

    def not_found(self):
        return self.json({"ok": False, "message": "Not found"}, status=404)

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))


def filter_places(places, qs):
    rows = [p for p in places if p.get("category") in ["clothing_store", "delivery_company"]]
    for key in ["wilaya", "commune", "category", "source_status"]:
        value = qs.get(key, [None])[0]
        if value:
            rows = [p for p in rows if str(p.get(key)) == value]
    q = qs.get("q", [None])[0]
    if q:
        rows = [p for p in rows if q.lower() in p["name"].lower()]
    return rows


def ingest_real_google_places(wilaya, queries, max_pages, key):
    data = load_data()
    found = 0
    saved = 0
    skipped = 0
    errors = []
    for query in queries:
        try:
            places = google_text_search(query, key, max_pages)
        except Exception as exc:
            errors.append(f"{query}: {exc}")
            continue
        found += len(places)
        for item in places:
            converted = convert_google_place(wilaya, item, query)
            if not converted:
                skipped += 1
                continue
            if upsert_place(data, converted):
                saved += 1
    save_data(data)
    return {
        "status": "google_places",
        "wilaya": wilaya,
        "queries": len(queries),
        "candidates_found": saved,
        "raw_found": found,
        "skipped_non_target": skipped,
        "errors": errors[:3],
    }


def google_text_search(query, key, max_pages):
    url = "https://places.googleapis.com/v1/places:searchText"
    field_mask = ",".join([
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
    ])
    body = {
        "textQuery": query,
        "languageCode": env_value("GOOGLE_PLACES_LANGUAGE", "fr") or "fr",
        "regionCode": "DZ",
        "pageSize": 20,
    }
    results = []
    page_token = None
    for _ in range(max_pages):
        if page_token:
            body["pageToken"] = page_token
        payload = json.dumps(body).encode("utf-8")
        request = Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": key,
                "X-Goog-FieldMask": field_mask,
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} {detail[:280]}") from exc
        except URLError as exc:
            raise RuntimeError(str(exc)) from exc
        results.extend(parsed.get("places", []))
        page_token = parsed.get("nextPageToken")
        if not page_token:
            break
    return results


def convert_google_place(wilaya, item, query):
    location = item.get("location") or {}
    lat = location.get("latitude")
    lng = location.get("longitude")
    if lat is None or lng is None:
        return None
    primary_type = item.get("primaryType") or ""
    types = item.get("types") or []
    classification = classify_google_place(primary_type, types, query)
    if not classification:
        return None
    category, subtype = classification
    name = (item.get("displayName") or {}).get("text") or "Unnamed place"
    business_status = item.get("businessStatus")
    phone = item.get("nationalPhoneNumber")
    website = item.get("websiteUri")
    score = 20 + (16 if business_status == "OPERATIONAL" else 0) + (12 if phone else 0) + (8 if website else 0)
    ts = now()
    return {
        "id": str(uuid4()),
        "name": name,
        "category": category,
        "subtype": subtype,
        "phone": phone,
        "website": website,
        "address_text": item.get("formattedAddress"),
        "lat": lat,
        "lng": lng,
        "wilaya": wilaya,
        "commune": wilaya,
        "source_status": "candidate",
        "verification_score": score,
        "last_verified_at": None,
        "google_place_id": item.get("id"),
        "google_maps_url": item.get("googleMapsUri"),
        "created_at": ts,
        "updated_at": ts,
    }


def classify_google_place(primary_type, types, query):
    all_types = {primary_type, *types}
    query_l = query.lower()
    if all_types & BLOCKED_TYPES:
        return None
    if all_types & DELIVERY_TYPES or any(word in query_l for word in ["delivery", "courier", "shipping", "livraison"]):
        subtype = primary_type if primary_type in DELIVERY_TYPES else next(iter(all_types & DELIVERY_TYPES), "courier")
        return "delivery_company", subtype
    clothing_words = ["clothing", "vetement", "vêtement", "boutique", "fashion", "mode", "shoe", "sportswear"]
    if all_types & CLOTHING_TYPES or any(word in query_l for word in clothing_words):
        subtype = primary_type if primary_type in CLOTHING_TYPES else next(iter(all_types & CLOTHING_TYPES), "general")
        return "clothing_store", subtype
    return None


def upsert_place(data, incoming):
    google_id = incoming.get("google_place_id")
    for place_record in data["places"]:
        same_google = google_id and place_record.get("google_place_id") == google_id
        same_near_name = (
            normalize_name(place_record.get("name")) == normalize_name(incoming.get("name"))
            and place_record.get("wilaya") == incoming.get("wilaya")
            and haversine(place_record.get("lat"), place_record.get("lng"), incoming.get("lat"), incoming.get("lng")) < 80
        )
        if same_google or same_near_name:
            place_record.update({k: v for k, v in incoming.items() if v not in [None, ""] and k not in ["id", "created_at"]})
            place_record["updated_at"] = now()
            return False
    data["places"].append(incoming)
    return True


def default_queries(wilaya):
    return [
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


def resolve_wilaya_name(value):
    normalized = normalize_name(value)
    if normalized in WILAYA_ALIASES:
        return WILAYA_ALIASES[normalized]
    for name in WILAYA_CENTERS:
        if normalize_name(name) == normalized:
            return name
    return str(value or "Oran").strip() or "Oran"


def center_for_wilaya(wilaya):
    wilaya = resolve_wilaya_name(wilaya)
    if wilaya in WILAYA_CENTERS:
        return WILAYA_CENTERS[wilaya]
    normalized = normalize_name(wilaya)
    for name, center in WILAYA_CENTERS.items():
        if normalize_name(name) == normalized:
            return center
    return (28.0339, 1.6596)


def normalize_name(value):
    return "".join(ch for ch in str(value or "").lower().replace("'", "") if ch.isalnum() or ch.isspace()).strip()


def run_dbscan(points, eps_m, min_samples):
    visited = set()
    clustered = set()
    clusters = []
    for point in points:
        if point["id"] in visited:
            continue
        visited.add(point["id"])
        neighbors = [p for p in points if haversine(point["lat"], point["lng"], p["lat"], p["lng"]) <= eps_m]
        if len(neighbors) < min_samples:
            continue
        cluster = []
        queue = list(neighbors)
        cluster.append(point)
        clustered.add(point["id"])
        while queue:
            current = queue.pop(0)
            if current["id"] not in visited:
                visited.add(current["id"])
                current_neighbors = [p for p in points if haversine(current["lat"], current["lng"], p["lat"], p["lng"]) <= eps_m]
                if len(current_neighbors) >= min_samples:
                    queue.extend([p for p in current_neighbors if p not in queue])
            if current["id"] not in clustered:
                cluster.append(current)
                clustered.add(current["id"])
        clusters.append(cluster)
    return [cluster_summary(c) for c in clusters]


def cluster_summary(points):
    lat = sum(p["lat"] for p in points) / len(points)
    lng = sum(p["lng"] for p in points) / len(points)
    radius = max(haversine(lat, lng, p["lat"], p["lng"]) for p in points)
    area = math.pi * max(radius / 1000, 0.001) ** 2
    return {
        "id": str(uuid4()),
        "wilaya": points[0]["wilaya"],
        "algorithm": "local_demo_dbscan",
        "centroid_lat": lat,
        "centroid_lng": lng,
        "store_count": len(points),
        "radius_m": round(radius, 2),
        "density_score": round(len(points) / max(area, 0.01), 3),
        "calculated_at": now(),
    }


def haversine(lat1, lng1, lat2, lng2):
    radius = 6371000
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


if __name__ == "__main__":
    load_data()
    server = QuietThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Local demo running at http://127.0.0.1:{PORT}")
    print("This demo uses work/local_demo_data.json and does not require Docker, Postgres, Redis, or API keys.")
    server.serve_forever()
