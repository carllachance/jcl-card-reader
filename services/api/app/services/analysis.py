from dataclasses import dataclass
from pathlib import Path


@dataclass
class OCRResult:
    raw_text: str
    clues: dict


class OCRProvider:
    def extract(self, image_path: str, side: str) -> OCRResult:
        raise NotImplementedError


class EmbeddingProvider:
    def embed(self, image_path: str) -> list[float]:
        raise NotImplementedError


class MockOCRProvider(OCRProvider):
    def extract(self, image_path: str, side: str) -> OCRResult:
        name = Path(image_path).name.lower()
        if "griffey" in name:
            clues = {
                "player_name": "Ken Griffey Jr.",
                "year": 1989,
                "set_name": "Upper Deck",
                "card_number": "1",
                "team": "Seattle Mariners",
                "parallel": None,
                "serial_number": None,
                "has_autograph": False,
                "has_relic": False,
            }
        elif "jeter" in name:
            clues = {
                "player_name": "Derek Jeter",
                "year": 1993,
                "set_name": "SP Foil",
                "card_number": "279",
                "team": "New York Yankees",
                "parallel": None,
                "serial_number": None,
                "has_autograph": False,
                "has_relic": False,
            }
        else:
            clues = {
                "player_name": "Unknown",
                "year": None,
                "set_name": "Unknown",
                "card_number": None,
                "team": None,
                "parallel": None,
                "serial_number": None,
                "has_autograph": False,
                "has_relic": False,
            }
        return OCRResult(raw_text=f"mocked {side} ocr from {name}", clues=clues)


class MockEmbeddingProvider(EmbeddingProvider):
    def embed(self, image_path: str) -> list[float]:
        stem = sum(ord(c) for c in Path(image_path).name)
        return [((stem % 97) / 100.0), ((stem % 53) / 100.0), ((stem % 31) / 100.0)]


class AnalysisPipeline:
    """Placeholder pipeline interface for future CV providers (detection/rectification/OCR/embedding)."""

    def __init__(self, ocr: OCRProvider, embedding: EmbeddingProvider):
        self.ocr = ocr
        self.embedding = embedding

    def run(self, front_path: str, back_path: str) -> dict:
        front = self.ocr.extract(front_path, "front")
        back = self.ocr.extract(back_path, "back")
        clues = {**front.clues}
        embedding = self.embedding.embed(front_path)
        return {
            "raw_ocr_front": front.raw_text,
            "raw_ocr_back": back.raw_text,
            "clues": clues,
            "embedding": embedding,
        }
