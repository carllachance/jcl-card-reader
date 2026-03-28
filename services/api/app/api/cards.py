from tempfile import NamedTemporaryFile
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.inventory import InventoryCard
from app.models.catalog import CatalogCard
from app.schemas.cards import UploadAnalyzeResponse, ConfirmRequest, CardDetail
from app.services.analysis import AnalysisPipeline, OCRSpaceProvider, ImageEmbeddingProvider
from app.services.catalog_search import CatalogSearchService
from app.services.valuation import MockValuationProvider
from app.adapters.object_storage import ObjectStorage

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.post("/upload", response_model=UploadAnalyzeResponse)
def upload_and_analyze(
    front_image: UploadFile = File(...),
    back_image: UploadFile = File(...),
    notes: str = Form(default=""),
    db: Session = Depends(get_db),
):
    storage = ObjectStorage()
    with NamedTemporaryFile(delete=True, suffix=".jpg") as ftmp, NamedTemporaryFile(delete=True, suffix=".jpg") as btmp:
        ftmp.write(front_image.file.read())
        ftmp.flush()
        btmp.write(back_image.file.read())
        btmp.flush()

        front_url = storage.store(ftmp.name, "front")
        back_url = storage.store(btmp.name, "back")

    pipeline = AnalysisPipeline(OCRSpaceProvider(), ImageEmbeddingProvider())
    try:
        result = pipeline.run(front_url, back_url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to analyze images: {exc}") from exc

    search = CatalogSearchService()
    catalog_cards = db.query(CatalogCard).all()
    candidates = search.rank(catalog_cards, result["clues"], result["embedding"])

    status = "needs_review"
    inv = InventoryCard(
        status=status,
        front_image_url=front_url,
        back_image_url=back_url,
        raw_ocr_front=result["raw_ocr_front"],
        raw_ocr_back=result["raw_ocr_back"],
        extracted_clues=result["clues"],
        candidate_matches=candidates,
        notes=notes,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    return UploadAnalyzeResponse(card_id=inv.id, status=status, extracted_clues=result["clues"], candidates=candidates)


@router.post("/{card_id}/confirm", response_model=CardDetail)
def confirm_match(card_id: int, payload: ConfirmRequest, db: Session = Depends(get_db)):
    card = db.query(InventoryCard).filter(InventoryCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if payload.none_of_these:
        card.status = "needs_review"
        card.confirmed_catalog_id = None
        card.valuation_snapshot = None
    else:
        if payload.catalog_id is None:
            raise HTTPException(status_code=400, detail="catalog_id required unless none_of_these")
        card.confirmed_catalog_id = payload.catalog_id
        card.status = "confirmed"
        card.valuation_snapshot = MockValuationProvider().get_value_range(payload.catalog_id)

    db.commit()
    db.refresh(card)
    return card


@router.get("", response_model=list[CardDetail])
def list_inventory(
    query: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(InventoryCard)
    if status:
        q = q.filter(InventoryCard.status == status)
    rows = q.order_by(InventoryCard.created_at.desc()).all()
    if query:
        rows = [r for r in rows if query.lower() in (r.notes or "").lower() or query.lower() in str(r.extracted_clues).lower()]
    return rows


@router.get("/{card_id}", response_model=CardDetail)
def get_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(InventoryCard).filter(InventoryCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card
