# ChemistrySpot — État des lieux (maj : 2026-03-04, session Bloomberg terminal)

## Objectif Phase 1
- ~~50 excipients en base~~ ✅ **ATTEINT** (50/50, IDs 10–59)
- Page prix / fournisseurs par excipient ⏳
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
| `excipient_suppliers` | **À peupler** | SQL créé, script Python prêt, table à créer via SQL Editor |
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

**Batch 3 (IDs 40–59) — pipeline batch 3 (2026-03-04) :**
Croscarmellose sodium, Crospovidone, Sodium starch glycolate, Gelatin,
Acacia, Xanthan gum, Carboxymethylcellulose sodium, Ethyl cellulose,
Shellac, Carbomer, Sodium bicarbonate, Ascorbic acid, Alpha-tocopherol,
Butylated hydroxytoluene, Methylparaben, Propylparaben, Sorbic acid,
Potassium sorbate, Cetyl alcohol, Mineral oil

### Fournisseurs (192)
- Source : API PubChem PUG View (XML vendors) — 19 CIDs traités
- **Problème qualité : 180/192 ont `country = "Unknown"`** (détection TLD lacunaire)
- Pas de prix, pas de lien direct avec `excipients` (table `excipient_suppliers` manquante)

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

**Env :** Python 3.12 système (pas de venv actif — `chemspot_env/` n'existe pas)

---

## Front-end (GitHub Pages)

| Page | Fichier | État |
|---|---|---|
| Accueil | `index.html` | ✅ Bloomberg terminal (refait en session 2) |
| Catalogue | `catalogue.html` | Fonctionnel, Supabase live |
| Détail excipient | `produit-detail.html` | Réécrit — Tab 1 tableau prix, Tab 3 cartes fournisseurs (attend excipient_suppliers) |
| Fournisseurs | `fournisseurs.html` | 192 fournisseurs, sans lien excipient ni prix |
| Contact | `contact.html` | Fonctionnel |

**CSS :** `css/main.css`, `css/components.css`, `css/responsive.css`
**JS global :** `js/main.js` (attention aux conflits avec les scripts inline)

### index.html — Bloomberg Terminal (commit 3620306)

Architecture de la page :
- **Ticker bar** (42px, 13px, JetBrains Mono) : 30 excipients avec prix fictifs, animation CSS `scroll-left` sur tableau doublé
- **Indices** : CS-30 / CS-CEL / CS-SUC avec sparklines SVG 140×50, gradient fill
- **Gazette statique** 3 colonnes (plus de RSS/rss2json) :
  - Réglementaire (bordure bleue `#4fc3f7`) : 5 liens EMA/EDQM/ICH réels
  - Marché (bordure verte `#00d4aa`) : 5 articles PharmaCompass price trends
  - Académique (bordure jaune `#f0b429`) : 5 liens PubMed avec DOI
- **Table prix top 10** : pleine largeur, CAS, min/max, Δ30j, barre de progression
- **Section headers** : `── LABEL ──────` + ligne gradient + badge LIVE/SOURCE
- Styles scoped dans `<style>` bloc avec `!important` — autres pages non affectées

**Pourquoi RSS abandonné :** rss2json.com retourne HTTP 422 pour EMA, Pharmaphorum et PubMed. Remplacé par contenu statique curé.

---

## Priorités restantes Phase 1

1. **[DB]** ⏳ Exécuter `scripts/create_excipient_suppliers_table.sql` dans Supabase SQL Editor
2. **[DB]** ⏳ Lancer `python3 scripts/populate_excipient_suppliers.py` pour peupler la table
3. **[DATA]** Scraping prix réels (Sigma-Aldrich, TCI Chemicals) → table `prices`
4. **[QUALITE]** Améliorer détection pays fournisseurs (180/192 Unknown)

### Nouveaux scripts (session 2026-03-04)

| Script | Rôle |
|---|---|
| `scripts/create_excipient_suppliers_table.sql` | DDL table M2M + RLS |
| `scripts/populate_excipient_suppliers.py` | Peuple excipient_suppliers (réel + synthétique) |

---

## Problèmes connus

- Clés Supabase hardcodées dans les scripts (pas de .env)
- `STATUS.md` à la racine : partiellement mis à jour, à vérifier
- Conflits JS potentiels entre `main.js` et scripts inline
- `chemspot_env/` mentionné dans l'ancienne mémoire mais n'existe pas sur disque

---

## Historique commits clés

| Commit | Description |
|---|---|
| `19b923c` | Batch 3 : 20 excipients (IDs 40–59) insérés — 50/50 ✅ |
| `cd75e37` | index.html : Bloomberg terminal v1 (RSS dynamique) |
| `bb826ae` | Fix RSS URLs (rss2json proxy, hardcodées) |
| `3620306` | index.html : gazette statique + layout overhaul final |
