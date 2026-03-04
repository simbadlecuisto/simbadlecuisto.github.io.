#!/usr/bin/env python3
"""
ChemistrySpot — Insérer les prix dans Supabase (table prices)
Lit data/prices.json généré par fetch_prices_pharmacompass.py

Usage: python scripts/insert_prices_supabase.py
Prérequis: créer la table prices (scripts/create_prices_table.sql)
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────
SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3MjM0Mzk0fQ.dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0"
DATA_FILE    = "data/prices.json"

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "resolution=merge-duplicates",  # upsert
}


def upsert_prices(records: list[dict]) -> dict:
    """UPSERT en batch dans la table prices."""
    now = datetime.now(timezone.utc).isoformat()

    rows = []
    for r in records:
        rows.append({
            "excipient_id": r["excipient_id"],
            "prix_min":     r["prix_min"],
            "prix_max":     r["prix_max"],
            "devise":       r.get("devise", "EUR"),
            "source":       r.get("source", "Estimate"),
            "grade":        r.get("grade", "Pharmaceutical Grade"),
            "date_maj":     now,
        })

    payload = json.dumps(rows).encode("utf-8")
    url = f"{SUPABASE_URL}/rest/v1/prices"
    req = urllib.request.Request(url, data=payload, headers=HEADERS, method="POST")

    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode()
        return {"status": resp.status, "body": body}


def main():
    print("═" * 60)
    print("ChemistrySpot — Insert Prices → Supabase")
    print("═" * 60)

    # Charger JSON
    print(f"\n📂 Lecture {DATA_FILE}...")
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier introuvable : {DATA_FILE}")
        print("   Lancer d'abord : python scripts/fetch_prices_pharmacompass.py")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON invalide : {e}")
        return

    print(f"   → {len(records)} entrées à insérer\n")

    # Insérer en lots de 50
    BATCH_SIZE = 50
    inserted   = 0
    errors     = 0

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        try:
            result = upsert_prices(batch)
            inserted += len(batch)
            print(f"  ✅  Lot {i//BATCH_SIZE + 1} : {len(batch)} lignes (HTTP {result['status']})")
        except urllib.error.HTTPError as e:
            errors += len(batch)
            body = e.read().decode()
            print(f"  ❌  Lot {i//BATCH_SIZE + 1} : HTTP {e.code} — {body[:200]}")
        except Exception as e:
            errors += len(batch)
            print(f"  ❌  Lot {i//BATCH_SIZE + 1} : {e}")

    print("\n" + "─" * 60)
    print(f"✅  Insertions réussies : {inserted}")
    print(f"❌  Erreurs             : {errors}")
    print("─" * 60)

    if inserted > 0:
        print(f"\n🔗 Vérifier dans Supabase:")
        print(f"   SELECT COUNT(*) FROM prices;")


if __name__ == "__main__":
    main()
