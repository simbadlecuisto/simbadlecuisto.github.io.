-- Migration : ajout des colonnes académiques à la table excipients
-- À exécuter une seule fois dans Supabase SQL Editor

ALTER TABLE excipients
  ADD COLUMN IF NOT EXISTS categorie                text,
  ADD COLUMN IF NOT EXISTS formes_pharmaceutiques   text[],
  ADD COLUMN IF NOT EXISTS pharmacopees             text[],
  ADD COLUMN IF NOT EXISTS concentrations_typiques  text,
  ADD COLUMN IF NOT EXISTS mecanisme                text;
