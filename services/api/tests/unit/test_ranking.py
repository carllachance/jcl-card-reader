from app.services.catalog_search import CatalogSearchService
from app.models.catalog import CatalogCard


def test_ranking_prioritizes_exact_clues():
    cards = [
        CatalogCard(id=1, year=1989, set_name="Upper Deck", card_number="1", player_name="Ken Griffey Jr.", team="Seattle Mariners", image_embedding=[0.9,0.1,0.2]),
        CatalogCard(id=2, year=1993, set_name="SP Foil", card_number="279", player_name="Derek Jeter", team="NY", image_embedding=[0.1,0.2,0.9]),
    ]
    clues = {"player_name": "Ken Griffey Jr.", "year": 1989, "set_name": "Upper Deck", "card_number": "1"}
    ranked = CatalogSearchService().rank(cards, clues, [0.9,0.1,0.2])
    assert ranked[0]["catalog_id"] == 1
    assert ranked[0]["confidence"] > ranked[1]["confidence"]
