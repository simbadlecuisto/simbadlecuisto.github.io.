-- ═══════════════════════════════════════════════════════════════
-- ChemistrySpot — Table prices
-- Exécuter dans Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS prices (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    excipient_id INT NOT NULL REFERENCES excipients(id) ON DELETE CASCADE,
    prix_min    DECIMAL(10,2),
    prix_max    DECIMAL(10,2),
    devise      VARCHAR(3)   DEFAULT 'EUR',
    source      VARCHAR(100) DEFAULT 'Pharmacompass',
    grade       VARCHAR(50),
    date_maj    TIMESTAMPTZ  DEFAULT NOW(),
    UNIQUE(excipient_id, source)
);

ALTER TABLE prices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read" ON prices FOR SELECT USING (true);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_prices_excipient ON prices(excipient_id);
CREATE INDEX IF NOT EXISTS idx_prices_source    ON prices(source);

-- Vérification
SELECT 'Table prices créée avec succès' AS status;
