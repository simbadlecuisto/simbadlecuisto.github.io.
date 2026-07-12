#!/usr/bin/env python3
"""
fetch_vendors_pubchem.py — Récupère les fournisseurs depuis PubChem
Pour chaque excipient avec un CID connu, télécharge le XML des vendors
via l'API PUG View et déduplique par SourceName.
Sortie : data/vendors_pubchem.json

Usage : python3 scripts/fetch_vendors_pubchem.py
"""

import json
import time
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

PUG_VIEW_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/categories/compound/{cid}/XML"
)
NS = {"p": "http://pubchem.ncbi.nlm.nih.gov/pug_view"}

DELAY_SECONDS = 0.3        # ≤ 5 req/s (limite PubChem)
OUTPUT_FILE   = Path(__file__).parent / "data" / "vendors_pubchem.json"

# Excipients avec CID connu (les 19 qui ont retourné des données PubChem)
EXCIPIENTS = [
    {"id": 19, "nom": "Mannitol",                  "cid": 453},
    {"id": 20, "nom": "Sorbitol",                  "cid": 5780},
    {"id": 21, "nom": "Starch",                    "cid": 24832200},
    {"id": 22, "nom": "Stearic acid",              "cid": 5281},
    {"id": 23, "nom": "Citric acid",               "cid": 311},
    {"id": 24, "nom": "Sucrose",                   "cid": 5988},
    {"id": 25, "nom": "Propylene glycol",          "cid": 1030},
    {"id": 26, "nom": "Benzyl alcohol",            "cid": 244},
    {"id": 27, "nom": "Sodium lauryl sulfate",     "cid": 3423265},
    {"id": 28, "nom": "Calcium stearate",          "cid": 15985},
    {"id": 29, "nom": "Dicalcium phosphate",       "cid": 24456},
    {"id": 30, "nom": "Calcium carbonate",         "cid": 10112},
    {"id": 31, "nom": "Sodium chloride",           "cid": 5234},
    {"id": 32, "nom": "Potassium chloride",        "cid": 4873},
    {"id": 33, "nom": "Zinc oxide",                "cid": 14806},
    {"id": 34, "nom": "Colloidal silicon dioxide", "cid": 24261},
    {"id": 37, "nom": "Macrogol 4000",             "cid": 87686022},
    {"id": 38, "nom": "Polysorbate 80",            "cid": 5281955},
    {"id": 39, "nom": "Benzalkonium chloride",     "cid": 15865},
]


# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def guess_country(url: str) -> str:
    """Devine le pays depuis le TLD ou le nom de domaine."""
    if not url:
        return "Unknown"
    url_lower = url.lower()
    tld_map = {
        ".cn": "China", ".de": "Germany", ".fr": "France",
        ".uk": "United Kingdom", ".co.uk": "United Kingdom",
        ".jp": "Japan", ".in": "India", ".kr": "South Korea",
        ".ca": "Canada", ".au": "Australia", ".nl": "Netherlands",
        ".ch": "Switzerland", ".be": "Belgium", ".it": "Italy",
        ".es": "Spain", ".ru": "Russia", ".br": "Brazil",
        ".com.cn": "China",
    }
    for tld, country in tld_map.items():
        if url_lower.endswith(tld + "/") or url_lower.endswith(tld):
            return country
    # Quelques cas particuliers par domaine connu
    known = {
        "sigmaaldrich": "USA", "merck": "Germany", "thermofisher": "USA",
        "fishersci": "USA", "alfa": "USA", "tcichemicals": "Japan",
        "caymanchem": "USA", "santacruz": "USA", "scbt": "USA",
        "abcam": "United Kingdom", "lgcstandards": "United Kingdom",
        "glentham": "United Kingdom", "rrscientific": "USA",
        "acros": "Belgium",
    }
    for key, country in known.items():
        if key in url_lower:
            return country
    return "Unknown"


def fetch_vendors_for_cid(cid: int, nom: str) -> list[dict]:
    """
    Télécharge et parse le XML PubChem vendors pour un CID.
    Retourne une liste de dicts {source_name, source_url, pubchem_detail}.
    """
    url = PUG_VIEW_URL.format(cid=cid)
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print(f"    ⚠️  HTTP {r.status_code} pour CID {cid}")
            return []

        root = ET.fromstring(r.content)
        seen   = set()
        result = []

        for src in root.findall(".//p:Sources", NS):
            cat  = src.findtext("p:SourceCategories", namespaces=NS) or ""
            if "Vendor" not in cat:
                continue
            name   = src.findtext("p:SourceName",   namespaces=NS) or ""
            s_url  = src.findtext("p:SourceURL",    namespaces=NS) or ""
            detail = src.findtext("p:SourceDetail", namespaces=NS) or ""

            if name and name not in seen:
                seen.add(name)
                result.append({
                    "source_name":    name,
                    "source_url":     s_url,
                    "pubchem_detail": detail,
                    "country":        guess_country(s_url),
                })

        return result

    except Exception as e:
        print(f"    ❌ Erreur CID {cid}: {e}")
        return []


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  FETCH VENDORS PUBCHEM — ChemistrySpot")
    print(f"  {len(EXCIPIENTS)} excipients avec CID à traiter")
    print("=" * 60)

    # vendor_name → { source_url, pubchem_detail, country, excipients: [] }
    vendors_map: dict[str, dict] = {}

    for i, exc in enumerate(EXCIPIENTS, 1):
        nom = exc["nom"]
        cid = exc["cid"]
        print(f"\n[{i:02d}/{len(EXCIPIENTS)}] {nom} (CID {cid}) ...", end=" ", flush=True)

        vendors = fetch_vendors_for_cid(cid, nom)

        for v in vendors:
            name = v["source_name"]
            if name not in vendors_map:
                vendors_map[name] = {
                    "name":           name,
                    "website":        v["source_url"],
                    "pubchem_detail": v["pubchem_detail"],
                    "country":        v["country"],
                    "excipients":     [],
                }
            vendors_map[name]["excipients"].append(nom)

        print(f"{len(vendors)} vendors uniques")
        time.sleep(DELAY_SECONDS)

    # Trier par nombre d'excipients fournis (les plus polyvalents en premier)
    vendors_list = sorted(
        vendors_map.values(),
        key=lambda v: (-len(v["excipients"]), v["name"].lower())
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(vendors_list, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"  ✅ {len(vendors_list)} fournisseurs uniques trouvés")
    top = vendors_list[:5]
    print("  Top 5 (plus de produits couverts) :")
    for v in top:
        print(f"    - {v['name']} ({len(v['excipients'])} excipients, {v['country']})")
    print(f"  💾 Sauvegardé → {OUTPUT_FILE}")
    print("=" * 60)
    print("\n→ Étape suivante : python3 scripts/insert_vendors_supabase.py")


if __name__ == "__main__":
    main()
