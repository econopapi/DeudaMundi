from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import require_admin_api_key
from app.etl.run_world_bank import run_world_bank_etl
from app.etl.seed_governments import seed_governments

router = APIRouter(prefix="/admin")


def _run_global_etl() -> dict[str, int | str]:
    try:
        return run_world_bank_etl()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Global ETL failed: {exc}",
        ) from exc


@router.post("/etl/run")
def run_global_etl_endpoint(_: None = Depends(require_admin_api_key)) -> dict[str, int | str]:
    return _run_global_etl()


@router.post("/etl/world-bank/run")
def run_world_bank_etl_endpoint(_: None = Depends(require_admin_api_key)) -> dict[str, int | str]:
    return _run_global_etl()


@router.post("/etl/governments/run")
def run_governments_seed_endpoint(
    _: None = Depends(require_admin_api_key),
    source: str | None = Query(default=None, pattern="^(pilot|wikidata|hybrid)$"),
) -> dict[str, int | str]:
    try:
        return seed_governments(source=source)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Governments ETL failed: {exc}",
        ) from exc
