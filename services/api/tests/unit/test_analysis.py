from app.services.analysis import AnalysisPipeline, MockOCRProvider, MockEmbeddingProvider


def test_analysis_pipeline_extracts_clues_from_filename():
    result = AnalysisPipeline(MockOCRProvider(), MockEmbeddingProvider()).run("/tmp/griffey-front.jpg", "/tmp/griffey-back.jpg")
    assert result["clues"]["player_name"] == "Ken Griffey Jr."
    assert isinstance(result["embedding"], list)
