from celery import Celery
from celery.schedules import crontab

from app.config import get_settings
from app.db import open_pool
from app.services import discover_google_places, recalculate_clusters, recalculate_distances, run_verification


settings = get_settings()

celery_app = Celery("retail_delivery_worker", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.timezone = "Africa/Algiers"
celery_app.conf.beat_schedule = {
    "nightly-default-wilaya-refresh": {
        "task": "app.worker.nightly_refresh_task",
        "schedule": crontab(hour=2, minute=15),
        "args": (settings.default_wilaya,),
    }
}


def with_db_pool(func, *args, **kwargs):
    open_pool()
    return func(*args, **kwargs)


@celery_app.task(name="app.worker.ingest_google_places_task")
def ingest_google_places_task(wilaya: str, queries: list[str] | None = None, included_types: list[str] | None = None, max_pages_per_query: int = 1):
    return with_db_pool(discover_google_places, wilaya, queries, included_types, max_pages_per_query)


@celery_app.task(name="app.worker.run_verification_task")
def run_verification_task(wilaya: str | None = None):
    return with_db_pool(run_verification, wilaya, None)


@celery_app.task(name="app.worker.recalculate_clusters_task")
def recalculate_clusters_task(wilaya: str, eps_m: int = 750, min_samples: int = 3):
    return with_db_pool(recalculate_clusters, wilaya, eps_m, min_samples)


@celery_app.task(name="app.worker.recalculate_distances_task")
def recalculate_distances_task(wilaya: str, use_google_routes: bool = False):
    return with_db_pool(recalculate_distances, wilaya, use_google_routes)


@celery_app.task(name="app.worker.nightly_refresh_task")
def nightly_refresh_task(wilaya: str):
    def run_all():
        ingestion = discover_google_places(
            wilaya=wilaya,
            queries=[
                f"clothing store in {wilaya} Algeria",
                f"women clothing store in {wilaya} Algeria",
                f"kids clothing store in {wilaya} Algeria",
                f"delivery company in {wilaya} Algeria",
                f"courier service in {wilaya} Algeria",
                f"shipping service in {wilaya} Algeria",
            ],
            included_types=[],
            max_pages_per_query=3,
        )
        verification = run_verification(wilaya=wilaya)
        clusters = recalculate_clusters(wilaya=wilaya, eps_m=750, min_samples=3)
        distances = recalculate_distances(wilaya=wilaya, use_google_routes=bool(settings.routes_key))
        return {
            "ingestion": ingestion,
            "verification": verification,
            "clusters": clusters,
            "distances": distances,
        }

    return with_db_pool(run_all)
