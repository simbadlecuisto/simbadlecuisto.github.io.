-- ═══════════════════════════════════════════════════════════════
-- ChemistrySpot — Table contact_requests
-- Exécuter dans Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS contact_requests (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prenom      VARCHAR(100) NOT NULL,
    nom         VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    telephone   VARCHAR(30),
    entreprise  VARCHAR(200) NOT NULL,
    poste       VARCHAR(100),
    sujet       VARCHAR(50)  NOT NULL,
    message     TEXT         NOT NULL,
    statut      VARCHAR(20)  DEFAULT 'nouveau',   -- nouveau / lu / traité
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

ALTER TABLE contact_requests ENABLE ROW LEVEL SECURITY;

-- Permettre l'insertion publique (formulaire de contact)
CREATE POLICY "Allow public insert" ON contact_requests
    FOR INSERT WITH CHECK (true);

-- Lecture réservée aux admins (service_role uniquement via RLS)
-- (pas de SELECT policy publique)

-- Index
CREATE INDEX IF NOT EXISTS idx_contact_requests_email   ON contact_requests(email);
CREATE INDEX IF NOT EXISTS idx_contact_requests_statut  ON contact_requests(statut);
CREATE INDEX IF NOT EXISTS idx_contact_requests_created ON contact_requests(created_at DESC);

SELECT 'Table contact_requests créée avec succès' AS status;
