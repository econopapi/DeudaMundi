from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

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
    return list_countries(db=db, page=page, page_size=page_size, region=region)


@router.get("/{iso3}", response_model=CountryDetailResponse)
def get_country_detail_endpoint(
    iso3: str,
    db: Session = Depends(get_db),
) -> CountryDetailResponse:
    detail = get_country_detail(db=db, iso3=iso3)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{iso3}' not found",
        )
    return detail


@router.get("/{iso3}/history", response_model=CountryHistoryResponse)
def get_country_history_endpoint(
    iso3: str,
    db: Session = Depends(get_db),
) -> CountryHistoryResponse:
    history = get_country_history(db=db, iso3=iso3)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{iso3}' not found",
        )
    return history


@router.get("/{iso3}/governments", response_model=CountryGovernmentsResponse)
def get_country_governments_endpoint(
    iso3: str,
    db: Session = Depends(get_db),
) -> CountryGovernmentsResponse:
    governments = get_country_governments(db=db, iso3=iso3)
    if not governments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{iso3}' not found",
        )
    return governments
