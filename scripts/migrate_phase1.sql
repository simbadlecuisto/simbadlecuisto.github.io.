-- ═══════════════════════════════════════════════════════════════
-- ChemistrySpot — Phase 1 : Moteur de recherche avancé
-- Migration : nouvelles colonnes table excipients
-- Exécuter dans Supabase SQL Editor (Dashboard > SQL Editor)
-- ═══════════════════════════════════════════════════════════════

ALTER TABLE excipients
  ADD COLUMN IF NOT EXISTS grades             TEXT[],
  ADD COLUMN IF NOT EXISTS taille_particule_min INTEGER,
  ADD COLUMN IF NOT EXISTS taille_particule_max INTEGER,
  ADD COLUMN IF NOT EXISTS certifications     TEXT[],
  ADD COLUMN IF NOT EXISTS conditionnements   TEXT[],
  ADD COLUMN IF NOT EXISTS origine            TEXT[],
  ADD COLUMN IF NOT EXISTS stock_disponible   BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS lien_produit_direct TEXT;

-- Index pour les recherches par certification et stock
CREATE INDEX IF NOT EXISTS idx_excipients_certifications  ON excipients USING GIN (certifications);
CREATE INDEX IF NOT EXISTS idx_excipients_grades          ON excipients USING GIN (grades);
CREATE INDEX IF NOT EXISTS idx_excipients_origine         ON excipients USING GIN (origine);
CREATE INDEX IF NOT EXISTS idx_excipients_conditionnements ON excipients USING GIN (conditionnements);
CREATE INDEX IF NOT EXISTS idx_excipients_stock           ON excipients (stock_disponible);

-- Vérification
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'excipients'
  AND column_name IN ('grades','taille_particule_min','taille_particule_max',
                      'certifications','conditionnements','origine',
                      'stock_disponible','lien_produit_direct')
ORDER BY column_name;
