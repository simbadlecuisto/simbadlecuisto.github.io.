-- Migration : création de la table formulations
-- À exécuter dans Supabase SQL Editor

CREATE TABLE IF NOT EXISTS formulations (
    id                  serial PRIMARY KEY,
    excipient_id        integer NOT NULL REFERENCES excipients(id) ON DELETE CASCADE,
    nom_formulation     text NOT NULL,
    type_forme          text,
    role_excipient      text,
    concentration       text,
    pa_exemple          text,
    autres_excipients   text[],
    notes               text,
    created_at          timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_formulations_excipient_id
    ON formulations(excipient_id);

-- Lecture publique (SELECT sans authentification)
ALTER TABLE formulations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "formulations_public_read"
    ON formulations FOR SELECT
    USING (true);
