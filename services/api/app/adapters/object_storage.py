from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import uuid

from app.core.config import settings


class ObjectStorage:
    """Local filesystem storage adapter used by the upload flow."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def store(self, source_path: str, side: str) -> str:
        ext = Path(source_path).suffix or ".jpg"
        date_prefix = datetime.utcnow().strftime("%Y%m%d")
        filename = f"{date_prefix}-{side}-{uuid.uuid4().hex}{ext}"
        destination = self.base_dir / filename
        shutil.copy2(source_path, destination)
        return str(destination)
