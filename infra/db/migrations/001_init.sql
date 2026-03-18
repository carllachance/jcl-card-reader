CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS catalog_cards (
  id BIGSERIAL PRIMARY KEY,
  sport TEXT NOT NULL DEFAULT 'baseball',
  year INTEGER NOT NULL,
  set_name TEXT NOT NULL,
  card_number TEXT NOT NULL,
  player_name TEXT NOT NULL,
  team TEXT,
  parallel TEXT,
  has_autograph BOOLEAN NOT NULL DEFAULT FALSE,
  has_relic BOOLEAN NOT NULL DEFAULT FALSE,
  serial_number TEXT,
  image_embedding VECTOR(3)
);

CREATE TABLE IF NOT EXISTS inventory_cards (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'needs_review',
  front_image_url TEXT NOT NULL,
  back_image_url TEXT NOT NULL,
  raw_ocr_front TEXT NOT NULL,
  raw_ocr_back TEXT NOT NULL,
  extracted_clues JSONB NOT NULL,
  candidate_matches JSONB NOT NULL,
  confirmed_catalog_id BIGINT REFERENCES catalog_cards(id),
  valuation_snapshot JSONB,
  notes TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory_cards(status);
CREATE INDEX IF NOT EXISTS idx_inventory_clues_gin ON inventory_cards USING gin(extracted_clues);
CREATE INDEX IF NOT EXISTS idx_catalog_embedding ON catalog_cards USING ivfflat (image_embedding vector_cosine_ops);
