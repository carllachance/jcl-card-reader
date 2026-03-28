from tempfile import NamedTemporaryFile

from flask import Blueprint, jsonify, request

from app.adapters.object_storage import ObjectStorage
from app.core.db import get_db_session
from app.models.catalog import CatalogCard
from app.models.inventory import InventoryCard
from app.services.analysis import AnalysisPipeline, ImageEmbeddingProvider, OCRSpaceProvider
from app.services.catalog_search import CatalogSearchService
from app.services.valuation import MockValuationProvider

cards_blueprint = Blueprint("cards", __name__, url_prefix="/api/cards")


def _json_error(message: str, status_code: int):
    return jsonify({"detail": message}), status_code


def serialize_candidate_match(candidate: dict) -> dict:
    return {
        "catalog_id": candidate.get("catalog_id"),
        "confidence": candidate.get("confidence"),
        "explanation": candidate.get("explanation"),
    }


def serialize_card_detail(card: InventoryCard) -> dict:
    return {
        "id": card.id,
        "created_at": card.created_at.isoformat() if card.created_at else None,
        "status": card.status,
        "front_image_url": card.front_image_url,
        "back_image_url": card.back_image_url,
        "raw_ocr_front": card.raw_ocr_front,
        "raw_ocr_back": card.raw_ocr_back,
        "extracted_clues": card.extracted_clues,
        "candidate_matches": card.candidate_matches,
        "confirmed_catalog_id": card.confirmed_catalog_id,
        "valuation_snapshot": card.valuation_snapshot,
        "notes": card.notes,
    }


def serialize_upload_response(card_id: int, status: str, extracted_clues: dict, candidates: list[dict]) -> dict:
    return {
        "card_id": card_id,
        "status": status,
        "extracted_clues": extracted_clues,
        "candidates": [serialize_candidate_match(c) for c in candidates],
    }


@cards_blueprint.post("/upload")
def upload_and_analyze():
    front_image = request.files.get("front_image")
    back_image = request.files.get("back_image")
    notes = request.form.get("notes", "")

    if front_image is None or back_image is None:
        return _json_error("front_image and back_image are required", 400)

    db = get_db_session()
    storage = ObjectStorage()
    with NamedTemporaryFile(delete=True, suffix=".jpg") as ftmp, NamedTemporaryFile(delete=True, suffix=".jpg") as btmp:
        ftmp.write(front_image.read())
        ftmp.flush()
        btmp.write(back_image.read())
        btmp.flush()

        front_url = storage.store(ftmp.name, "front")
        back_url = storage.store(btmp.name, "back")

    pipeline = AnalysisPipeline(OCRSpaceProvider(), ImageEmbeddingProvider())
    try:
        result = pipeline.run(front_url, back_url)
    except Exception as exc:
        return _json_error(f"Unable to analyze images: {exc}", 400)

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

    return jsonify(serialize_upload_response(inv.id, status, result["clues"], candidates))


@cards_blueprint.post("/<int:card_id>/confirm")
def confirm_match(card_id: int):
    db = get_db_session()
    card = db.query(InventoryCard).filter(InventoryCard.id == card_id).first()
    if not card:
        return _json_error("Card not found", 404)

    payload = request.get_json(silent=True)
    if payload is None:
        payload = {}
    elif not isinstance(payload, dict):
        return _json_error("JSON body must be an object", 400)
    none_of_these = payload.get("none_of_these", False)
    if not isinstance(none_of_these, bool):
        none_of_these = str(none_of_these).strip().lower() in {"1", "true", "yes", "y"}

    catalog_id = payload.get("catalog_id")
    if catalog_id is not None:
        try:
            catalog_id = int(catalog_id)
        except (TypeError, ValueError):
            return _json_error("catalog_id must be an integer or null", 400)

    if none_of_these:
        card.status = "needs_review"
        card.confirmed_catalog_id = None
        card.valuation_snapshot = None
    else:
        if catalog_id is None:
            return _json_error("catalog_id required unless none_of_these", 400)
        card.confirmed_catalog_id = catalog_id
        card.status = "confirmed"
        card.valuation_snapshot = MockValuationProvider().get_value_range(catalog_id)

    db.commit()
    db.refresh(card)
    return jsonify(serialize_card_detail(card))


@cards_blueprint.get("")
def list_inventory():
    db = get_db_session()
    query = request.args.get("query")
    status = request.args.get("status")

    q = db.query(InventoryCard)
    if status:
        q = q.filter(InventoryCard.status == status)
    rows = q.order_by(InventoryCard.created_at.desc()).all()
    if query:
        query_lower = query.lower()
        rows = [
            r
            for r in rows
            if query_lower in (r.notes or "").lower() or query_lower in str(r.extracted_clues).lower()
        ]

    return jsonify([serialize_card_detail(r) for r in rows])


@cards_blueprint.get("/<int:card_id>")
def get_card(card_id: int):
    db = get_db_session()
    card = db.query(InventoryCard).filter(InventoryCard.id == card_id).first()
    if not card:
        return _json_error("Card not found", 404)
    return jsonify(serialize_card_detail(card))
