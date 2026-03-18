from datetime import datetime


class ValuationProvider:
    def get_value_range(self, catalog_id: int) -> dict:
        raise NotImplementedError


class MockValuationProvider(ValuationProvider):
    def get_value_range(self, catalog_id: int) -> dict:
        base = 20 + (catalog_id * 3)
        return {
            "low": round(base * 0.8, 2),
            "high": round(base * 1.2, 2),
            "comp_count": 12 + catalog_id,
            "last_updated": datetime.utcnow().isoformat(),
            "confidence": "medium" if catalog_id % 2 else "high",
            "source": "mock_comps_provider_v1",
        }
