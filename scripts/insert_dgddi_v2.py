#!/usr/bin/env python3
"""
insert_dgddi_v2.py — Parse DGDDI v2 CSVs and upsert into Supabase supply_chain_data.

New excipients processed:
  39129090 — Cellulose Microcristalline (MCC)      [REAL DGDDI data]
  39123100 — Croscarmellose Sodium                  [REAL DGDDI data]
  29159070 — Stéarate de Magnésium (alt code)       [REAL DGDDI data]
  39123900 — HPMC / Hypromellose                    [SYNTHETIC DGDDI_synthetic]

Only processes Import rows (excluding "Retour France").
Upsert conflict key: excipient_nom, country_iso3, year
"""

import csv
import json
import os
import urllib.request
import urllib.error
from collections import defaultdict

# ── Configuration ─────────────────────────────────────────────────────────────

SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SERVICE_ROLE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6"
    "InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3MjM0Mzk0fQ"
    ".dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0"
)

EUR_TO_USD = 1.08
BATCH_SIZE = 50

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "dgddi_raw")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ── Excipient name mapping (HS code → display name) ──────────────────────────

EXCIPIENT_MAP = {
    "39129090": "Cellulose Microcristalline",
    "39123100": "Croscarmellose Sodium",
    "29159070": "Stéarate de Magnésium",
    "39123900": "HPMC / Hypromellose",
}

# Source field: "DGDDI" for real data, "DGDDI_synthetic" for synthetic
SOURCE_MAP = {
    "39129090": "DGDDI",
    "39123100": "DGDDI",
    "29159070": "DGDDI",
    "39123900": "DGDDI_synthetic",
}

CSV_FILES = {
    "39129090": "dgddi_39129090.csv",
    "39123100": "dgddi_39123100.csv",
    "29159070": "dgddi_29159070.csv",
    "39123900": "dgddi_39123900.csv",
}

# ── Country mapping (French name → ISO3 + lat/lng) ───────────────────────────
# Extends the mapping from insert_dgddi_supabase.py with additional countries

