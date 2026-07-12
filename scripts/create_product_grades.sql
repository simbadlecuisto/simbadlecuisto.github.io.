-- ═══════════════════════════════════════════════════════════════
-- ChemistrySpot — Table product_grades (Phase B, feuille de route v7.1)
-- Grades commerciaux par excipient (ex. MCC PH-101 vs PH-102)
-- Exécuter dans Supabase Dashboard > SQL Editor
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS product_grades (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    excipient_id    BIGINT NOT NULL REFERENCES excipients(id) ON DELETE CASCADE,
    grade_name      VARCHAR(100) NOT NULL,      -- ex. 'PH-102'
    nom_commercial  VARCHAR(150),               -- ex. 'Avicel PH-102' + fabricant
    fabricant       VARCHAR(120),               -- ex. 'IFF (ex-DuPont)'
    specs           JSONB DEFAULT '{}'::jsonb,  -- d50_um, densite_vrac_g_ml, humidite_pct_max…
    pharmacopees    TEXT[],                     -- {Ph.Eur., USP-NF, JP}
    usage_principal TEXT,                       -- ex. 'Compression directe'
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (excipient_id, grade_name)
);

ALTER TABLE product_grades ENABLE ROW LEVEL SECURITY;

-- Lecture publique (affichage site) ; écriture réservée service_role
CREATE POLICY "Public read" ON product_grades
    FOR SELECT USING (true);

CREATE INDEX IF NOT EXISTS idx_product_grades_excipient ON product_grades(excipient_id);

SELECT 'Table product_grades créée avec succès' AS status;
