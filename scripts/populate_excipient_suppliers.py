#!/usr/bin/env python3
"""
populate_excipient_suppliers.py — Peuple la table excipient_suppliers dans Supabase.

Sources :
  - data/vendors_pubchem.json  : liens réels vendor×excipient (batch 2, IDs 19-39)
  - Assignation synthétique   : excipients sans données PubChem (batches 1 et 3)

Prérequis :
  La table excipient_suppliers doit exister (exécuter create_excipient_suppliers_table.sql
  dans Supabase SQL Editor avant de lancer ce script).

Usage : python3 scripts/populate_excipient_suppliers.py
"""

import json
import random
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

# ─────────────────────────────────────────────
# CONFIGURATION SUPABASE
# ─────────────────────────────────────────────

SUPABASE_URL      = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SUPABASE_SERV_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwi"
    "cm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3"
    "MjM0Mzk0fQ.dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0"
)

HEADERS = {
    "apikey":        SUPABASE_SERV_KEY,
    "Authorization": f"Bearer {SUPABASE_SERV_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "resolution=merge-duplicates,return=representation",
}

ES_URL      = f"{SUPABASE_URL}/rest/v1/excipient_suppliers"
SUP_URL     = f"{SUPABASE_URL}/rest/v1/suppliers"
EXC_URL     = f"{SUPABASE_URL}/rest/v1/excipients"
DELAY       = 0.15
BATCH_SIZE  = 50

VENDORS_FILE = Path(__file__).parent / "data" / "vendors_pubchem.json"
REPORT_FILE  = Path(__file__).parent / "data" / "excipient_suppliers_report.json"

# ─────────────────────────────────────────────
# CATÉGORIES DE PRIX (€/kg)
# ─────────────────────────────────────────────

PRICE_RANGES = {
    "bulk_commodity":   (5,   25),
    "lipid_wax":        (5,   40),
    "inorganic":        (5,   35),
    "specialty_polymer":(20,  90),
    "coating_polymer":  (30, 180),
    "surfactant":       (15,  80),
    "preservative":     (20, 120),
    "antioxidant":      (20, 100),
    "solvent":          (3,   40),
    "buffer":           (5,   30),
}

# Mapping excipient nom_commun → catégorie de prix
EXCIPIENT_CATEGORIES = {
    # Batch 1
    "Lactose":                    "bulk_commodity",
    "Microcrystalline cellulose": "bulk_commodity",
    "Magnesium stearate":         "lipid_wax",
    "Povidone":                   "specialty_polymer",
    "Talc":                       "inorganic",
    "Titanium dioxide":           "inorganic",
    "Glycerol":                   "solvent",
    "Purified water":             "solvent",
    "Ethanol":                    "solvent",
    # Batch 2
    "Mannitol":                   "bulk_commodity",
    "Sorbitol":                   "bulk_commodity",
    "Starch":                     "bulk_commodity",
    "Stearic acid":               "lipid_wax",
    "Citric acid":                "buffer",
    "Sucrose":                    "bulk_commodity",
    "Propylene glycol":           "solvent",
    "Benzyl alcohol":             "solvent",
    "Sodium lauryl sulfate":      "surfactant",
    "Calcium stearate":           "lipid_wax",
    "Dicalcium phosphate":        "inorganic",
    "Calcium carbonate":          "inorganic",
    "Sodium chloride":            "bulk_commodity",
    "Potassium chloride":         "bulk_commodity",
    "Zinc oxide":                 "inorganic",
    "Colloidal silicon dioxide":  "inorganic",
    "Hydroxypropyl cellulose":    "specialty_polymer",
    "Hypromellose":               "specialty_polymer",
    "Macrogol 4000":              "specialty_polymer",
    "Polysorbate 80":             "surfactant",
    "Benzalkonium chloride":      "surfactant",
    # Batch 3
    "Croscarmellose sodium":      "specialty_polymer",
    "Crospovidone":               "specialty_polymer",
    "Sodium starch glycolate":    "specialty_polymer",
    "Gelatin":                    "coating_polymer",
    "Acacia":                     "coating_polymer",
    "Xanthan gum":                "coating_polymer",
    "Carboxymethylcellulose sodium": "specialty_polymer",
    "Ethyl cellulose":            "coating_polymer",
    "Shellac":                    "coating_polymer",
    "Carbomer":                   "coating_polymer",
    "Sodium bicarbonate":         "buffer",
    "Ascorbic acid":              "antioxidant",
    "Alpha-tocopherol":           "antioxidant",
    "Butylated hydroxytoluene":   "preservative",
    "Methylparaben":              "preservative",
    "Propylparaben":              "preservative",
    "Sorbic acid":                "preservative",
    "Potassium sorbate":          "preservative",
    "Cetyl alcohol":              "lipid_wax",
    "Mineral oil":                "lipid_wax",
}

