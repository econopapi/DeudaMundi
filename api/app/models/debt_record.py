from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class DebtRecord(Base):
    __tablename__ = "debt_records"
    __table_args__ = (UniqueConstraint("country_id", "year", name="uq_debt_country_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, index=True)

    total_external_debt_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    debt_pct_gdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    debt_per_capita_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    gdp_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    source: Mapped[str] = mapped_column(String(30), default="worldbank")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    country = relationship("Country", back_populates="debt_records")
