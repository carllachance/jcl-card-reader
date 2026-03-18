from io import BytesIO
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import Base, engine, SessionLocal
from app.models.catalog import CatalogCard


client = TestClient(app)


def setup_module():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(CatalogCard).count() == 0:
        db.add(CatalogCard(year=1989, set_name="Upper Deck", card_number="1", player_name="Ken Griffey Jr.", team="Seattle Mariners", image_embedding=[0.8,0.3,0.2]))
        db.commit()
    db.close()


def test_upload_analyze_confirm_inventory_flow():
    files = {
        "front_image": ("griffey-front.jpg", BytesIO(b"front"), "image/jpeg"),
        "back_image": ("griffey-back.jpg", BytesIO(b"back"), "image/jpeg"),
    }
    upload = client.post("/api/cards/upload", files=files, data={"notes": "shoebox find"})
    assert upload.status_code == 200
    body = upload.json()
    card_id = body["card_id"]
    assert body["status"] == "needs_review"
    assert len(body["candidates"]) >= 1

    confirm = client.post(f"/api/cards/{card_id}/confirm", json={"catalog_id": body["candidates"][0]["catalog_id"], "none_of_these": False})
    assert confirm.status_code == 200
    assert confirm.json()["status"] == "confirmed"
    assert confirm.json()["valuation_snapshot"]["low"] > 0

    inv = client.get("/api/cards")
    assert inv.status_code == 200
    assert any(c["id"] == card_id for c in inv.json())
