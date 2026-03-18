from sqlalchemy import String, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class CatalogCard(Base):
    __tablename__ = "catalog_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[str] = mapped_column(String(32), default="baseball")
    year: Mapped[int] = mapped_column(Integer)
    set_name: Mapped[str] = mapped_column(String(120))
    card_number: Mapped[str] = mapped_column(String(40))
    player_name: Mapped[str] = mapped_column(String(120))
    team: Mapped[str | None] = mapped_column(String(80), nullable=True)
    parallel: Mapped[str | None] = mapped_column(String(80), nullable=True)
    has_autograph: Mapped[bool] = mapped_column(default=False)
    has_relic: Mapped[bool] = mapped_column(default=False)
    serial_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    image_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
