#!/usr/bin/env python3
"""
ChemistrySpot — Géocodage des fournisseurs via OpenStreetMap Nominatim
Ajoute latitude/longitude à la table suppliers dans Supabase.

Usage: python3 scripts/geocode_suppliers.py
"""

import json
import time
import random
import urllib.request
import urllib.error
import urllib.parse

# ── Configuration ───────────────────────────────────────────────
SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3MjM0Mzk0fQ.dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0"

BASE_HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "ChemistrySpot/1.0 (pharmaceutical supplier geocoding, contact@chemistryspot.com)"
}

# ── Coordonnées par défaut par pays (centroïdes) ───────────────
COUNTRY_COORDS = {
    "USA":            (37.09,  -95.71),
    "China":          (35.86,  104.19),
    "Germany":        (51.16,   10.45),
    "UK":             (55.37,   -3.43),
    "France":         (46.22,    2.21),
    "Japan":          (36.20,  138.25),
    "India":          (20.59,   78.96),
    "Ukraine":        (48.37,   31.16),
    "Russia":         (61.52,  105.31),
    "Switzerland":    (46.81,    8.22),
    "Spain":          (40.46,   -3.74),
    "Belgium":        (50.50,    4.46),
    "Netherlands":    (52.13,    5.29),
    "Poland":         (51.91,   19.14),
    "Hungary":        (47.16,   19.50),
    "Latvia":         (56.87,   24.60),
    "Turkey":         (38.96,   35.24),
    "South Korea":    (35.90,  127.76),
    "Hong Kong":      (22.39,  114.10),
    "Israel":         (31.04,   34.85),
    "Greece":         (39.07,   21.82),
    "Italy":          (41.87,   12.56),
    "Austria":        (47.51,   14.55),
    "Canada":         (56.13, -106.34),
    "Australia":     (-25.27,  133.77),
    "Singapore":       (1.35,  103.81),
    "Brazil":        (-14.23,  -51.92),
    "Taiwan":         (23.69,  120.96),
    "Czech Republic": (49.81,   15.47),
    "Denmark":        (56.26,    9.50),
    "Sweden":         (60.12,   18.64),
    "Norway":         (60.47,    8.46),
    "Finland":        (61.92,   25.74),
    "Ireland":        (53.41,   -8.24),
    "Portugal":       (39.39,   -8.22),
    "Mexico":         (23.63,  -102.55),
    "Argentina":     (-38.41,  -63.61),
    "South Africa":  (-30.55,   22.93),
    "UAE":            (23.42,   53.84),
}