# ─────────────────────────────────────────────
# CERTIFICATIONS
# ─────────────────────────────────────────────

ALL_CERTS = ["GMP", "ISO 9001", "USP/NF", "Ph.Eur.", "DMF", "Halal", "Kosher", "FDA IND"]

# Certifications préférentielles par nom fournisseur (contient)
CERT_PREFS = {
    "sigma": ["USP/NF", "Ph.Eur.", "GMP", "ISO 9001"],
    "merck": ["USP/NF", "Ph.Eur.", "GMP", "DMF"],
    "tci":   ["USP/NF", "GMP", "ISO 9001"],
    "alfa":  ["GMP", "ISO 9001", "USP/NF"],
    "acros": ["USP/NF", "GMP"],
    "thermo": ["GMP", "ISO 9001", "USP/NF"],
    "fluka": ["USP/NF", "Ph.Eur."],
    "carlo": ["Ph.Eur.", "GMP"],
}

DELIVERY_DELAYS = ["2-5 jours", "5-10 jours", "2-3 semaines", "4-6 semaines"]
DELIVERY_WEIGHTS = [0.25, 0.40, 0.25, 0.10]


def pick_certs(supplier_name: str) -> list[str]:
    """Choisit 1-3 certifications adaptées au fournisseur."""
    name_lower = supplier_name.lower()
    pool = ALL_CERTS
    for key, preferred in CERT_PREFS.items():
        if key in name_lower:
            pool = preferred
            break
    n = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
    return random.sample(pool, min(n, len(pool)))


def pick_delivery() -> str:
    return random.choices(DELIVERY_DELAYS, weights=DELIVERY_WEIGHTS)[0]


def generate_prices(nom_commun: str) -> tuple[float, float]:
    """Génère prix_min et prix_max réalistes pour un excipient."""
    cat = EXCIPIENT_CATEGORIES.get(nom_commun, "bulk_commodity")
    base_min, base_max_range = PRICE_RANGES[cat]
    prix_min = round(base_min * random.uniform(0.8, 1.1), 2)
    prix_max = round(prix_min * random.uniform(1.3, 2.0), 2)
    # Clamp prix_max au plafond de la catégorie
    prix_max = min(prix_max, base_max_range * 1.2)
    return prix_min, prix_max


# ─────────────────────────────────────────────
# FETCH DONNÉES SUPABASE
# ─────────────────────────────────────────────

def fetch_all(url: str, select: str, limit: int = 300) -> list[dict]:
    """Récupère toutes les lignes d'une table Supabase."""
    headers_read = {
        "apikey":        SUPABASE_SERV_KEY,
        "Authorization": f"Bearer {SUPABASE_SERV_KEY}",
    }
    r = requests.get(
        url,
        headers=headers_read,
        params={"select": select, "limit": limit},
        timeout=20,
    )
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} : {r.text[:300]}")
    return r.json()


def check_table_exists() -> bool:
    """Vérifie que la table excipient_suppliers existe en faisant une requête minimale."""
    headers_read = {
        "apikey":        SUPABASE_SERV_KEY,
        "Authorization": f"Bearer {SUPABASE_SERV_KEY}",
    }
    r = requests.get(
        ES_URL,
        headers=headers_read,
        params={"select": "id", "limit": 1},
        timeout=10,
    )
    return r.status_code == 200


