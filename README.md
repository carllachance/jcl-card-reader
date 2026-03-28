# Baseball Card Inventory + Valuation MVP

Monorepo with:
- `apps/web`: Next.js + TypeScript + Tailwind UI for upload/review/inventory.
- `services/api`: FastAPI service with analysis pipeline, catalog ranking, inventory, and mock valuation.
- `infra/db`: Postgres/pgvector schema migrations + seed SQL.
- `packages/contracts`: shared API contract placeholder.

## Quick start

```bash
docker compose up --build
```

Web: `http://localhost:3000`
API docs: `http://localhost:8000/docs`

## Local API only

```bash
cd services/api
pip install -r requirements.txt
python -m app.repositories.seed_catalog
uvicorn app.main:app --reload
```

## Test

```bash
cd services/api
pytest
```

## Flow supported
1. Upload front/back photos
2. Store originals in object storage adapter (`storage/` local for MVP)
3. Analyze via real OCR (OCR.space API) + image-derived embeddings through `AnalysisPipeline`
4. Rank top 5 local catalog candidates with explanations
5. Confirm match or none-of-these
6. Persist inventory entry + valuation snapshot
7. Browse/search inventory and card detail


Set `OCR_SPACE_API_KEY` to your OCR.space key for production-quality OCR (the API default `helloworld` key is used when not set).
