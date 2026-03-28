from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
import re

import httpx


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


class OCRSpaceProvider(OCRProvider):
    """OCR provider backed by the OCR.space API (real OCR, no mocked results)."""

    API_URL = "https://api.ocr.space/parse/image"

    _YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")
    _CARD_NUMBER_PATTERN = re.compile(r"(?:#|No\.?|Number|Card)\s*([A-Z0-9-]{1,8})\b", re.IGNORECASE)
    _SERIAL_PATTERN = re.compile(r"\b(\d{1,4})\s*/\s*(\d{2,5})\b")

    KNOWN_PLAYERS = (
        "Ken Griffey Jr.",
        "Derek Jeter",
        "Mike Trout",
        "Shohei Ohtani",
        "Mookie Betts",
        "Aaron Judge",
        "Cal Ripken Jr.",
        "Nolan Ryan",
        "Ichiro Suzuki",
    )

    KNOWN_SETS = (
        "Upper Deck",
        "Topps",
        "Bowman",
        "Donruss",
        "Fleer",
        "SP Foil",
        "Stadium Club",
        "Chrome",
        "Finest",
    )

    KNOWN_TEAMS = (
        "Seattle Mariners",
        "New York Yankees",
        "Los Angeles Angels",
        "Los Angeles Dodgers",
        "Boston Red Sox",
        "New York Mets",
        "Chicago Cubs",
    )

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 20.0):
        self.api_key = api_key or os.getenv("OCR_SPACE_API_KEY", "helloworld")
        self.timeout_seconds = timeout_seconds

    def extract(self, image_path: str, side: str) -> OCRResult:
        with open(image_path, "rb") as image_file:
            response = httpx.post(
                self.API_URL,
                data={
                    "apikey": self.api_key,
                    "language": "eng",
                    "isOverlayRequired": False,
                    "isTable": False,
                    "OCREngine": 2,
                },
                files={"file": (image_path, image_file, "application/octet-stream")},
                timeout=self.timeout_seconds,
            )

        response.raise_for_status()
        payload = response.json()
        if payload.get("IsErroredOnProcessing"):
            errors = "; ".join(payload.get("ErrorMessage") or ["unknown OCR error"])
            raise RuntimeError(errors)

        parsed_results = payload.get("ParsedResults") or []
        raw_text = "\n".join(r.get("ParsedText", "") for r in parsed_results).strip()
        clues = self._parse_clues(raw_text)
        return OCRResult(raw_text=f"[{side}] {raw_text}".strip(), clues=clues)

    def _parse_clues(self, raw_text: str) -> dict:
        upper = raw_text.upper()

        year_match = self._YEAR_PATTERN.search(raw_text)
        card_match = self._CARD_NUMBER_PATTERN.search(raw_text)
        serial_match = self._SERIAL_PATTERN.search(raw_text)

        player_name = self._find_known_entity(raw_text, self.KNOWN_PLAYERS)
        set_name = self._find_known_entity(raw_text, self.KNOWN_SETS)
        team = self._find_known_entity(raw_text, self.KNOWN_TEAMS)

        has_autograph = "AUTO" in upper or "AUTOGRAPH" in upper
        has_relic = any(token in upper for token in ("RELIC", "JERSEY", "PATCH", "MEMORABILIA"))

        return {
            "player_name": player_name,
            "year": int(year_match.group(1)) if year_match else None,
            "set_name": set_name,
            "card_number": card_match.group(1) if card_match else None,
            "team": team,
            "parallel": None,
            "serial_number": f"{serial_match.group(1)}/{serial_match.group(2)}" if serial_match else None,
            "has_autograph": has_autograph,
            "has_relic": has_relic,
        }

    @staticmethod
    def _find_known_entity(raw_text: str, candidates: tuple[str, ...]) -> str | None:
        lowered = raw_text.lower()
        for candidate in candidates:
            if candidate.lower() in lowered:
                return candidate
        return None


class ImageEmbeddingProvider(EmbeddingProvider):
    """Image embedding derived from image file bytes (content-based, deterministic)."""

    def embed(self, image_path: str) -> list[float]:
        with open(image_path, "rb") as image_file:
            digest = hashlib.sha256(image_file.read()).digest()
        return [round(int.from_bytes(digest[i : i + 8], "big") / (2**64 - 1), 6) for i in (0, 8, 16)]


class AnalysisPipeline:
    """Pipeline that performs OCR and computes an image embedding from uploaded card images."""

    def __init__(self, ocr: OCRProvider, embedding: EmbeddingProvider):
        self.ocr = ocr
        self.embedding = embedding

    def run(self, front_path: str, back_path: str) -> dict:
        front = self.ocr.extract(front_path, "front")
        back = self.ocr.extract(back_path, "back")

        clues = {**front.clues}
        for key, value in back.clues.items():
            if clues.get(key) is None and value is not None:
                clues[key] = value

        embedding = self.embedding.embed(front_path)
        return {
            "raw_ocr_front": front.raw_text,
            "raw_ocr_back": back.raw_text,
            "clues": clues,
            "embedding": embedding,
        }
