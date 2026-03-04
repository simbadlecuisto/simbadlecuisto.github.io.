# ChemistrySpot — État des lieux (maj : 2026-03-04, session excipient_suppliers)

## Objectif Phase 1
- ~~50 excipients en base~~ ✅ **ATTEINT** (50/50, IDs 10–59)
- ~~Page prix / fournisseurs par excipient~~ ✅ **ATTEINT** (produit-detail.html live)
- Site déployé sur GitHub Pages ✅

---

## Base de données Supabase

**URL :** `https://jkaffpgqbyhuihvyvtld.supabase.co`
**Clé :** service_role (hardcodée dans les scripts — pas de .env)

### Tables existantes

| Table | Lignes | Notes |
|---|---|---|
| `excipients` | **50** ✅ | IDs 10–59 |
| `suppliers` | **192** | Extraits via PubChem PUG View |
| `excipient_suppliers` | **1 737** ✅ | 1 222 réelles (PubChem) + 515 synthétiques, 50 excipients couverts |
| `prices` | **inexistante** | À créer (scraping futur) |

### Excipients en base

**Batch 1 (IDs 10–18) — insérés manuellement :**
Lactose, Microcrystalline cellulose, Magnesium stearate, Povidone, Talc,
Titanium dioxide, Glycerol, Purified water, Ethanol

**Batch 2 (IDs 19–39) — pipeline PubChem :**
Mannitol, Sorbitol, Starch, Stearic acid, Citric acid, Sucrose,
Propylene glycol, Benzyl alcohol, Sodium lauryl sulfate, Calcium stearate,
Dicalcium phosphate, Calcium carbonate, Sodium chloride, Potassium chloride,
Zinc oxide, Colloidal silicon dioxide, Hydroxypropyl cellulose, Hypromellose,
Macrogol 4000, Polysorbate 80, Benzalkonium chloride

**Batch 3 (IDs 40–59) — pipeline batch 3 :**
Croscarmellose sodium, Crospovidone, Sodium starch glycolate, Gelatin,
Acacia, Xanthan gum, Carboxymethylcellulose sodium, Ethyl cellulose,
Shellac, Carbomer, Sodium bicarbonate, Ascorbic acid, Alpha-tocopherol,
Butylated hydroxytoluene, Methylparaben, Propylparaben, Sorbic acid,
Potassium sorbate, Cetyl alcohol, Mineral oil

### Fournisseurs (192)
- Source : API PubChem PUG View (XML vendors) — 19 CIDs traités
- **Problème qualité : 180/192 ont `country = "Unknown"`** (détection TLD lacunaire)
- Liés aux excipients via `excipient_suppliers` ✅

### excipient_suppliers
- Schéma : `excipient_id`, `supplier_id`, `prix_min`, `prix_max`, `devise`, `delai_livraison`, `stock_disponible`, `certifications[]`
- Contraintes : UNIQUE(excipient_id, supplier_id), FK vers excipients et suppliers, RLS SELECT public
- Prix par catégorie (bulk_commodity 5–25 €/kg, specialty_polymer 20–90, coating_polymer 30–180, etc.)
- Certifications : GMP, ISO 9001, USP/NF, Ph.Eur., DMF, Halal, Kosher, FDA IND

---

## Pipeline ETL (scripts/)

| Script | Rôle | Entrée → Sortie |
|---|---|---|
| `fetch_pubchem.py` | Props chimiques via PubChem REST | CID list → `data/excipients_pubchem.json` |
| `enrich_manual.py` | Enrichissement pharma manuel | pubchem.json → `data/excipients_complets.json` |
| `insert_supabase.py` | Upsert table `excipients` | excipients_complets.json → Supabase |
| `fetch_pubchem_b3.py` | Idem batch 3 (IDs 40–59) | CID list → `data/excipients_pubchem_b3.json` |
| `enrich_manual_b3.py` | Enrichissement batch 3 | pubchem_b3.json → `data/excipients_complets_b3.json` |
| `insert_supabase_b3.py` | Upsert batch 3 | excipients_complets_b3.json → Supabase |
| `fetch_vendors_pubchem.py` | Vendors via PUG View XML | CID list → `data/vendors_pubchem.json` |
| `insert_vendors_supabase.py` | Upsert table `suppliers` | vendors_pubchem.json → Supabase |
| `create_excipient_suppliers_table.sql` | DDL table M2M + RLS | À coller dans Supabase SQL Editor |
| `populate_excipient_suppliers.py` | Peuple excipient_suppliers | vendors_pubchem.json + Supabase → 1 737 rows |

**Env :** Python 3.12 système (pas de venv actif — `chemspot_env/` n'existe pas)

---

## Front-end (GitHub Pages)

| Page | Fichier | État |
|---|---|---|
| Accueil | `index.html` | ✅ Bloomberg terminal |
| Catalogue | `catalogue.html` | ✅ Fonctionnel, Supabase live |
| Détail excipient | `produit-detail.html` | ✅ Tab 1 tableau prix live, Tab 3 cartes fournisseurs live |
| Fournisseurs | `fournisseurs.html` | 192 fournisseurs, sans lien prix |
| Contact | `contact.html` | Fonctionnel |

**CSS :** `css/main.css`, `css/components.css`, `css/responsive.css`
**JS global :** `js/main.js` (attention aux conflits avec les scripts inline)

### produit-detail.html — architecture (commit 3495599)

- **Tab 1 "Prix & Fournisseurs"** : tableau comparatif trié prix_min ASC — colonnes fournisseur (lien website), pays + flag, prix min/max (€/kg), devise, délai, badge stock, badges certif colorés, bouton devis
- **Tab 2 "Analyse Marché"** : placeholder Phase 2
- **Tab 3 "Fournisseurs"** : grille de cartes — flag pays, plage prix, certifications, lien site web, bouton devis
- **Tab 4 "Alertes Réglementaires"** : placeholder Phase 2
- Requête Supabase : `excipient_suppliers.select('*, suppliers(id, name, country, website)').eq('excipient_id', id).order('prix_min')`

### index.html — Bloomberg Terminal (commit 3620306)

- **Ticker bar** : 30 excipients avec prix fictifs, animation CSS `scroll-left`
- **Indices** : CS-30 / CS-CEL / CS-SUC avec sparklines SVG
- **Gazette statique** 3 colonnes (Réglementaire / Marché / Académique) — contenu curé, RSS abandonné
- **Table prix top 10** : CAS, min/max, Δ30j, barre de progression

---

## Priorités Phase 2

1. **[DATA]** Scraping prix réels (Sigma-Aldrich, TCI Chemicals) → table `prices`
2. **[QUALITE]** Améliorer détection pays fournisseurs (180/192 Unknown)
3. **[FRONT]** `fournisseurs.html` → afficher excipients liés par fournisseur
4. **[FRONT]** Tab "Analyse Marché" → indices de prix, volumes, tendances

---

## Problèmes connus

- Clés Supabase hardcodées dans les scripts (pas de .env)
- `STATUS.md` à la racine : partiellement mis à jour, à vérifier
- Conflits JS potentiels entre `main.js` et scripts inline

---

## Historique commits clés

| Commit | Description |
|---|---|
| `3495599` | excipient_suppliers : DDL + populate (1 737 rows) + produit-detail.html live ✅ |
| `19b923c` | Batch 3 : 20 excipients (IDs 40–59) insérés — 50/50 ✅ |
| `3620306` | index.html : gazette statique + layout overhaul final |
| `cd75e37` | index.html : Bloomberg terminal v1 |
