-- ═══════════════════════════════════════════════════════════════
-- ChemistrySpot — Supply Chain Map : 2 nouvelles tables
-- Exécuter dans Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════

-- ── TABLE 1 : supply_chain_data ──────────────────────────────
-- Flux commerciaux UN Comtrade (top exportateurs par excipient)

CREATE TABLE IF NOT EXISTS supply_chain_data (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    excipient_nom    TEXT          NOT NULL,
    hs_code          VARCHAR(10)   NOT NULL,
    country_iso3     VARCHAR(3)    NOT NULL,
    country_name     TEXT          NOT NULL,
    lat              DECIMAL(8,5),
    lng              DECIMAL(8,5),
    export_value_usd BIGINT,
    export_qty_kg    BIGINT,
    market_share_pct DECIMAL(5,2),
    rank_in_excipient INT,
    year             INT           NOT NULL DEFAULT 2023,
    source           TEXT          DEFAULT 'UN Comtrade',
    created_at       TIMESTAMPTZ   DEFAULT NOW(),
    UNIQUE(excipient_nom, country_iso3, year)
);

ALTER TABLE supply_chain_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read supply_chain_data"
    ON supply_chain_data FOR SELECT USING (true);

CREATE INDEX IF NOT EXISTS idx_scd_excipient ON supply_chain_data(excipient_nom);
CREATE INDEX IF NOT EXISTS idx_scd_country   ON supply_chain_data(country_iso3);
CREATE INDEX IF NOT EXISTS idx_scd_year      ON supply_chain_data(year);

-- ── TABLE 2 : geopolitical_risks ─────────────────────────────
-- Évaluation risque géopolitique par pays (mise à jour manuelle/trimestrielle)

CREATE TABLE IF NOT EXISTS geopolitical_risks (
    id                     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_iso3           VARCHAR(3)   NOT NULL UNIQUE,
    country_name           TEXT         NOT NULL,
    risk_level             INT          NOT NULL CHECK (risk_level BETWEEN 1 AND 5),
    -- 1=Faible  2=Faible-Modéré  3=Modéré  4=Élevé  5=Critique
    risk_label             TEXT         NOT NULL,
    risk_color             TEXT         NOT NULL,  -- hex couleur carte
    risk_factors           TEXT[]       DEFAULT '{}',
    political_stability    DECIMAL(4,2),           -- World Bank score (-2.5 à +2.5)
    supply_disruption_risk TEXT CHECK (supply_disruption_risk IN ('low','medium','high','critical')),
    sanctions_active       BOOLEAN      DEFAULT FALSE,
    export_restrictions    BOOLEAN      DEFAULT FALSE,
    notes                  TEXT,
    last_updated           TIMESTAMPTZ  DEFAULT NOW()
);

ALTER TABLE geopolitical_risks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read geopolitical_risks"
    ON geopolitical_risks FOR SELECT USING (true);

CREATE INDEX IF NOT EXISTS idx_gr_country    ON geopolitical_risks(country_iso3);
CREATE INDEX IF NOT EXISTS idx_gr_risk_level ON geopolitical_risks(risk_level);

-- Vérification
SELECT
    (SELECT COUNT(*) FROM supply_chain_data)   AS supply_chain_rows,
    (SELECT COUNT(*) FROM geopolitical_risks)  AS geopolitical_rows;
