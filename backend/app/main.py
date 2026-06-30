from typing import Literal
from uuid import UUID

from fastapi import FastAPI, File, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import close_pool, open_pool
from app.schemas import (
    ApiMessage,
    ClusterRequest,
    DistanceRequest,
    IngestionRequest,
    PlaceCreate,
    PlaceOut,
    PlacePatch,
    VerificationCheckCreate,
    VerificationRunRequest,
)
from app.services import (
    add_verification_check,
    create_place,
    discover_google_places,
    export_places_csv,
    export_places_geojson,
    get_place,
    import_places_csv,
    list_cluster_distances,
    list_clusters,
    list_places,
    recalculate_clusters,
    recalculate_distances,
    remove_place,
    run_verification,
    update_place,
)
from app.worker import ingest_google_places_task, nightly_refresh_task


settings = get_settings()
app = FastAPI(title="Wilaya Retail And Delivery Coverage API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    open_pool()


@app.on_event("shutdown")
def shutdown() -> None:
    close_pool()


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "retail-delivery-api"}


@app.get("/places", response_model=list[PlaceOut])
def api_list_places(
    wilaya: str | None = None,
    commune: str | None = None,
    category: Literal["clothing_store", "delivery_company"] | None = None,
    source_status: Literal["candidate", "verified", "rejected", "manually_added"] | None = None,
    q: str | None = None,
    min_score: int | None = Query(default=None, ge=0, le=100),
    limit: int = Query(default=500, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    return list_places(
        {
            "wilaya": wilaya,
            "commune": commune,
            "category": category,
            "source_status": source_status,
            "q": q,
            "min_score": min_score,
            "limit": limit,
            "offset": offset,
        }
    )


@app.get("/places/{place_id}", response_model=PlaceOut)
def api_get_place(place_id: UUID) -> dict:
    place = get_place(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@app.post("/places", response_model=PlaceOut, status_code=201)
def api_create_place(payload: PlaceCreate) -> dict:
    return create_place(payload)


@app.patch("/places/{place_id}", response_model=PlaceOut)
def api_update_place(place_id: UUID, payload: PlacePatch) -> dict:
    place = update_place(place_id, payload)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@app.delete("/places/{place_id}", response_model=ApiMessage)
def api_remove_place(place_id: UUID, hard: bool = False) -> ApiMessage:
    removed = remove_place(place_id, hard=hard)
    if not removed:
        raise HTTPException(status_code=404, detail="Place not found")
    return ApiMessage(message="Place removed" if hard else "Place rejected/deactivated")


@app.post("/places/{place_id}/verification-checks", response_model=ApiMessage)
def api_add_verification_check(place_id: UUID, payload: VerificationCheckCreate) -> ApiMessage:
    check = add_verification_check(place_id, payload)
    if not check:
        raise HTTPException(status_code=404, detail="Place not found")
    return ApiMessage(message="Verification check added", data={"check": check})


@app.post("/verification/run", response_model=ApiMessage)
def api_run_verification(payload: VerificationRunRequest) -> ApiMessage:
    result = run_verification(payload.wilaya, payload.place_id)
    return ApiMessage(message="Verification pass completed", data=result)


@app.post("/ingestion/google-places", response_model=ApiMessage)
def api_ingest_google_places(payload: IngestionRequest) -> ApiMessage:
    if payload.enqueue:
        task = ingest_google_places_task.delay(
            payload.wilaya,
            payload.queries,
            payload.included_types,
            payload.max_pages_per_query,
        )
        return ApiMessage(message="Google Places ingestion queued", data={"task_id": task.id})
    result = discover_google_places(
        wilaya=payload.wilaya,
        queries=payload.queries,
        included_types=payload.included_types,
        max_pages_per_query=payload.max_pages_per_query,
    )
    return ApiMessage(message="Google Places ingestion finished", data=result)


@app.post("/ingestion/nightly-refresh", response_model=ApiMessage)
def api_nightly_refresh(wilaya: str = Query(default=settings.default_wilaya), enqueue: bool = True) -> ApiMessage:
    if enqueue:
        task = nightly_refresh_task.delay(wilaya)
        return ApiMessage(message="Nightly refresh queued", data={"task_id": task.id})
    result = nightly_refresh_task.run(wilaya)
    return ApiMessage(message="Nightly refresh finished", data=result)


@app.post("/analysis/clusters/recalculate", response_model=ApiMessage)
def api_recalculate_clusters(payload: ClusterRequest) -> ApiMessage:
    result = recalculate_clusters(payload.wilaya, payload.eps_m, payload.min_samples)
    return ApiMessage(message="Clusters recalculated", data=result)


@app.post("/analysis/distances/recalculate", response_model=ApiMessage)
def api_recalculate_distances(payload: DistanceRequest) -> ApiMessage:
    result = recalculate_distances(payload.wilaya, payload.use_google_routes)
    return ApiMessage(message="Cluster delivery distances recalculated", data=result)


@app.get("/clusters")
def api_list_clusters(wilaya: str | None = None) -> list[dict]:
    return list_clusters(wilaya)


@app.get("/cluster-distances")
def api_list_cluster_distances(wilaya: str | None = None) -> list[dict]:
    return list_cluster_distances(wilaya)


@app.post("/imports/places.csv", response_model=ApiMessage)
async def api_import_places_csv(file: UploadFile = File(...)) -> ApiMessage:
    content = await file.read()
    result = import_places_csv(content)
    return ApiMessage(message="CSV import finished", data=result)


@app.get("/exports/places.csv")
def api_export_places_csv(
    wilaya: str | None = None,
    commune: str | None = None,
    category: Literal["clothing_store", "delivery_company"] | None = None,
    source_status: Literal["candidate", "verified", "rejected", "manually_added"] | None = None,
) -> Response:
    content = export_places_csv(
        {"wilaya": wilaya, "commune": commune, "category": category, "source_status": source_status, "limit": 5000, "offset": 0}
    )
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="places.csv"'},
    )


@app.get("/exports/places.geojson")
def api_export_places_geojson(
    wilaya: str | None = None,
    commune: str | None = None,
    category: Literal["clothing_store", "delivery_company"] | None = None,
    source_status: Literal["candidate", "verified", "rejected", "manually_added"] | None = None,
) -> dict:
    return export_places_geojson(
        {"wilaya": wilaya, "commune": commune, "category": category, "source_status": source_status, "limit": 5000, "offset": 0}
    )
