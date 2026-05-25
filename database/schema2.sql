-- ============================================================
-- FactGuard · Schema Migration · May 2026
-- Add timestamps to results + sources (run after schema.sql)
-- ============================================================

-- Shared trigger function (safe to re-run)
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$;

-- RESULTS TABLE
ALTER TABLE results
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

DROP TRIGGER IF EXISTS results_updated_at ON results;
CREATE TRIGGER results_updated_at
  BEFORE UPDATE ON results
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE results
ADD COLUMN IF NOT EXISTS job_id TEXT;

CREATE INDEX IF NOT EXISTS idx_results_job_id ON results(job_id);

-- SOURCES TABLE
ALTER TABLE sources
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE sources
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

DROP TRIGGER IF EXISTS sources_updated_at ON sources;
CREATE TRIGGER sources_updated_at
  BEFORE UPDATE ON sources
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
