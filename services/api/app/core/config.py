from pydantic import BaseModel
import os


class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./card_reader.db")
    storage_dir: str = os.getenv("STORAGE_DIR", "./storage")


settings = Settings()
