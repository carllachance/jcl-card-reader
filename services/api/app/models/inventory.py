from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class InventoryCard(Base):
    __tablename__ = "inventory_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(32), default="needs_review")
    front_image_url: Mapped[str] = mapped_column(String(255))
    back_image_url: Mapped[str] = mapped_column(String(255))
    raw_ocr_front: Mapped[str] = mapped_column(Text, default="")
    raw_ocr_back: Mapped[str] = mapped_column(Text, default="")
    extracted_clues: Mapped[dict] = mapped_column(JSON, default={})
    candidate_matches: Mapped[list] = mapped_column(JSON, default=[])
    confirmed_catalog_id: Mapped[int | None] = mapped_column(ForeignKey("catalog_cards.id"), nullable=True)
    valuation_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
