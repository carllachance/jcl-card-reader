# Architecture

## Service-oriented pipeline
- **Storage adapter**: `ObjectStorage` abstracts Supabase-compatible blob storage.
- **Analysis pipeline**: `AnalysisPipeline` composes OCR + embedding providers.
- **Catalog search**: deterministic weighted score of clue matches + image similarity.
- **Valuation provider**: interface + mock implementation for comps.

## Extension points
- Replace `MockOCRProvider` with provider calling real OCR/vision APIs.
- Replace `MockEmbeddingProvider` with CLIP-like embedding service.
- Add pgvector ANN query in `CatalogSearchService` before scoring.
- Swap `MockValuationProvider` with real sales/comps integrations.

## Data model notes
- `catalog_cards` is sport-agnostic and stores structured metadata + embedding.
- `inventory_cards` stores raw OCR, normalized clues, candidates, and review status.
- `needs_review` status ensures human-in-the-loop workflows.
