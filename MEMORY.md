# ChemistrySpot — État des lieux (maj : 2026-03-04, pipeline batch 3 terminé)

## Objectif Phase 1
- 50 excipients en base (actuellement : 30)
- Page prix / fournisseurs par excipient
- Site déployé sur GitHub Pages

---

## Base de données Supabase

**URL :** `https://jkaffpgqbyhuihvyvtld.supabase.co`
**Clé :** service_role (hardcodée dans les scripts — pas de .env)

### Tables existantes

| Table | Lignes | Notes |
|---|---|---|
| `excipients` | **50** ✅ | IDs 10–59 — Objectif Phase 1 atteint |
| `suppliers` | **192** | Extraits via PubChem PUG View |
| `excipient_suppliers` | **inexistante** | À créer (liaison M2M) |
| `prices` | **inexistante** | À créer (scraping futur) |

### Excipients en base (IDs 10–39)

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

**✅ 50/50 — Objectif Phase 1 excipients atteint**

### Fournisseurs (192)
- Source : API PubChem PUG View (XML vendors) — 19 CIDs traités
- Couvrent 16/19 excipients du batch 2
- **Problème qualité : 180/192 ont `country = "Unknown"** (détection TLD lacunaire)
- Pas de prix, pas de lien direct avec la table `excipients`

---

## Pipeline ETL (scripts/)

| Script | Rôle | Entrée → Sortie |
|---|---|---|
| `fetch_pubchem.py` | Récupère props chimiques via API PubChem | CID list → `data/excipients_pubchem.json` |
| `enrich_manual.py` | Enrichit avec infos pharma manuelles | pubchem.json → `data/excipients_complets.json` |
| `insert_supabase.py` | Upsert dans table `excipients` | excipients_complets.json → Supabase |
| `fetch_vendors_pubchem.py` | Récupère vendors via PUG View XML | CID list → `data/vendors_pubchem.json` |
| `insert_vendors_supabase.py` | Upsert dans table `suppliers` | vendors_pubchem.json → Supabase |

**Env :** Python 3.12, venv `chemspot_env/` (`source chemspot_env/bin/activate`)

---

## Front-end (GitHub Pages)

| Page | Fichier | État |
|---|---|---|
| Accueil | `index.html` | Fonctionnel |
| Catalogue | `catalogue.html` | Fonctionnel, Supabase live |
| Détail excipient | `produit-detail.html` | Fonctionnel, section fournisseurs vide |
| Fournisseurs | `fournisseurs.html` | Affiche les 192 fournisseurs, sans lien excipient ni prix |
| Contact | `contact.html` | Fonctionnel |

**CSS :** `css/main.css`, `css/components.css`, `css/responsive.css`
**JS global :** `js/main.js` (attention aux conflits avec les scripts inline des pages)

---

## Priorités pour atteindre Phase 1

1. ~~**[DATA]** Définir et insérer les 20 excipients manquants (IDs 40–59)~~ ✅ **DONE**
2. **[DB]** Créer table `excipient_suppliers` dans Supabase (schema : `excipient_id INT, supplier_id INT`) + peupler à partir de `vendors_pubchem.json`
3. **[FRONT]** `produit-detail.html` → section fournisseurs dynamique (requête Supabase join)
4. **[DATA]** Scraping prix (Sigma-Aldrich, TCI Chemicals, etc.) → table `prices`
5. **[QUALITE]** Améliorer détection pays fournisseurs (180/192 Unknown)

---

## Problèmes connus

- Clés Supabase hardcodées dans les scripts (pas de .env)
- `STATUS.md` à la racine est outdaté (affiche encore 9 excipients)
- Conflits JS potentiels entre `main.js` et scripts inline des pages HTML
