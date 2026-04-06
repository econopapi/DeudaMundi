from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.cache import CACHE_TTL_RANKINGS_SECONDS, get_cache_json, set_cache_json
from app.db.session import get_db
from app.schemas.ranking import RankingsResponse
from app.services.rankings import get_rankings

router = APIRouter(prefix="/rankings")


@router.get("", response_model=RankingsResponse)
def get_rankings_endpoint(
    metric: str = Query(default="absolute"),
    region: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> RankingsResponse:
    cache_key = f"rankings:{metric}:{region or 'all'}:{limit}"
    cached = get_cache_json(cache_key)
    if cached:
        return RankingsResponse.model_validate(cached)

    try:
        result = RankingsResponse.model_validate(
            get_rankings(db=db, metric=metric, region=region, limit=limit)
        )
        set_cache_json(
            key=cache_key,
            value=result.model_dump(),
            ttl_seconds=CACHE_TTL_RANKINGS_SECONDS,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
