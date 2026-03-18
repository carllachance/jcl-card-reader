from app.core.db import SessionLocal, Base, engine
from app.models.catalog import CatalogCard

SAMPLE = [
    {"year": 1989, "set_name": "Upper Deck", "card_number": "1", "player_name": "Ken Griffey Jr.", "team": "Seattle Mariners", "image_embedding": [0.8, 0.3, 0.2]},
    {"year": 1993, "set_name": "SP Foil", "card_number": "279", "player_name": "Derek Jeter", "team": "New York Yankees", "image_embedding": [0.2, 0.8, 0.4]},
    {"year": 2011, "set_name": "Topps Update", "card_number": "US175", "player_name": "Mike Trout", "team": "Los Angeles Angels", "image_embedding": [0.4, 0.2, 0.9]},
    {"year": 2018, "set_name": "Topps Chrome", "card_number": "150", "player_name": "Shohei Ohtani", "team": "Los Angeles Angels", "image_embedding": [0.6, 0.7, 0.3]},
    {"year": 2020, "set_name": "Bowman", "card_number": "BP-50", "player_name": "Julio Rodriguez", "team": "Seattle Mariners", "image_embedding": [0.5, 0.5, 0.5]},
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(CatalogCard).count() == 0:
        for row in SAMPLE:
            db.add(CatalogCard(**row))
        db.commit()
    db.close()


if __name__ == "__main__":
    run()
