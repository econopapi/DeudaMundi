from __future__ import annotations

import os
from random import choice

from locust import HttpUser, between, task

COUNTRY_ISO3_SAMPLES = ["ARG", "USA", "BRA", "DEU", "GRC"]


class DeudaMundiApiUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = os.getenv("LOCUST_HOST", "http://127.0.0.1:8000")

    @task(3)
    def health(self) -> None:
        self.client.get("/api/v1/health", name="GET /health")

    @task(3)
    def countries(self) -> None:
        self.client.get("/api/v1/countries?page=1&page_size=20", name="GET /countries")

    @task(2)
    def rankings(self) -> None:
        self.client.get(
            "/api/v1/rankings?metric=absolute&limit=20",
            name="GET /rankings",
        )

    @task(2)
    def globe_data(self) -> None:
        self.client.get("/api/v1/globe-data", name="GET /globe-data")

    @task(1)
    def history(self) -> None:
        iso3 = choice(COUNTRY_ISO3_SAMPLES)
        self.client.get(f"/api/v1/countries/{iso3}/history", name="GET /countries/{iso3}/history")

    @task(1)
    def governments(self) -> None:
        iso3 = choice(COUNTRY_ISO3_SAMPLES)
        self.client.get(
            f"/api/v1/countries/{iso3}/governments",
            name="GET /countries/{iso3}/governments",
        )
