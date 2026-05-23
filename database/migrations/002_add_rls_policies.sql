-- ============================================================
-- RLS policies for public read + service-role writes
-- ============================================================
ALTER TABLE claims  ENABLE ROW LEVEL SECURITY;
ALTER TABLE results ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public select"     ON claims  FOR SELECT USING (true);
CREATE POLICY "Allow public select"     ON results FOR SELECT USING (true);
CREATE POLICY "Allow public select"     ON sources FOR SELECT USING (true);

-- Service role bypasses RLS automatically, so no extra policy needed for writes.
