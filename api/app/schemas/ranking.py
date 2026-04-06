from pydantic import BaseModel


class RankingItem(BaseModel):
    rank: int
    iso3: str
    name_en: str
    region: str | None
    value: float
    latest_year: int


class RankingsResponse(BaseModel):
    metric: str
    region: str | None
    limit: int
    items: list[RankingItem]
