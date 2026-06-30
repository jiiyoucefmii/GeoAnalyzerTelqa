from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="postgresql://app:change_me@localhost:5432/retail_map")
    redis_url: str = Field(default="redis://localhost:6379/0")
    google_maps_api_key: str = Field(default="")
    google_places_api_key: str = Field(default="")
    google_routes_api_key: str = Field(default="")
    google_geocoding_api_key: str = Field(default="")
    google_places_language: str = Field(default="fr")
    default_wilaya: str = Field(default="Oran")
    api_cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def places_key(self) -> str:
        return self.google_places_api_key or self.google_maps_api_key

    @property
    def routes_key(self) -> str:
        return self.google_routes_api_key or self.google_maps_api_key

    @property
    def geocoding_key(self) -> str:
        return self.google_geocoding_api_key or self.google_maps_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
