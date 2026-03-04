#!/usr/bin/env python3
"""
insert_supabase_b3.py — Batch 3 (IDs 40-59)
Insère / met à jour les 20 excipients du batch 3 dans la table Supabase `excipients`.
Sortie : data/insert_report_b3.json

Usage : python3 scripts/insert_supabase_b3.py
"""

import json
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

TABLE_URL    = f"{SUPABASE_URL}/rest/v1/excipients"
DELAY_INSERT = 0.15

INPUT_FILE   = Path(__file__).parent / "data" / "excipients_complets_b3.json"
REPORT_FILE  = Path(__file__).parent / "data" / "insert_report_b3.json"

COLONNES_TABLE = [
    "id", "nom_commun", "nom_chimique", "cas_number", "formule",
    "masse_molaire", "cid_pubchem", "iupac_name", "smiles", "inchi",
    "fonction_principale", "utilisation_typique", "proprietes_cles",
    "precautions", "references_pharma", "date_extraction",
]


# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def build_row(exc: dict) -> dict:
    row = {col: exc[col] for col in COLONNES_TABLE if col in exc}
    if row.get("masse_molaire") is not None:
        try:
            row["masse_molaire"] = float(row["masse_molaire"])
        except (ValueError, TypeError):
            row["masse_molaire"] = None
    return row


def upsert_one(row: dict) -> dict:
    try:
        r = requests.post(TABLE_URL, headers=HEADERS, json=[row], timeout=15)
        if r.status_code in (200, 201):
            return {"ok": True,  "status": r.status_code, "data": r.json(), "error": None}
        return {"ok": False, "status": r.status_code, "data": None, "error": r.text}
    except Exception as e:
        return {"ok": False, "status": None, "data": None, "error": str(e)}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  INSERT SUPABASE — Batch 3 (IDs 40-59)")
    print(f"  Démarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"\n❌ Fichier introuvable : {INPUT_FILE}")
        print("   Exécutez d'abord : python3 scripts/enrich_manual_b3.py")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        excipients = json.load(f)

    print(f"\n📂 {len(excipients)} excipients lus depuis {INPUT_FILE.name}")
    print(f"🔗 Cible : {TABLE_URL}\n")

    results       = []
    success_count = 0
    error_count   = 0

    for i, exc in enumerate(excipients, 1):
        nom    = exc.get("nom_commun", "?")
        exc_id = exc.get("id", "?")
        print(f"[{i:02d}/{len(excipients)}] {nom} (id={exc_id}) ...", end=" ", flush=True)

        row    = build_row(exc)
        result = upsert_one(row)

        if result["ok"]:
            success_count += 1
            print("✅")
        else:
            error_count += 1
            print(f"❌  HTTP {result['status']} — {str(result['error'])[:120]}")

        results.append({
            "id": exc_id, "nom_commun": nom,
            "ok": result["ok"], "http_status": result["status"],
            "error": result["error"],
        })
        time.sleep(DELAY_INSERT)

    rapport = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total":        len(excipients),
        "success":      success_count,
        "errors":       error_count,
        "details":      results,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"  ✅ {success_count}/{len(excipients)} insérés/mis à jour avec succès")
    if error_count:
        print(f"  ❌ {error_count} erreur(s) — voir {REPORT_FILE.name}")
        failed = [r["nom_commun"] for r in results if not r["ok"]]
        print(f"     Échecs : {', '.join(failed)}")
    print(f"  💾 Rapport → {REPORT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
