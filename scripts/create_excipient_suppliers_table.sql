-- ============================================================
-- DDL : table excipient_suppliers (liaison M2M excipients × suppliers)
-- Coller dans Supabase SQL Editor (Dashboard > SQL Editor)
-- ============================================================

CREATE TABLE IF NOT EXISTS excipient_suppliers (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    excipient_id     INT          NOT NULL,
    supplier_id      INT          NOT NULL,
    prix_min         DECIMAL(10,2),
    prix_max         DECIMAL(10,2),
    devise           VARCHAR(3)   NOT NULL DEFAULT 'EUR',
    delai_livraison  VARCHAR(50),
    stock_disponible BOOLEAN      NOT NULL DEFAULT true,
    certifications   TEXT[]       DEFAULT '{}',
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_excipient_supplier UNIQUE (excipient_id, supplier_id),
    CONSTRAINT fk_excipient FOREIGN KEY (excipient_id)
        REFERENCES excipients(id) ON DELETE CASCADE,
    CONSTRAINT fk_supplier  FOREIGN KEY (supplier_id)
        REFERENCES suppliers(id)  ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_es_excipient ON excipient_suppliers(excipient_id);
CREATE INDEX IF NOT EXISTS idx_es_supplier  ON excipient_suppliers(supplier_id);

-- Row Level Security : lecture publique (anon key), écriture service_role uniquement
ALTER TABLE excipient_suppliers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read"
    ON excipient_suppliers FOR SELECT USING (true);
