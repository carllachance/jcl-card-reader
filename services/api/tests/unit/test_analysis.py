from app.services.analysis import AnalysisPipeline, OCRSpaceProvider, ImageEmbeddingProvider


class _DummyResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "IsErroredOnProcessing": False,
            "ParsedResults": [{"ParsedText": "Ken Griffey Jr. Upper Deck #1 1989"}],
        }


def test_analysis_pipeline_extracts_real_ocr_text(tmp_path, monkeypatch):
    front = tmp_path / "front.jpg"
    back = tmp_path / "back.jpg"
    front.write_bytes(b"front-image-bytes")
    back.write_bytes(b"back-image-bytes")

    monkeypatch.setattr("app.services.analysis.httpx.post", lambda *args, **kwargs: _DummyResponse())

    result = AnalysisPipeline(OCRSpaceProvider(api_key="test"), ImageEmbeddingProvider()).run(str(front), str(back))

    assert "front" in result["raw_ocr_front"]
    assert "back" in result["raw_ocr_back"]
    assert result["clues"]["player_name"] == "Ken Griffey Jr."
    assert isinstance(result["embedding"], list)
    assert len(result["embedding"]) == 3
