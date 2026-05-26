-- ============================================================
-- FactGuard · Threat Monitoring Schema · May 2026
-- ============================================================

-- 4. threats — one row per detected threat/alert
CREATE TABLE IF NOT EXISTS threats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT,
  threat_type TEXT NOT NULL
    CHECK (threat_type IN ('brand','regulatory','vendor','disinformation','general')),
  severity TEXT NOT NULL DEFAULT 'medium'
    CHECK (severity IN ('low','medium','high','critical')),
  title TEXT NOT NULL,
  description TEXT,
  source_url TEXT,
  source_domain TEXT,
  detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  alert_status TEXT NOT NULL DEFAULT 'new'
    CHECK (alert_status IN ('new','acknowledged','investigating','resolved','dismissed')),
  confidence REAL CHECK (confidence BETWEEN 0 AND 1),
  raw_evidence JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS threats_updated_at ON threats;
CREATE TRIGGER threats_updated_at BEFORE UPDATE ON threats
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 5. audit_logs — one row per API request for compliance tracking
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  action TEXT NOT NULL,
  api_endpoint TEXT,
  request_body JSONB,
  response_status INT,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_threats_type ON threats(threat_type);
CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity);
CREATE INDEX IF NOT EXISTS idx_threats_status ON threats(alert_status);
CREATE INDEX IF NOT EXISTS idx_threats_detected ON threats(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);
