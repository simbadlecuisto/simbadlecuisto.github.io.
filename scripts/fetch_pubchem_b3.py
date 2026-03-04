#!/usr/bin/env python3
"""
fetch_pubchem_b3.py — Batch 3 (IDs 40-59)
Récupère les données chimiques depuis l'API PubChem pour 20 nouveaux excipients.
Sortie : data/excipients_pubchem_b3.json

Usage : python3 scripts/fetch_pubchem_b3.py
"""

import json
import time
import requests
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

PUBCHEM_PROPS_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/"
    "MolecularFormula,MolecularWeight,IUPACName,InChI,IsomericSMILES/JSON"
)
PUBCHEM_NAME_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/"
    "MolecularFormula,MolecularWeight,IUPACName,InChI,IsomericSMILES/JSON"
)

DELAY_SECONDS = 0.25   # 4 req/s max (limite PubChem : 5/s)
OUTPUT_FILE = Path(__file__).parent / "data" / "excipients_pubchem_b3.json"

# ─────────────────────────────────────────────
# BATCH 3 — 20 excipients (IDs 40-59)
# cid_pubchem : None → recherche par nom (polymères)
# ─────────────────────────────────────────────

EXCIPIENTS_CIBLES = [
    {"id": 40, "nom_commun": "Croscarmellose sodium",        "cas_number": "74811-65-7",  "cid_pubchem": None},
    {"id": 41, "nom_commun": "Crospovidone",                 "cas_number": "9003-39-8",   "cid_pubchem": None},
    {"id": 42, "nom_commun": "Sodium starch glycolate",      "cas_number": "9063-38-1",   "cid_pubchem": None},
    {"id": 43, "nom_commun": "Gelatin",                      "cas_number": "9000-70-8",   "cid_pubchem": None},
    {"id": 44, "nom_commun": "Acacia",                       "cas_number": "9000-01-5",   "cid_pubchem": None},
    {"id": 45, "nom_commun": "Xanthan gum",                  "cas_number": "11138-66-2",  "cid_pubchem": None},
    {"id": 46, "nom_commun": "Carboxymethylcellulose sodium", "cas_number": "9004-32-4",  "cid_pubchem": None},
    {"id": 47, "nom_commun": "Ethyl cellulose",              "cas_number": "9004-57-3",   "cid_pubchem": None},
    {"id": 48, "nom_commun": "Shellac",                      "cas_number": "9000-59-3",   "cid_pubchem": None},
    {"id": 49, "nom_commun": "Carbomer",                     "cas_number": "9003-01-4",   "cid_pubchem": None},
    {"id": 50, "nom_commun": "Sodium bicarbonate",           "cas_number": "144-55-8",    "cid_pubchem": 516892},
    {"id": 51, "nom_commun": "Ascorbic acid",                "cas_number": "50-81-7",     "cid_pubchem": 5785},
    {"id": 52, "nom_commun": "Alpha-tocopherol",             "cas_number": "59-02-9",     "cid_pubchem": 14985},
    {"id": 53, "nom_commun": "Butylated hydroxytoluene",     "cas_number": "128-37-0",    "cid_pubchem": 31404},
    {"id": 54, "nom_commun": "Methylparaben",                "cas_number": "99-76-3",     "cid_pubchem": 7456},
    {"id": 55, "nom_commun": "Propylparaben",                "cas_number": "94-13-3",     "cid_pubchem": 7184},
    {"id": 56, "nom_commun": "Sorbic acid",                  "cas_number": "110-44-1",    "cid_pubchem": 643460},
    {"id": 57, "nom_commun": "Potassium sorbate",            "cas_number": "24634-61-5",  "cid_pubchem": 23676745},
    {"id": 58, "nom_commun": "Cetyl alcohol",                "cas_number": "36653-82-4",  "cid_pubchem": 2682},
    {"id": 59, "nom_commun": "Mineral oil",                  "cas_number": "8042-47-9",   "cid_pubchem": None},
]

# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def fetch_by_cid(cid: int) -> dict | None:
    url = PUBCHEM_PROPS_URL.format(cid=cid)
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            props = r.json()["PropertyTable"]["Properties"][0]
            return {
                "cid_pubchem":   props.get("CID"),
                "formule":       props.get("MolecularFormula"),
                "masse_molaire": float(props.get("MolecularWeight", 0)) or None,
                "iupac_name":    props.get("IUPACName"),
                "nom_chimique":  props.get("IUPACName"),
                "inchi":         props.get("InChI"),
                "smiles":        props.get("IsomericSMILES"),
            }
        print(f"    ⚠️  CID {cid} → HTTP {r.status_code}")
    except Exception as e:
        print(f"    ❌ Erreur CID {cid}: {e}")
    return None


def fetch_by_name(name: str) -> dict | None:
    url = PUBCHEM_NAME_URL.format(name=requests.utils.quote(name))
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            props = r.json()["PropertyTable"]["Properties"][0]
            return {
                "cid_pubchem":   props.get("CID"),
                "formule":       props.get("MolecularFormula"),
                "masse_molaire": float(props.get("MolecularWeight", 0)) or None,
                "iupac_name":    props.get("IUPACName"),
                "nom_chimique":  props.get("IUPACName"),
                "inchi":         props.get("InChI"),
                "smiles":        props.get("IsomericSMILES"),
            }
        print(f"    ⚠️  '{name}' → HTTP {r.status_code} (polymère sans données PubChem)")
    except Exception as e:
        print(f"    ❌ Erreur '{name}': {e}")
    return None


def enrich_excipient(exc: dict) -> dict:
    print(f"  [{exc['id']}] {exc['nom_commun']} ...", end=" ", flush=True)

    pubchem_data = None
    if exc["cid_pubchem"]:
        pubchem_data = fetch_by_cid(exc["cid_pubchem"])

    if not pubchem_data:
        pubchem_data = fetch_by_name(exc["nom_commun"])

    result = {**exc}

    if pubchem_data:
        result.update(pubchem_data)
        result["cid_pubchem"] = exc["cid_pubchem"] or pubchem_data.get("cid_pubchem")
        print("✅")
    else:
        result.update({
            "formule": None, "masse_molaire": None,
            "iupac_name": None, "nom_chimique": None,
            "inchi": None, "smiles": None,
        })
        print("⚠️  (données PubChem indisponibles)")

    return result


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  FETCH PUBCHEM — Batch 3 (IDs 40-59)")
    print(f"  {len(EXCIPIENTS_CIBLES)} excipients à enrichir")
    print("=" * 60)

    resultats = []
    erreurs   = []

    for i, exc in enumerate(EXCIPIENTS_CIBLES, 1):
        print(f"\n[{i}/{len(EXCIPIENTS_CIBLES)}]", end=" ")
        enrichi = enrich_excipient(exc)
        resultats.append(enrichi)
        if enrichi.get("formule") is None:
            erreurs.append(exc["nom_commun"])
        time.sleep(DELAY_SECONDS)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"  ✅ {len(resultats) - len(erreurs)}/{len(resultats)} enrichis avec succès")
    if erreurs:
        print(f"  ⚠️  Sans données PubChem : {', '.join(erreurs)}")
    print(f"  💾 Sauvegardé → {OUTPUT_FILE}")
    print("=" * 60)
    print("\n→ Étape suivante : python3 scripts/enrich_manual_b3.py")


if __name__ == "__main__":
    main()
