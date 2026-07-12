#!/usr/bin/env python3
"""
ChemistrySpot — Insertion des grades produits (Phase B).
Upsert de scripts/data/product_grades_seed.json dans la table product_grades.

Prérequis : la table doit exister (scripts/create_product_grades.sql
à exécuter dans le Dashboard Supabase > SQL Editor).

Usage :
    SUPABASE_SERVICE_KEY='eyJ...' python3 scripts/insert_product_grades.py [--excipient-id N]

La clé service_role est lue depuis l'environnement (ne pas la committer :
le repo est public).
"""
import json
import os
import sys
import urllib.request
import urllib.error

SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SEED_PATH = os.path.join(os.path.dirname(__file__), "data", "product_grades_seed.json")


def main():
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not key:
        sys.exit("Erreur : variable d'environnement SUPABASE_SERVICE_KEY manquante.")

    only_id = None
    if "--excipient-id" in sys.argv:
        only_id = int(sys.argv[sys.argv.index("--excipient-id") + 1])

    with open(SEED_PATH, encoding="utf-8") as f:
        grades = json.load(f)["grades"]

    if only_id is not None:
        grades = [g for g in grades if g["excipient_id"] == only_id]

    if not grades:
        sys.exit("Aucun grade à insérer (filtre trop restrictif ?).")

    # Upsert groupé : la contrainte UNIQUE (excipient_id, grade_name)
    # rend le script idempotent.
    url = (f"{SUPABASE_URL}/rest/v1/product_grades"
           f"?on_conflict=excipient_id,grade_name")
    req = urllib.request.Request(
        url,
        data=json.dumps(grades).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"HTTP {resp.status} — {len(grades)} grades upsertés"
                  f" ({len({g['excipient_id'] for g in grades})} excipients)")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} : {e.read().decode('utf-8', 'replace')}")


if __name__ == "__main__":
    main()
