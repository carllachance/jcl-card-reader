from io import BytesIO

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models.catalog import CatalogCard
from app.models.inventory import InventoryCard
from app.services.analysis import OCRResult


client = app.test_client()


def setup_module():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(CatalogCard).count() == 0:
        db.add(
            CatalogCard(
                year=1989,
                set_name="Upper Deck",
                card_number="1",
                player_name="Ken Griffey Jr.",
                team="Seattle Mariners",
                image_embedding=[0.8, 0.3, 0.2],
            )
        )
        db.commit()
    db.close()


def _fake_extract(_self, _image_path: str, side: str):
    return OCRResult(
        raw_text=f"[{side}] Ken Griffey Jr. Upper Deck #1 1989",
        clues={
            "player_name": "Ken Griffey Jr.",
            "year": 1989,
            "set_name": "Upper Deck",
            "card_number": "1",
            "team": "Seattle Mariners",
            "parallel": None,
            "serial_number": None,
            "has_autograph": False,
            "has_relic": False,
        },
    )


def _upload_card(notes: str = "shoebox find") -> dict:
    data = {
        "front_image": (BytesIO(b"front"), "griffey-front.jpg"),
        "back_image": (BytesIO(b"back"), "griffey-back.jpg"),
        "notes": notes,
    }
    upload = client.post("/api/cards/upload", data=data, content_type="multipart/form-data")
    assert upload.status_code == 200
    return upload.get_json()


def test_upload_validation_failure_when_files_missing():
    upload = client.post("/api/cards/upload", data={"notes": "missing files"})
    assert upload.status_code == 400
    assert upload.get_json()["detail"] == "front_image and back_image are required"


def test_upload_analyze_confirm_inventory_flow(monkeypatch):
    monkeypatch.setattr("app.services.analysis.OCRSpaceProvider.extract", _fake_extract)

    body = _upload_card()
    card_id = body["card_id"]
    assert body["status"] == "needs_review"
    assert len(body["candidates"]) >= 1

    confirm = client.post(
        f"/api/cards/{card_id}/confirm",
        json={"catalog_id": body["candidates"][0]["catalog_id"], "none_of_these": False},
    )
    assert confirm.status_code == 200
    assert confirm.get_json()["status"] == "confirmed"
    assert confirm.get_json()["valuation_snapshot"]["low"] > 0

    inv = client.get("/api/cards")
    assert inv.status_code == 200
    assert any(c["id"] == card_id for c in inv.get_json())


def test_confirm_with_none_of_these_true(monkeypatch):
    monkeypatch.setattr("app.services.analysis.OCRSpaceProvider.extract", _fake_extract)
    body = _upload_card(notes="none-of-these")
    card_id = body["card_id"]

    confirm = client.post(
        f"/api/cards/{card_id}/confirm",
        json={"catalog_id": body["candidates"][0]["catalog_id"], "none_of_these": True},
    )
    assert confirm.status_code == 200
    payload = confirm.get_json()
    assert payload["status"] == "needs_review"
    assert payload["confirmed_catalog_id"] is None
    assert payload["valuation_snapshot"] is None


def test_confirm_without_catalog_id_returns_400(monkeypatch):
    monkeypatch.setattr("app.services.analysis.OCRSpaceProvider.extract", _fake_extract)
    body = _upload_card(notes="missing-catalog-id")
    card_id = body["card_id"]

    confirm = client.post(f"/api/cards/{card_id}/confirm", json={"none_of_these": False})
    assert confirm.status_code == 400
    assert confirm.get_json()["detail"] == "catalog_id required unless none_of_these"


def test_confirm_with_non_object_json_returns_400(monkeypatch):
    monkeypatch.setattr("app.services.analysis.OCRSpaceProvider.extract", _fake_extract)
    body = _upload_card(notes="non-object-json")
    card_id = body["card_id"]

    confirm = client.post(f"/api/cards/{card_id}/confirm", json=["not", "an", "object"])
    assert confirm.status_code == 400
    assert confirm.get_json()["detail"] == "JSON body must be an object"


def test_get_missing_card_returns_404():
    response = client.get("/api/cards/999999999")
    assert response.status_code == 404
    assert response.get_json()["detail"] == "Card not found"


def test_list_query_and_status_filtering_basics(monkeypatch):
    monkeypatch.setattr("app.services.analysis.OCRSpaceProvider.extract", _fake_extract)

    uploaded = _upload_card(notes="query-filter-target")
    card_id = uploaded["card_id"]

    with SessionLocal() as db:
        card = db.query(InventoryCard).filter(InventoryCard.id == card_id).first()
        assert card is not None
        card.status = "confirmed"
        db.commit()

    filtered = client.get("/api/cards", query_string={"query": "query-filter-target", "status": "confirmed"})
    assert filtered.status_code == 200
    rows = filtered.get_json()
    assert any(row["id"] == card_id for row in rows)

    wrong_status = client.get("/api/cards", query_string={"query": "query-filter-target", "status": "needs_review"})
    assert wrong_status.status_code == 200
    assert all(row["id"] != card_id for row in wrong_status.get_json())