# ── Supabase helpers ─────────────────────────────────────────────
def supabase_get(path: str) -> tuple[int, bytes]:
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    req = urllib.request.Request(url, headers=BASE_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def check_columns_exist() -> bool:
    """Returns True if latitude/longitude columns exist in suppliers table."""
    status, body = supabase_get("suppliers?select=id,latitude,longitude&limit=1")
    if status == 400:
        msg = body.decode(errors="replace")
        if "column" in msg.lower():
            print("\n⚠️  Les colonnes latitude/longitude n'existent pas encore.")
            print("   Exécutez ce SQL dans le Supabase Dashboard (SQL Editor) :\n")
            print("   ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS latitude NUMERIC;")
            print("   ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS longitude NUMERIC;\n")
            print("   Puis relancez ce script.\n")
            return False
    return True


def fetch_all_suppliers() -> list[dict]:
    status, body = supabase_get(
        "suppliers?select=id,name,country,website,latitude,longitude&order=id&limit=500"
    )
    if status != 200:
        raise RuntimeError(f"Supabase GET error {status}: {body.decode(errors='replace')[:200]}")
    return json.loads(body.decode())


def update_supplier_coords(sid: int, lat: float, lng: float) -> bool:
    url     = f"{SUPABASE_URL}/rest/v1/suppliers?id=eq.{sid}"
    payload = json.dumps({"latitude": lat, "longitude": lng}).encode()
    hdrs    = {**BASE_HEADERS, "Prefer": "return=minimal"}
    req     = urllib.request.Request(url, data=payload, headers=hdrs, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"    ❌ PATCH id={sid}: HTTP {e.code}")
        return False


# ── Nominatim geocoder ────────────────────────────────────────────
def nominatim_geocode(query: str) -> tuple[float, float] | None:
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": "1"})
    url    = f"{NOMINATIM_URL}?{params}"
    req    = urllib.request.Request(url, headers=NOMINATIM_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            results = json.loads(r.read().decode())
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"    ⚠️  Nominatim error: {e}")
    return None


def build_query(sup: dict) -> str | None:
    """Build best geocoding query string from supplier data."""
    name    = (sup.get("name")    or "").strip()
    country = (sup.get("country") or "").strip()
    city    = (sup.get("city")    or "").strip()
    address = (sup.get("address") or "").strip()

    if address and city and country:
        return f"{address}, {city}, {country}"
    if city and country:
        return f"{city}, {country}"
    if name and country and country not in ("Unknown", ""):
        return f"{name}, {country}"
    return None


# ── Main ──────────────────────────────────────────────────────────
def main():
    print("═" * 62)
    print("ChemistrySpot — Géocodage fournisseurs (Nominatim)")
    print("═" * 62)

    # 1. Check columns
    if not check_columns_exist():
        return

    # 2. Fetch suppliers
    print("\n📦 Chargement des fournisseurs…")
    try:
        suppliers = fetch_all_suppliers()
    except Exception as e:
        print(f"❌ Erreur Supabase : {e}")
        return
    print(f"   → {len(suppliers)} fournisseurs chargés\n")

    total      = len(suppliers)
    geocoded   = 0
    skipped    = 0
    fallback   = 0
    failed     = 0
    already    = 0

    for i, sup in enumerate(suppliers, 1):
        sid     = sup["id"]
        name    = (sup.get("name") or "").strip()
        country = (sup.get("country") or "").strip()

        # Skip already geocoded
        if sup.get("latitude") is not None and sup.get("longitude") is not None:
            already += 1
            print(f"  ⏭  {i:3d}/{total}: {name[:45]:<45} → déjà géocodé")
            continue

        # Try Nominatim first
        query = build_query(sup)
        lat, lng = None, None
        method = ""

        if query:
            coords = nominatim_geocode(query)
            time.sleep(1.1 + random.random() * 0.4)  # respect rate limit
            if coords:
                lat, lng = coords
                method = "nominatim"
            else:
                # Fallback: try name+country only if we used a richer query
                if country and country not in ("Unknown", ""):
                    coords2 = nominatim_geocode(f"{name}, {country}")
                    time.sleep(1.1 + random.random() * 0.4)
                    if coords2:
                        lat, lng = coords2
                        method = "nominatim(name)"

        # Country centroid fallback
        if lat is None and country in COUNTRY_COORDS:
            lat, lng = COUNTRY_COORDS[country]
            # Add small random offset so pins don't stack exactly
            lat += (random.random() - 0.5) * 2.0
            lng += (random.random() - 0.5) * 3.0
            method = "centroid"
            fallback += 1

        if lat is None:
            skipped += 1
            print(f"  ❓ {i:3d}/{total}: {name[:45]:<45} → ignoré (pays inconnu)")
            continue

        # Update Supabase
        ok = update_supplier_coords(sid, round(lat, 5), round(lng, 5))
        if ok:
            geocoded += 1
            print(f"  ✅ {i:3d}/{total}: {name[:45]:<45} → {lat:.4f}, {lng:.4f} ({method})")
        else:
            failed += 1
            print(f"  ❌ {i:3d}/{total}: {name[:45]:<45} → PATCH échoué")

    print("\n" + "─" * 62)
    print(f"Résumé :")
    print(f"  Déjà géocodés    : {already}")
    print(f"  Nouvellement géo : {geocoded}  (dont {fallback} par centroïde)")
    print(f"  Ignorés          : {skipped}  (pays Unknown)")
    print(f"  Échecs PATCH     : {failed}")
    print(f"  Total traités    : {total}")
    print("─" * 62)


if __name__ == "__main__":
    main()
