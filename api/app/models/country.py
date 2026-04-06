from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    iso2: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    iso3: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    name_es: Mapped[str] = mapped_column(String(150))
    name_en: Mapped[str] = mapped_column(String(150))
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subregion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capital: Mapped[str | None] = mapped_column(String(120), nullable=True)
    flag_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    debt_records = relationship(
        "DebtRecord",
        back_populates="country",
        cascade="all, delete-orphan",
    )
