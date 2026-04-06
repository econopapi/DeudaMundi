from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Government(Base):
    __tablename__ = "governments"
    __table_args__ = (
        UniqueConstraint(
            "country_id",
            "leader_name",
            "start_date",
            name="uq_government_country_leader_start",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        index=True,
    )

    leader_name: Mapped[str] = mapped_column(String(150))
    party: Mapped[str | None] = mapped_column(String(150), nullable=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    political_lean: Mapped[str | None] = mapped_column(String(50), nullable=True)
