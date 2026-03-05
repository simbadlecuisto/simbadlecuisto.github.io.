# ChemistrySpot — État des lieux (maj : 2026-03-05)

## Phases complétées

### Phase 1 ✅ COMPLETE
- 50/50 excipients en base (IDs 10–59)
- Page prix / fournisseurs par excipient (produit-detail.html)
- Site déployé sur GitHub Pages

### Phase 2 ✅ COMPLETE (2026-03-05)
- Redesign global : dark theme unifié (bg #0a0e1a / accent #00d4aa) sur les 5 pages
- `css/design-system.css` : système CSS unique remplaçant main.css/components.css
- Table `prices` créée + 50 lignes insérées (source: Estimate)
- 180/192 fournisseurs Unknown → tous corrigés (China 86, USA 60, Ukraine 7, UK 5, India 4, Germany 3…)
- `contact.html` : formulaire envoi vers Supabase `contact_requests`
- `catalogue.html` : prix lus depuis table `prices` (dynamique)
- `produit-detail.html` : bandeau "Prix indicatif marché" en Tab 1 depuis `prices`

---

## Base de données Supabase

**URL :** `https://jkaffpgqbyhuihvyvtld.supabase.co`
**Clé anon :** `eyJhbGci...OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI`
**Clé service_role :** hardcodée dans scripts INSERT/PATCH (RLS bloque anon pour écriture)

### Tables

| Table | Lignes | Notes |
|---|---|---|
| `excipients` | **50** | IDs 10–59 |
| `suppliers` | **192** | Pays corrigés ✅ (plus d'Unknown) |
| `excipient_suppliers` | **1 737** | 1 222 réelles + 515 synthétiques, prix synthétiques |
| `prices` | **50** | 1 ligne / excipient, source "Estimate", SELECT public |
| `contact_requests` | — | À créer dans Supabase (SQL: scripts/create_contact_requests_table.sql) |

**Note : `contact_requests` doit être créée manuellement dans Supabase SQL Editor.**

### Schéma prices
`id, excipient_id (FK), prix_min, prix_max, devise (EUR), source, grade, date_maj`
UNIQUE(excipient_id, source) — RLS SELECT public

### Schéma contact_requests
`id, prenom, nom, email, telephone, entreprise, poste, sujet, message, statut (nouveau/lu/traité), created_at`
RLS : INSERT public, pas de SELECT public

---

## Pipeline ETL (scripts/)

| Script | Rôle |
|---|---|
| `fetch_pubchem.py` / `enrich_manual.py` / `insert_supabase.py` | Pipeline batch 1–2 |
| `fetch_pubchem_b3.py` / `enrich_manual_b3.py` / `insert_supabase_b3.py` | Pipeline batch 3 |
| `fetch_vendors_pubchem.py` / `insert_vendors_supabase.py` | Fournisseurs PubChem |
| `populate_excipient_suppliers.py` | Peuple table M2M (1 737 rows) |
| `fetch_prices_pharmacompass.py` | Scrape Pharmacompass → `data/prices.json` (fallback catégorie) |
| `insert_prices_supabase.py` | Upsert `data/prices.json` → table `prices` (service_role) |
| `fix_supplier_countries.py` | Corrige pays fournisseurs Unknown (base manuelle 180 entrées) |
| `create_prices_table.sql` | DDL table prices |
| `create_contact_requests_table.sql` | DDL table contact_requests (**à exécuter dans Supabase**) |

**Env :** Python 3.12 système (pas de venv — `chemspot_env/` n'existe pas)
**RLS :** anon key = lecture seule ; service_role = écriture (INSERT/PATCH/UPDATE)

---

## Front-end (GitHub Pages)

| Page | État |
|---|---|
| `index.html` | ✅ Bloomberg terminal, dark theme |
| `catalogue.html` | ✅ Prix dynamiques depuis table `prices`, cards Sigma-Aldrich |
| `produit-detail.html` | ✅ Bandeau prix marché (prices table) + tableau fournisseurs (excipient_suppliers) |
| `fournisseurs.html` | ✅ 192 fournisseurs, filtres pays/excipient/recherche, tags excipients, pays corrigés |
| `contact.html` | ✅ Formulaire → Supabase contact_requests (INSERT via anon key) |

**CSS :** `css/design-system.css` (unique, remplace main.css/components.css/responsive.css)
**JS Supabase CDN :** `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2`

---

## Points d'attention

- Clés Supabase hardcodées dans HTML et scripts (pas de .env)
- `contact_requests` n'est pas encore créée dans Supabase → à faire manuellement
- Prix dans `excipient_suppliers` = synthétiques (aléatoires) — non utilisés pour affichage
- Prix dans `prices` = estimations par catégorie (Pharmacompass a bloqué le scraping)

---

## Historique commits clés

| Commit | Description |
|---|---|
| `9fb7062` | Fix 3 priorités : prix dynamiques, formulaire contact, pays fournisseurs ✅ |
| `4c8d192` | Phase 2 complete : redesign global + scripts prix/pays committed |
| `3495599` | excipient_suppliers : DDL + populate (1 737 rows) + produit-detail.html live |
| `19b923c` | Batch 3 : 20 excipients (IDs 40–59) insérés — 50/50 |
| `3620306` | index.html : gazette statique + layout overhaul |
