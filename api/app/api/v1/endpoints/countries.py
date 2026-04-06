from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.cache import (
    CACHE_TTL_COUNTRIES_SECONDS,
    get_cache_json,
    set_cache_json,
)
from app.db.session import get_db
from app.schemas.country import (
    CountriesListResponse,
    CountryDetailResponse,
    CountryGovernmentsResponse,
    CountryHistoryResponse,
)
from app.services.countries import (
    get_country_detail,
    get_country_governments,
    get_country_history,
    list_countries,
)

router = APIRouter(prefix="/countries")


@router.get("", response_model=CountriesListResponse)
def list_countries_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    region: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> CountriesListResponse:
    cache_key = f"countries:list:{page}:{page_size}:{region or 'all'}"
    cached = get_cache_json(cache_key)
    if cached:
        return CountriesListResponse.model_validate(cached)

    result = CountriesListResponse.model_validate(
        list_countries(db=db, page=page, page_size=page_size, region=region)
    )
    set_cache_json(
        key=cache_key,
        value=result.model_dump(),
        ttl_seconds=CACHE_TTL_COUNTRIES_SECONDS,
    )
    return result


@router.get("/{iso3}", response_model=CountryDetailResponse)
def get_country_detail_endpoint(
    iso3: str,
    db: Session = Depends(get_db),
) -> CountryDetailResponse:
    normalized_iso3 = iso3.upper()
    cache_key = f"countries:detail:{normalized_iso3}"
    cached = get_cache_json(cache_key)
    if cached:
        return CountryDetailResponse.model_validate(cached)

    detail = get_country_detail(db=db, iso3=iso3)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{iso3}' not found",
        )
    result = CountryDetailResponse.model_validate(detail)
    set_cache_json(
        key=cache_key,
        value=result.model_dump(),
        ttl_seconds=CACHE_TTL_COUNTRIES_SECONDS,
    )
    return result


@router.get("/{iso3}/history", response_model=CountryHistoryResponse)
def get_country_history_endpoint(
    iso3: str,
    db: Session = Depends(get_db),
) -> CountryHistoryResponse:
    normalized_iso3 = iso3.upper()
    cache_key = f"countries:history:{normalized_iso3}"
    cached = get_cache_json(cache_key)
    if cached:
        return CountryHistoryResponse.model_validate(cached)

    history = get_country_history(db=db, iso3=iso3)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{iso3}' not found",
        )
    result = CountryHistoryResponse.model_validate(history)
    set_cache_json(
        key=cache_key,
        value=result.model_dump(),
        ttl_seconds=CACHE_TTL_COUNTRIES_SECONDS,
    )
    return result


@router.get("/{iso3}/governments", response_model=CountryGovernmentsResponse)
def get_country_governments_endpoint(
    iso3: str,
    db: Session = Depends(get_db),
) -> CountryGovernmentsResponse:
    normalized_iso3 = iso3.upper()
    cache_key = f"countries:governments:{normalized_iso3}"
    cached = get_cache_json(cache_key)
    if cached:
        return CountryGovernmentsResponse.model_validate(cached)

    governments = get_country_governments(db=db, iso3=iso3)
    if not governments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{iso3}' not found",
        )
    result = CountryGovernmentsResponse.model_validate(governments)
    set_cache_json(
        key=cache_key,
        value=result.model_dump(),
        ttl_seconds=CACHE_TTL_COUNTRIES_SECONDS,
    )
    return result


