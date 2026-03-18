from app.models.catalog import CatalogCard


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(y * y for y in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class CatalogSearchService:
    def rank(self, catalog_cards: list[CatalogCard], clues: dict, image_embedding: list[float]) -> list[dict]:
        candidates = []
        for card in catalog_cards:
            score = 0.0
            reasons = []
            if clues.get("player_name") and clues.get("player_name") == card.player_name:
                score += 0.35
                reasons.append("player match")
            if clues.get("year") and clues.get("year") == card.year:
                score += 0.2
                reasons.append("year match")
            if clues.get("set_name") and clues.get("set_name") == card.set_name:
                score += 0.2
                reasons.append("set match")
            if clues.get("card_number") and clues.get("card_number") == card.card_number:
                score += 0.15
                reasons.append("card number match")

            emb = card.image_embedding or [0.0, 0.0, 0.0]
            sim = max(cosine_similarity(image_embedding, emb), 0)
            score += 0.1 * sim
            reasons.append(f"image similarity {sim:.2f}")

            candidates.append(
                {
                    "catalog_id": card.id,
                    "confidence": round(min(score, 1.0), 3),
                    "explanation": ", ".join(reasons),
                }
            )
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        return candidates[:5]