# ─────────────────────────────────────────────
# GÉNÉRATION DES ROWS
# ─────────────────────────────────────────────

def build_rows_from_vendors(
    vendors: list[dict],
    supplier_map: dict[str, int],  # name → id
    excipient_map: dict[str, int], # nom_commun → id
) -> list[dict]:
    """
    Construit les rows excipient_suppliers depuis vendors_pubchem.json.
    Utilise les liens réels vendor×excipient (batch 2).
    """
    rows = []
    seen = set()

    for vendor in vendors:
        sup_name = vendor["name"]
        sup_id = supplier_map.get(sup_name)
        if sup_id is None:
            continue

        for exc_name in vendor.get("excipients", []):
            exc_id = excipient_map.get(exc_name)
            if exc_id is None:
                continue
            key = (exc_id, sup_id)
            if key in seen:
                continue
            seen.add(key)

            prix_min, prix_max = generate_prices(exc_name)
            rows.append({
                "excipient_id":     exc_id,
                "supplier_id":      sup_id,
                "prix_min":         prix_min,
                "prix_max":         prix_max,
                "devise":           "EUR",
                "delai_livraison":  pick_delivery(),
                "stock_disponible": random.random() > 0.15,
                "certifications":   pick_certs(sup_name),
            })

    return rows


def build_synthetic_rows(
    excipient_map: dict[str, int],
    supplier_ids: list[int],
    vendor_covered_exc_ids: set[int],
    supplier_names: dict[int, str],
) -> list[dict]:
    """
    Pour les excipients sans données PubChem (batches 1 et 3),
    assigne aléatoirement 5-25 fournisseurs par excipient.
    """
    rows = []
    seen = set()

    # Excipients batch 1 et 3 qui n'ont pas de vrais fournisseurs
    synthetic_excipients = {
        nom: eid for nom, eid in excipient_map.items()
        if eid not in vendor_covered_exc_ids
    }

    print(f"  Excipients sans fournisseurs PubChem : {len(synthetic_excipients)}")

    for nom_commun, exc_id in synthetic_excipients.items():
        n_suppliers = random.randint(5, 25)
        chosen_ids = random.sample(supplier_ids, min(n_suppliers, len(supplier_ids)))

        for sup_id in chosen_ids:
            key = (exc_id, sup_id)
            if key in seen:
                continue
            seen.add(key)

            prix_min, prix_max = generate_prices(nom_commun)
            sup_name = supplier_names.get(sup_id, "")
            rows.append({
                "excipient_id":     exc_id,
                "supplier_id":      sup_id,
                "prix_min":         prix_min,
                "prix_max":         prix_max,
                "devise":           "EUR",
                "delai_livraison":  pick_delivery(),
                "stock_disponible": random.random() > 0.15,
                "certifications":   pick_certs(sup_name),
            })

    return rows


# ─────────────────────────────────────────────
# INSERTION
# ─────────────────────────────────────────────

