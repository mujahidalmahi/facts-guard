CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- FactGuard · Supabase Schema · May 2026
-- Safe to re-run (IF NOT EXISTS / OR REPLACE / DROP IF EXISTS).
-- ============================================================

-- Shared trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$;

-- 1. claims — one row per verification request
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

DROP TRIGGER IF EXISTS claims_updated_at ON claims;
CREATE TRIGGER claims_updated_at BEFORE UPDATE ON claims
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 2. results — one row per completed verification
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
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. sources — one row per source article per result
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
  credibility TEXT
    CHECK (credibility IN ('High','Medium','Low'))
);

ALTER TABLE sources
ADD COLUMN IF NOT EXISTS credibility TEXT
  CHECK (credibility IN ('High','Medium','Low'));

-- Indexes
CREATE INDEX IF NOT EXISTS idx_claims_hash ON claims(claim_hash);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_claims_created ON claims(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_results_claim ON results(claim_id);
CREATE INDEX IF NOT EXISTS idx_sources_result ON sources(result_id);
