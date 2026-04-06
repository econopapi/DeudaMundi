from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import require_admin_api_key
from app.etl.run_world_bank import run_world_bank_etl

router = APIRouter(prefix="/admin")


@router.post("/etl/world-bank/run")
def run_world_bank_etl_endpoint(_: None = Depends(require_admin_api_key)) -> dict[str, int]:
    try:
        return run_world_bank_etl()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"World Bank ETL failed: {exc}",
        ) from exc