def insert_batch(rows: list[dict]) -> dict:
    """Insère un lot de rows dans excipient_suppliers."""
    try:
        r = requests.post(ES_URL, headers=HEADERS, json=rows, timeout=30)
        if r.status_code in (200, 201):
            return {"ok": True, "status": r.status_code, "error": None}
        return {"ok": False, "status": r.status_code, "error": r.text[:300]}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e)}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    random.seed(42)  # reproductibilité

    print("=" * 60)
    print("  POPULATE EXCIPIENT_SUPPLIERS — ChemistrySpot")
    print(f"  Démarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 0. Vérifier que la table existe
    print("\n🔍 Vérification table excipient_suppliers...")
    if not check_table_exists():
        print("\n❌ La table excipient_suppliers n'existe pas dans Supabase.")
        print("   Exécutez d'abord le SQL dans Supabase SQL Editor :")
        print("   scripts/create_excipient_suppliers_table.sql")
        return

    print("   ✅ Table détectée")

    # 1. Charger les données de référence depuis Supabase
    print("\n📡 Chargement des données depuis Supabase...")

    excipients_raw = fetch_all(EXC_URL, "id,nom_commun", limit=100)
    suppliers_raw  = fetch_all(SUP_URL, "id,name",       limit=300)

    excipient_map = {e["nom_commun"]: e["id"] for e in excipients_raw}
    supplier_map  = {s["name"]: s["id"] for s in suppliers_raw}
    supplier_names = {s["id"]: s["name"] for s in suppliers_raw}
    supplier_ids   = [s["id"] for s in suppliers_raw]

    print(f"   {len(excipient_map)} excipients chargés")
    print(f"   {len(supplier_map)} fournisseurs chargés")

    # 2. Charger vendors_pubchem.json
    if not VENDORS_FILE.exists():
        print(f"\n❌ Fichier introuvable : {VENDORS_FILE}")
        return

    with open(VENDORS_FILE, encoding="utf-8") as f:
        vendors = json.load(f)

    print(f"\n📂 {len(vendors)} vendors dans {VENDORS_FILE.name}")

    # 3. Construire rows réels depuis vendors_pubchem.json
    print("\n🔗 Construction des liens réels (vendors_pubchem.json)...")
    real_rows = build_rows_from_vendors(vendors, supplier_map, excipient_map)

    vendor_covered_exc_ids = {r["excipient_id"] for r in real_rows}
    print(f"   {len(real_rows)} liens réels générés")
    print(f"   {len(vendor_covered_exc_ids)} excipients couverts par données PubChem")

    # 4. Construire rows synthétiques pour les excipients non couverts
    print("\n🎲 Génération des liens synthétiques (excipients sans données PubChem)...")
    synthetic_rows = build_synthetic_rows(
        excipient_map, supplier_ids, vendor_covered_exc_ids, supplier_names
    )
    print(f"   {len(synthetic_rows)} liens synthétiques générés")

    # 5. Fusionner et dédupliquer
    all_rows = real_rows + synthetic_rows
    print(f"\n📊 Total : {len(all_rows)} lignes à insérer")

    # 6. Insertion par batches
    print(f"\n💾 Insertion dans Supabase (batches de {BATCH_SIZE})...")

    results       = []
    success_count = 0
    error_count   = 0

    for batch_start in range(0, len(all_rows), BATCH_SIZE):
        batch     = all_rows[batch_start:batch_start + BATCH_SIZE]
        batch_end = batch_start + len(batch)
        print(
            f"  Lot [{batch_start + 1:04d}–{batch_end:04d}/{len(all_rows)}] ...",
            end=" ",
            flush=True,
        )
        result = insert_batch(batch)
        if result["ok"]:
            success_count += len(batch)
            print(f"✅ ({len(batch)} lignes)")
        else:
            error_count += len(batch)
            print(f"❌  HTTP {result['status']} — {result['error']}")

        results.append({
            "batch":       f"{batch_start + 1}-{batch_end}",
            "count":       len(batch),
            "ok":          result["ok"],
            "http_status": result["status"],
            "error":       result["error"],
        })
        time.sleep(DELAY)

    # 7. Rapport
    rapport = {
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "total_rows":        len(all_rows),
        "real_rows":         len(real_rows),
        "synthetic_rows":    len(synthetic_rows),
        "excipients_covered": len({r["excipient_id"] for r in all_rows}),
        "success":           success_count,
        "errors":            error_count,
        "batches":           results,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"  ✅ {success_count}/{len(all_rows)} lignes insérées avec succès")
    print(f"     dont {len(real_rows)} réelles + {len(synthetic_rows)} synthétiques")
    if error_count:
        print(f"  ❌ {error_count} erreur(s) — voir {REPORT_FILE.name}")
    print(f"  💾 Rapport → {REPORT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
