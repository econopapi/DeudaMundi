from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.cache import CACHE_TTL_GLOBE_DATA_SECONDS, get_cache_json, set_cache_json
from app.db.session import get_db
from app.schemas.country import GlobeDataResponse
from app.services.countries import get_globe_data

router = APIRouter()


@router.get("/globe-data", response_model=GlobeDataResponse)
def get_globe_data_endpoint(
    region: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> GlobeDataResponse:
    cache_key = f"globe-data:{region or 'all'}"
    cached = get_cache_json(cache_key)
    if cached:
        return GlobeDataResponse.model_validate(cached)

    result = GlobeDataResponse.model_validate(get_globe_data(db=db, region=region))
    set_cache_json(
        key=cache_key,
        value=result.model_dump(),
        ttl_seconds=CACHE_TTL_GLOBE_DATA_SECONDS,
    )
    return result