COUNTRY_MAP = {
    # Original mapping
    "Allemagne":               ("DEU", 52.5200,   13.4050),
    "Chine":                   ("CHN", 35.8617,  104.1954),
    "Inde":                    ("IND", 20.5937,   78.9629),
    "Etats-Unis d Amérique":   ("USA", 37.0902,  -95.7129),
    "Etats-Unis d'Amérique":   ("USA", 37.0902,  -95.7129),
    "États-Unis":              ("USA", 37.0902,  -95.7129),
    "Pays-Bas":                ("NLD", 52.3676,    4.9041),
    "Royaume-Uni":             ("GBR", 55.3781,   -3.4360),
    "Belgique":                ("BEL", 50.8503,    4.3517),
    "Italie":                  ("ITA", 41.8719,   12.5674),
    "Danemark":                ("DNK", 56.2639,    9.5018),
    "Nouvelle-Zélande":        ("NZL", -40.9006, 174.8860),
    "Autriche":                ("AUT", 47.5162,   14.5501),
    "Irlande":                 ("IRL", 53.1424,   -7.6921),
    "Japon":                   ("JPN", 36.2048,  138.2529),
    "Suède":                   ("SWE", 60.1282,   18.6435),
    "Finlande":                ("FIN", 61.9241,   25.7482),
    "Pologne":                 ("POL", 51.9194,   19.1451),
    "Espagne":                 ("ESP", 40.4637,   -3.7492),
    "République tchèque":      ("CZE", 49.8175,   15.4730),
    "Turquie":                 ("TUR", 38.9637,   35.2433),
    "Malte":                   ("MLT", 35.9375,   14.3754),
    "Suisse":                  ("CHE", 46.8182,    8.2275),
    "Canada":                  ("CAN", 56.1304, -106.3468),
    "Brésil":                  ("BRA", -14.2350,  -51.9253),
    # New countries for v2
    "Taïwan":                  ("TWN",  23.6978,  120.9605),
    "Corée du Sud":            ("KOR",  35.9078,  127.7669),
    "Thaïlande":               ("THA",  15.8700,  100.9925),
    "Singapour":               ("SGP",   1.3521,  103.8198),
    # Additional countries appearing in 39123100 / 29159070 raw data
    "Hongrie":                 ("HUN",  47.1625,   19.5033),
    "Portugal":                ("PRT",  39.3999,   -8.2245),
    "Algérie":                 ("DZA",  28.0339,    1.6596),
    "Maroc":                   ("MAR",  31.7917,   -7.0926),
    "Mexique":                 ("MEX",  23.6345,  -102.5528),
    "Roumanie":                ("ROU",  45.9432,   24.9668),
    "Slovaquie":               ("SVK",  48.6690,   19.6990),
    "Slovénie":                ("SVN",  46.1512,   14.9955),
    "Croatie":                 ("HRV",  45.1000,   15.2000),
    "Bulgarie":                ("BGR",  42.7339,   25.4858),
    "Lituanie":                ("LTU",  55.1694,   23.8813),
    "Lettonie":                ("LVA",  56.8796,   24.6032),
    "Estonie":                 ("EST",  58.5953,   25.0136),
    "Finlande":                ("FIN",  61.9241,   25.7482),
    "Grèce":                   ("GRC",  39.0742,   21.8243),
    "Chypre":                  ("CYP",  35.1264,   33.4299),
    "Luxembourg":              ("LUX",  49.8153,    6.1296),
    "Israël":                  ("ISR",  31.0461,   34.8516),
    "Arabie saoudite":         ("SAU",  23.8859,   45.0792),
    "Émirats arabes unis":     ("ARE",  23.4241,   53.8478),
    "Russie":                  ("RUS",  61.5240,  105.3188),
    "Ukraine":                 ("UKR",  48.3794,   31.1656),
    "Norvège":                 ("NOR",  60.4720,    8.4689),
    "Serbie":                  ("SRB",  44.0165,   21.0059),
    "Australie":               ("AUS", -25.2744,  133.7751),
    "Argentine":               ("ARG", -38.4161,  -63.6167),
    "Colombie":                ("COL",   4.5709,  -74.2973),
    "Afrique du Sud":          ("ZAF", -30.5595,   22.9375),
    "Malaisie":                ("MYS",   4.2105,  101.9758),
    "Malaysie":                ("MYS",   4.2105,  101.9758),
    "Indonésie":               ("IDN",  -0.7893,  113.9213),
    "Pakistan":                ("PAK",  30.3753,   69.3451),
    "Bangladesh":              ("BGD",  23.6850,   90.3563),
    "Sri Lanka":               ("LKA",   7.8731,   80.7718),
    "Vietnam":                 ("VNM",  14.0583,  108.2772),
    "Philippines":             ("PHL",  12.8797,  121.7740),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_float(s):
    """Parse a float from a string, returning 0.0 on failure."""
    try:
        return float(s.strip().replace(",", "."))
    except (ValueError, AttributeError):
        return 0.0


def supabase_upsert(rows):
    """
    POST a list of row dicts to Supabase supply_chain_data with upsert semantics.
    Returns (success_count, error_message_or_None).
    """
    url = f"{SUPABASE_URL}/rest/v1/supply_chain_data?on_conflict=excipient_nom,country_iso3,year"
    payload = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            if body.strip():
                try:
                    inserted = json.loads(body)
                    return len(inserted), None
                except json.JSONDecodeError:
                    pass
            return len(rows), None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return 0, f"HTTP {e.code}: {body[:300]}"
    except urllib.error.URLError as e:
        return 0, f"URLError: {e.reason}"


# ── Main processing ───────────────────────────────────────────────────────────

def process_csv(hs_code, filename):
    """
    Read one CSV file, filter Import rows (excluding Retour France),
    group by (excipient_nom, country_iso3, year).
    Returns (list of raw row dicts, list of skipped country names).
    """
    excipient_nom = EXCIPIENT_MAP[hs_code]
    source = SOURCE_MAP[hs_code]
    filepath = os.path.join(RAW_DIR, filename)
    rows = []
    skipped_countries = []

    if not os.path.exists(filepath):
        print(f"  [WARN] CSV not found: {filepath}")
        return rows, skipped_countries

    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            flux = line.get("Flux", "").strip()
            if flux != "Import":
                continue
            pays = line.get("Pays partenaire", "").strip()
            if pays == "Retour France":
                continue

            if pays not in COUNTRY_MAP:
                skipped_countries.append(pays)
                continue

            iso3, lat, lng = COUNTRY_MAP[pays]
            year = int(line.get("Année", "2023").strip())
            valeur_keur = parse_float(line.get("Valeur (kEUR)", "0"))
            masse_tonnes = parse_float(line.get("Masse nette (tonnes)", "0"))

            rows.append({
                "excipient_nom": excipient_nom,
                "hs_code": hs_code,
                "country_iso3": iso3,
                "country_name": pays,
                "lat": lat,
                "lng": lng,
                "_value_keur": valeur_keur,
                "_masse_tonnes": masse_tonnes,
                "year": year,
                "_source": source,
            })

    return rows, skipped_countries


def compute_and_build_rows(raw_rows):
    """
    For each (excipient_nom, year) group:
      - aggregate multiple rows sharing (excipient_nom, country_iso3, year)
      - compute market_share_pct
      - compute rank_in_excipient
      - convert to final Supabase row format
    """
    # Aggregate by (excipient_nom, country_iso3, year)
    agg = defaultdict(lambda: {"value_keur": 0.0, "masse_tonnes": 0.0, "meta": None})
    for r in raw_rows:
        key = (r["excipient_nom"], r["country_iso3"], r["year"])
        agg[key]["value_keur"] += r["_value_keur"]
        agg[key]["masse_tonnes"] += r["_masse_tonnes"]
        if agg[key]["meta"] is None:
            agg[key]["meta"] = {
                "excipient_nom": r["excipient_nom"],
                "hs_code": r["hs_code"],
                "country_iso3": r["country_iso3"],
                "country_name": r["country_name"],
                "lat": r["lat"],
                "lng": r["lng"],
                "source": r["_source"],
            }

    # Group totals by (excipient_nom, year)
    group_totals = defaultdict(float)
    for (exc_nom, iso3, year), data in agg.items():
        group_totals[(exc_nom, year)] += data["value_keur"]

    # Build per-group ranked lists
    group_rows = defaultdict(list)
    for key in sorted(agg.keys()):
        exc_nom, iso3, year = key
        group_rows[(exc_nom, year)].append(key)

    final_rows = []
    for (exc_nom, year), keys in group_rows.items():
        keys_sorted = sorted(keys, key=lambda k: agg[k]["value_keur"], reverse=True)
        total_value = group_totals[(exc_nom, year)]

        for rank, key in enumerate(keys_sorted, start=1):
            data = agg[key]
            meta = data["meta"]
            value_keur = data["value_keur"]
            masse_tonnes = data["masse_tonnes"]

            export_value_usd = round(value_keur * 1000 * EUR_TO_USD)
            export_qty_kg = round(masse_tonnes * 1000)
            market_share_pct = round((value_keur / total_value * 100), 2) if total_value > 0 else 0.0

            final_rows.append({
                "excipient_nom": meta["excipient_nom"],
                "hs_code": meta["hs_code"],
                "country_iso3": meta["country_iso3"],
                "country_name": meta["country_name"],
                "lat": meta["lat"],
                "lng": meta["lng"],
                "export_value_usd": export_value_usd,
                "export_qty_kg": export_qty_kg,
                "market_share_pct": market_share_pct,
                "rank_in_excipient": rank,
                "year": year,
                "source": meta["source"],
            })

    return final_rows


def batch_upsert(rows):
    """Send rows in batches of BATCH_SIZE. Returns (total_inserted, errors)."""
    total_inserted = 0
    errors = []
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i: i + BATCH_SIZE]
        count, err = supabase_upsert(batch)
        if err:
            errors.append(f"Batch {i // BATCH_SIZE + 1}: {err}")
            print(f"  [ERR] Batch {i // BATCH_SIZE + 1}: {err}")
        else:
            total_inserted += count
            print(f"  [OK]  Batch {i // BATCH_SIZE + 1}: {count} rows upserted")
    return total_inserted, errors


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    all_raw = []
    all_skipped = {}
    per_excipient_raw = {}

    print("=== DGDDI v2 → Supabase supply_chain_data ===\n")
    print("Excipients: MCC (39129090), Croscarmellose (39123100),")
    print("            Stéarate de Magnésium (29159070), HPMC (39123900 synthetic)\n")

    # Step 1: Parse all CSVs
    for hs_code, filename in CSV_FILES.items():
        raw, skipped = process_csv(hs_code, filename)
        per_excipient_raw[hs_code] = raw
        all_raw.extend(raw)
        excipient_name = EXCIPIENT_MAP[hs_code]
        source_tag = SOURCE_MAP[hs_code]
        if skipped:
            all_skipped[hs_code] = skipped
            print(f"[{excipient_name}] Skipped {len(skipped)} unknown countries: {set(skipped)}")
        print(f"[{excipient_name}] {len(raw)} import rows parsed [{source_tag}]")

    # Step 2: Compute market shares, ranks, convert currencies
    final_rows = compute_and_build_rows(all_raw)

    # Step 3: Group by excipient for reporting
    by_excipient = defaultdict(list)
    for row in final_rows:
        by_excipient[(row["excipient_nom"], row["year"])].append(row)

    print(f"\nTotal rows to upsert: {len(final_rows)}")
    for (exc_nom, year), rows in sorted(by_excipient.items()):
        print(f"  {exc_nom} ({year}): {len(rows)} import partners")

    print("\n--- Upserting to Supabase ---\n")

    # Step 4: Upsert
    total_inserted, all_errors = batch_upsert(final_rows)

    # Step 5: Summary per excipient
    report = {
        "total_rows_upserted": total_inserted,
        "errors": all_errors,
        "per_excipient": {},
        "nc8_validity": {
            "39123900": "INVALID (HTTP 500) — HPMC synthetic",
            "39123100": "VALID (302 redirect) — Croscarmellose real data",
            "29159040": "INVALID (HTTP 500) — alt Mag Stearate",
            "29159070": "VALID (302 redirect) — Mag Stearate real data",
            "39129090": "VALID (existing download) — MCC/Cellulose NOS",
        },
    }

    print(f"\n=== Results ===")
    print(f"Total rows upserted: {total_inserted}")

    for (exc_nom, year), rows in sorted(by_excipient.items()):
        total_val_usd = sum(r["export_value_usd"] for r in rows)
        top3 = rows[:3]  # already sorted by rank
        top3_str = ", ".join(
            f"{r['country_name']} ({r['market_share_pct']}%)" for r in top3
        )
        key = f"{exc_nom}_{year}"
        report["per_excipient"][key] = {
            "excipient_nom": exc_nom,
            "year": year,
            "rows": len(rows),
            "source": rows[0]["source"] if rows else "unknown",
            "total_import_value_usd": total_val_usd,
            "top_partners": [
                {
                    "country": r["country_name"],
                    "iso3": r["country_iso3"],
                    "value_usd": r["export_value_usd"],
                    "market_share_pct": r["market_share_pct"],
                    "rank": r["rank_in_excipient"],
                }
                for r in rows
            ],
        }
        print(f"\n  {exc_nom} ({year}) [{rows[0]['source'] if rows else 'N/A'}]:")
        print(f"    Partners: {len(rows)}")
        print(f"    Total import value: ${total_val_usd:,}")
        print(f"    Top partners: {top3_str}")

    if all_skipped:
        report["skipped_countries"] = {EXCIPIENT_MAP[k]: list(set(v)) for k, v in all_skipped.items()}
        print(f"\nSkipped countries (not in mapping):")
        for hs, countries in all_skipped.items():
            print(f"  {EXCIPIENT_MAP[hs]}: {set(countries)}")

    if all_errors:
        print(f"\nErrors:")
        for err in all_errors:
            print(f"  {err}")

    # Step 6: Save report
    report_path = os.path.join(DATA_DIR, "dgddi_insert_report_v2.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport saved to: {report_path}")

    # Also update the main report to reflect all excipients
    main_report_path = os.path.join(DATA_DIR, "dgddi_insert_report.json")
    if os.path.exists(main_report_path):
        with open(main_report_path, encoding="utf-8") as f:
            main_report = json.load(f)
        main_report["per_excipient"].update(report["per_excipient"])
        main_report["total_rows_upserted"] = (
            main_report.get("total_rows_upserted", 0) + total_inserted
        )
        with open(main_report_path, "w", encoding="utf-8") as f:
            json.dump(main_report, f, ensure_ascii=False, indent=2)
        print(f"Updated main report: {main_report_path}")


if __name__ == "__main__":
    main()
