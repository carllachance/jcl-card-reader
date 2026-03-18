from datetime import datetime
from pydantic import BaseModel


class CandidateMatch(BaseModel):
    catalog_id: int
    confidence: float
    explanation: str


class UploadAnalyzeResponse(BaseModel):
    card_id: int
    status: str
    extracted_clues: dict
    candidates: list[CandidateMatch]


class ConfirmRequest(BaseModel):
    catalog_id: int | None = None
    none_of_these: bool = False


class CardDetail(BaseModel):
    id: int
    created_at: datetime
    status: str
    front_image_url: str
    back_image_url: str
    raw_ocr_front: str
    raw_ocr_back: str
    extracted_clues: dict
    candidate_matches: list[dict]
    confirmed_catalog_id: int | None
    valuation_snapshot: dict | None
    notes: str

    class Config:
        from_attributes = True
