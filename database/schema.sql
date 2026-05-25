CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- FactGuard · Consolidated Supabase Schema · May 2026
-- Run once in SQL Editor. Safe to re-run (IF NOT EXISTS).
-- ============================================================
-- Shared trigger function — defined once for all tables
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$;

-- ============================================================
-- Section 1 — Claim Verification (verify mode)
-- ============================================================

-- claims — one row per verification request
CREATE TABLE IF NOT EXISTS claims (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_text TEXT NOT NULL,
  claim_hash TEXT GENERATED ALWAYS AS
    (encode(sha256(claim_text::bytea), 'hex')) STORED,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','processing','done','error')),
  job_id TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER claims_updated_at BEFORE UPDATE ON claims
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- results — one row per completed verification
CREATE TABLE IF NOT EXISTS results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  verdict TEXT NOT NULL
    CHECK (verdict IN (
      'Verified','Likely True','Mixed Evidence',
      'Likely Misleading','Unverified'
    )),
  confidence TEXT NOT NULL
    CHECK (confidence IN ('High','Medium','Low')),
  summary TEXT NOT NULL,
  supports INT NOT NULL DEFAULT 0,
  contradicts INT NOT NULL DEFAULT 0,
  neutral INT NOT NULL DEFAULT 0,
  raw_json JSONB,
  job_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER results_updated_at BEFORE UPDATE ON results
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- sources — one row per source article per result
CREATE TABLE IF NOT EXISTS sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  result_id UUID NOT NULL REFERENCES results(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  title TEXT,
  author TEXT,
  published DATE,
  stance TEXT NOT NULL
    CHECK (stance IN ('supports','contradicts','neutral')),
  relevance SMALLINT CHECK (relevance BETWEEN 0 AND 10),
  summary TEXT,
  quote TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER sources_updated_at BEFORE UPDATE ON sources
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Indexes for verify section
CREATE INDEX IF NOT EXISTS idx_claims_hash ON claims(claim_hash);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_claims_created ON claims(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_results_claim ON results(claim_id);
CREATE INDEX IF NOT EXISTS idx_results_job_id ON results(job_id);
CREATE INDEX IF NOT EXISTS idx_sources_result ON sources(result_id);

-- ============================================================
-- Section 2 — Financial Analysis (financial mode)
-- ============================================================

-- financial_results — one row per financial analysis result
CREATE TABLE IF NOT EXISTS financial_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT UNIQUE NOT NULL,
  query TEXT NOT NULL,
  result JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_financial_results_job_id ON financial_results(job_id);
CREATE INDEX IF NOT EXISTS idx_financial_results_created ON financial_results(created_at DESC);

-- ============================================================
-- Section 3 — Price Comparison (cart mode)
-- ============================================================

-- cart_results — one row per cart/price comparison result
CREATE TABLE IF NOT EXISTS cart_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT UNIQUE NOT NULL,
  product TEXT NOT NULL,
  result JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cart_results_job_id ON cart_results(job_id);
CREATE INDEX IF NOT EXISTS idx_cart_results_created ON cart_results(created_at DESC);

-- product_queries — one row per price comparison request
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

CREATE TRIGGER product_queries_updated_at BEFORE UPDATE ON product_queries
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- product_listings — one row per merchant listing per price query
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

-- Indexes for cart section
CREATE INDEX IF NOT EXISTS idx_product_queries_hash ON product_queries(search_hash);
CREATE INDEX IF NOT EXISTS idx_product_queries_status ON product_queries(status);
CREATE INDEX IF NOT EXISTS idx_product_queries_created ON product_queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_product_listings_query ON product_listings(query_id);
