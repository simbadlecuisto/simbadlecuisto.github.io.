-- ═══════════════════════════════════════════════════════════════
-- ChemistrySpot — Phase 1 Étape 2 : Table clicks (tracking)
-- Exécuter dans Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS clicks (
  id               UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
  excipient_id     INTEGER      REFERENCES excipients(id) ON DELETE SET NULL,
  excipient_nom    TEXT,
  fournisseur_id   INTEGER,
  fournisseur_nom  TEXT,
  grade_selectionne TEXT,
  url_destination  TEXT,
  created_at       TIMESTAMPTZ  DEFAULT NOW(),
  user_agent       TEXT,
  ref_source       TEXT         DEFAULT 'CS'
);

ALTER TABLE clicks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow insert clicks"
  ON clicks FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow read clicks admin"
  ON clicks FOR SELECT USING (true);

-- Index pour analytics
CREATE INDEX IF NOT EXISTS idx_clicks_excipient  ON clicks (excipient_id);
CREATE INDEX IF NOT EXISTS idx_clicks_created    ON clicks (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_clicks_ref        ON clicks (ref_source);

-- Vérification
SELECT 'Table clicks créée avec succès' AS status;
