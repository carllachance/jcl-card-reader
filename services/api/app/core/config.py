import os


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./card_reader.db")
        self.storage_dir: str = os.getenv("STORAGE_DIR", "./storage")


settings = Settings()
