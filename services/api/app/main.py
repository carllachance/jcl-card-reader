from fastapi import FastAPI
from app.api.cards import router as cards_router
from app.core.db import Base, engine
import app.models.catalog  # noqa
import app.models.inventory  # noqa

app = FastAPI(title="Card Reader API", version="0.1.0")
Base.metadata.create_all(bind=engine)
app.include_router(cards_router)


@app.get('/health')
def health():
    return {"ok": True}
