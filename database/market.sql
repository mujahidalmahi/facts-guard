CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- FactGuard · Market Schema · May 2026
-- Price comparison tables for the market section.
-- Run once in SQL Editor. Safe to re-run (IF NOT EXISTS).
-- ============================================================
-- 1. product_queries — one row per price comparison request
CREATE TABLE IF NOT EXISTS product_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_name TEXT NOT NULL,
  search_hash TEXT GENERATED ALWAYS AS
    (encode(sha256(product_name::bytea), 'hex')) STORED,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','processing','done','error')),
  job_id TEXT UNIQUE,
  variants_data JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END; $$;

CREATE TRIGGER product_queries_updated_at BEFORE UPDATE ON product_queries
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 2. product_listings — one row per merchant listing per price query
CREATE TABLE IF NOT EXISTS product_listings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id UUID NOT NULL REFERENCES product_queries(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  price NUMERIC(10,2),
  currency TEXT DEFAULT 'USD',
  merchant TEXT NOT NULL,
  url TEXT NOT NULL,
  image TEXT,
  condition TEXT,
  model_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_product_queries_hash
  ON product_queries(search_hash);
CREATE INDEX IF NOT EXISTS idx_product_queries_status
  ON product_queries(status);
CREATE INDEX IF NOT EXISTS idx_product_listings_query
  ON product_listings(query_id);
CREATE INDEX IF NOT EXISTS idx_product_queries_created
  ON product_queries(created_at DESC);
