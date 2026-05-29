-- ============================================================
-- FactGuard · Financial Analysis & Cart Schema · May 2026
-- Tables for the financial analysis and cart price modes.
-- ============================================================

-- 1. financial_results — one row per financial analysis
CREATE TABLE IF NOT EXISTS financial_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT UNIQUE NOT NULL,
  query TEXT NOT NULL,
  result JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_financial_results_job_id ON financial_results(job_id);
CREATE INDEX IF NOT EXISTS idx_financial_results_created ON financial_results(created_at DESC);

-- 2. cart_results — one row per cart/price comparison result
CREATE TABLE IF NOT EXISTS cart_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT UNIQUE NOT NULL,
  product TEXT NOT NULL,
  result JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cart_results_job_id ON cart_results(job_id);
CREATE INDEX IF NOT EXISTS idx_cart_results_created ON cart_results(created_at DESC);
