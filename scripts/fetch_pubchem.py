#!/usr/bin/env python3
"""
fetch_pubchem.py — Étape 1/3
Récupère les données chimiques depuis l'API PubChem pour les 21 nouveaux excipients.
Sortie : data/excipients_pubchem.json

Usage : python3 scripts/fetch_pubchem.py
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
OUTPUT_FILE = Path(__file__).parent / "data" / "excipients_pubchem.json"

# ─────────────────────────────────────────────
# LISTE DES 21 NOUVEAUX EXCIPIENTS
# id : continue la numérotation Supabase (18 = dernier existant)
# cid_pubchem : None → recherche par nom
# ─────────────────────────────────────────────

EXCIPIENTS_CIBLES = [
    {"id": 19, "nom_commun": "Mannitol",                 "cas_number": "69-65-8",    "cid_pubchem": 453},
    {"id": 20, "nom_commun": "Sorbitol",                 "cas_number": "50-70-4",    "cid_pubchem": 5780},
    {"id": 21, "nom_commun": "Starch",                   "cas_number": "9005-25-8",  "cid_pubchem": 24832200},
    {"id": 22, "nom_commun": "Stearic acid",             "cas_number": "57-11-4",    "cid_pubchem": 5281},
    {"id": 23, "nom_commun": "Citric acid",              "cas_number": "77-92-9",    "cid_pubchem": 311},
    {"id": 24, "nom_commun": "Sucrose",                  "cas_number": "57-50-1",    "cid_pubchem": 5988},
    {"id": 25, "nom_commun": "Propylene glycol",         "cas_number": "57-55-6",    "cid_pubchem": 1030},
    {"id": 26, "nom_commun": "Benzyl alcohol",           "cas_number": "100-51-6",   "cid_pubchem": 244},
    {"id": 27, "nom_commun": "Sodium lauryl sulfate",    "cas_number": "151-21-3",   "cid_pubchem": 3423265},
    {"id": 28, "nom_commun": "Calcium stearate",         "cas_number": "1592-23-0",  "cid_pubchem": 15985},
    {"id": 29, "nom_commun": "Dicalcium phosphate",      "cas_number": "7789-77-7",  "cid_pubchem": 24456},
    {"id": 30, "nom_commun": "Calcium carbonate",        "cas_number": "471-34-1",   "cid_pubchem": 10112},
    {"id": 31, "nom_commun": "Sodium chloride",          "cas_number": "7647-14-5",  "cid_pubchem": 5234},
    {"id": 32, "nom_commun": "Potassium chloride",       "cas_number": "7447-40-7",  "cid_pubchem": 4873},
    {"id": 33, "nom_commun": "Zinc oxide",               "cas_number": "1314-13-2",  "cid_pubchem": 14806},
    {"id": 34, "nom_commun": "Colloidal silicon dioxide","cas_number": "7631-86-9",  "cid_pubchem": 24261},
    {"id": 35, "nom_commun": "Hydroxypropyl cellulose",  "cas_number": "9004-64-2",  "cid_pubchem": None},
    {"id": 36, "nom_commun": "Hypromellose",             "cas_number": "9004-65-3",  "cid_pubchem": None},
    {"id": 37, "nom_commun": "Macrogol 4000",            "cas_number": "25322-68-3", "cid_pubchem": 87686022},
    {"id": 38, "nom_commun": "Polysorbate 80",           "cas_number": "9005-65-6",  "cid_pubchem": 5281955},
    {"id": 39, "nom_commun": "Benzalkonium chloride",    "cas_number": "8001-54-5",  "cid_pubchem": 15865},
]

# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def fetch_by_cid(cid: int) -> dict | None:
    """Appel PubChem par CID."""
    url = PUBCHEM_PROPS_URL.format(cid=cid)
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            props = r.json()["PropertyTable"]["Properties"][0]
            return {
                "cid_pubchem": props.get("CID"),
                "formule":     props.get("MolecularFormula"),
                "masse_molaire": float(props.get("MolecularWeight", 0)) or None,
                "iupac_name":  props.get("IUPACName"),
                "nom_chimique": props.get("IUPACName"),
                "inchi":       props.get("InChI"),
                "smiles":      props.get("IsomericSMILES"),
            }
        print(f"    ⚠️  CID {cid} → HTTP {r.status_code}")
    except Exception as e:
        print(f"    ❌ Erreur CID {cid}: {e}")
    return None


def fetch_by_name(name: str) -> dict | None:
    """Fallback : appel PubChem par nom commun (pour polymères sans CID stable)."""
    url = PUBCHEM_NAME_URL.format(name=requests.utils.quote(name))
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            props = r.json()["PropertyTable"]["Properties"][0]
            return {
                "cid_pubchem": props.get("CID"),
                "formule":     props.get("MolecularFormula"),
                "masse_molaire": float(props.get("MolecularWeight", 0)) or None,
                "iupac_name":  props.get("IUPACName"),
                "nom_chimique": props.get("IUPACName"),
                "inchi":       props.get("InChI"),
                "smiles":      props.get("IsomericSMILES"),
            }
        print(f"    ⚠️  '{name}' → HTTP {r.status_code} (polymère sans données PubChem)")
    except Exception as e:
        print(f"    ❌ Erreur '{name}': {e}")
    return None


def enrich_excipient(exc: dict) -> dict:
    """Récupère les données PubChem et fusionne avec les infos de base."""
    print(f"  [{exc['id']}] {exc['nom_commun']} ...", end=" ", flush=True)

    pubchem_data = None
    if exc["cid_pubchem"]:
        pubchem_data = fetch_by_cid(exc["cid_pubchem"])

    if not pubchem_data:
        # Fallback par nom pour les polymères
        pubchem_data = fetch_by_name(exc["nom_commun"])

    result = {**exc}   # copie des champs de base

    if pubchem_data:
        result.update(pubchem_data)
        # Conserver le CID original si PubChem a retourné un autre
        result["cid_pubchem"] = exc["cid_pubchem"] or pubchem_data.get("cid_pubchem")
        print("✅")
    else:
        # Données PubChem indisponibles : on garde uniquement les infos manuelles
        result.update({
            "formule": None,
            "masse_molaire": None,
            "iupac_name": None,
            "nom_chimique": None,
            "inchi": None,
            "smiles": None,
        })
        print("⚠️  (données PubChem indisponibles)")

    return result


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  FETCH PUBCHEM — ChemistrySpot")
    print(f"  {len(EXCIPIENTS_CIBLES)} excipients à enrichir")
    print("=" * 60)

    resultats = []
    erreurs = []

    for i, exc in enumerate(EXCIPIENTS_CIBLES, 1):
        print(f"\n[{i}/{len(EXCIPIENTS_CIBLES)}]", end=" ")
        enrichi = enrich_excipient(exc)
        resultats.append(enrichi)

        if enrichi.get("formule") is None:
            erreurs.append(exc["nom_commun"])

        time.sleep(DELAY_SECONDS)

    # Sauvegarde
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"  ✅ {len(resultats) - len(erreurs)}/{len(resultats)} enrichis avec succès")
    if erreurs:
        print(f"  ⚠️  Sans données PubChem : {', '.join(erreurs)}")
    print(f"  💾 Sauvegardé → {OUTPUT_FILE}")
    print("=" * 60)
    print("\n→ Étape suivante : python3 scripts/enrich_manual.py")


if __name__ == "__main__":
    main()
