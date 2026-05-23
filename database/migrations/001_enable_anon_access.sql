-- ============================================================
-- Bypass RLS for public reads (no user auth in this app)
-- Run once after schema.sql
-- ============================================================
ALTER TABLE claims  DISABLE ROW LEVEL SECURITY;
ALTER TABLE results DISABLE ROW LEVEL SECURITY;
ALTER TABLE sources DISABLE ROW LEVEL SECURITY;
