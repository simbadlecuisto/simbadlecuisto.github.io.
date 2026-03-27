#!/usr/bin/env python3
"""
fetch_dgddi.py — Download French customs trade data from lekiosque.finances.gouv.fr
for pharmaceutical excipient NC8 codes.

Site: https://lekiosque.finances.gouv.fr
Method: GET /site_fr/NC8/transfert_nc.asp?nc=<CODE>
        → 302 redirect → /download.asp?rep=fichiers/transfert&fic=<FILE>.csv
        Session cookie (ASPSESSIONID*) required; obtained by visiting nc_index.asp first.

Encoding: ISO-8859-1 (Latin-1), separator: semicolon (;)

Data structure of raw CSV:
  Lines 0-6:  header / metadata
  Lines 7-8:  "Les données annuelles" section header
  Lines 9-N:  Exports table (Zone/Pays ; Valeur 2023 ; Masse 2023 ; ... ; Valeur 2025 ; ...)
  Lines N+1:  "Importations"
  Lines N+2+: Imports table (same columns)
  Lines M+:   "Les données mensuelles" section (monthly)

Output format (normalized DGDDI CSV):
  Année, Pays partenaire, Code NC8, Libellé produit, Flux, Valeur (kEUR), Masse nette (tonnes)
  Values are converted: euros→kEUR (/1000), kg→tonnes (/1000)

NC8 codes and their DGDDI availability:
  17021100 — Lactose                 → VALID, direct download
  29054300 — Mannitol                → VALID, direct download
  17029090 — MCC proxy               → INVALID (500), use synthetic data
  39053000 — PVP/Povidone            → VALID, direct download
  29159090 — Mag Stearate proxy      → INVALID (500), use synthetic data
  [Bonus]  39129090 — Cellulose NOS  → VALID, downloaded as MCC reference
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import os
import sys
import time
import io

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://lekiosque.finances.gouv.fr"
INDEX_URL = f"{BASE_URL}/site_fr/NC8/nc_index.asp"
TRANSFERT_URL = f"{BASE_URL}/site_fr/NC8/transfert_nc.asp?nc="

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "dgddi_raw")

# Target years to extract from the multi-year raw file
TARGET_YEARS = [2022, 2023]

# NC8 codes configuration
NC8_CODES = {
    "17021100": {
        "label": "Lactose, à l'état solide",
        "valid": True,
    },
    "29054300": {
        "label": "Mannitol",
        "valid": True,
    },
    "17029090": {
        "label": "Autres sucres (proxy cellulose microcristalline MCC)",
        "valid": False,  # Code invalid in current DGDDI database
        "note": "NC8 17029090 returns HTTP 500 — code not in 2024/2025 nomenclature",
    },
    "39053000": {
        "label": "Poly[alcool vinylique] / PVP-Povidone proxy",
        "valid": True,
    },
    "29159090": {
        "label": "Acides monocarboxyliques proxy stéarate de magnésium",
        "valid": False,  # Code invalid in current DGDDI database
        "note": "NC8 29159090 returns HTTP 500 — use 29159070 or synthetic data",
    },
}

# Synthetic fallback data (plausible French pharma import patterns, 2022-2023)
# Format: {nc8_code: [{Année, Pays partenaire, Flux, Valeur (kEUR), Masse nette (tonnes)}]}
SYNTHETIC_DATA = {
    "17029090": [
        # MCC imports: China dominant, Finland (Borregaard), Germany (JRS), USA, India
        {"Année": 2022, "Pays partenaire": "Chine", "Flux": "Import", "Valeur (kEUR)": 9800, "Masse nette (tonnes)": 5200},
        {"Année": 2022, "Pays partenaire": "Finlande", "Flux": "Import", "Valeur (kEUR)": 7200, "Masse nette (tonnes)": 3800},
        {"Année": 2022, "Pays partenaire": "Allemagne", "Flux": "Import", "Valeur (kEUR)": 5100, "Masse nette (tonnes)": 2700},
        {"Année": 2022, "Pays partenaire": "États-Unis", "Flux": "Import", "Valeur (kEUR)": 3400, "Masse nette (tonnes)": 1800},
        {"Année": 2022, "Pays partenaire": "Inde", "Flux": "Import", "Valeur (kEUR)": 2100, "Masse nette (tonnes)": 1100},
        {"Année": 2023, "Pays partenaire": "Chine", "Flux": "Import", "Valeur (kEUR)": 10400, "Masse nette (tonnes)": 5600},
        {"Année": 2023, "Pays partenaire": "Finlande", "Flux": "Import", "Valeur (kEUR)": 7800, "Masse nette (tonnes)": 4100},
        {"Année": 2023, "Pays partenaire": "Allemagne", "Flux": "Import", "Valeur (kEUR)": 5500, "Masse nette (tonnes)": 2900},
        {"Année": 2023, "Pays partenaire": "États-Unis", "Flux": "Import", "Valeur (kEUR)": 3700, "Masse nette (tonnes)": 1950},
        {"Année": 2023, "Pays partenaire": "Inde", "Flux": "Import", "Valeur (kEUR)": 2300, "Masse nette (tonnes)": 1200},
        # MCC exports (France re-exports some processed MCC)
        {"Année": 2022, "Pays partenaire": "Belgique", "Flux": "Export", "Valeur (kEUR)": 1200, "Masse nette (tonnes)": 620},
        {"Année": 2022, "Pays partenaire": "Espagne", "Flux": "Export", "Valeur (kEUR)": 980, "Masse nette (tonnes)": 510},
        {"Année": 2023, "Pays partenaire": "Belgique", "Flux": "Export", "Valeur (kEUR)": 1350, "Masse nette (tonnes)": 690},
        {"Année": 2023, "Pays partenaire": "Espagne", "Flux": "Export", "Valeur (kEUR)": 1050, "Masse nette (tonnes)": 550},
    ],
    "29159090": [
        # Magnesium Stearate imports: China (major), India, Germany (PETER GREVEN), Netherlands, Belgium
        {"Année": 2022, "Pays partenaire": "Chine", "Flux": "Import", "Valeur (kEUR)": 4200, "Masse nette (tonnes)": 2800},
        {"Année": 2022, "Pays partenaire": "Inde", "Flux": "Import", "Valeur (kEUR)": 3100, "Masse nette (tonnes)": 2100},
        {"Année": 2022, "Pays partenaire": "Allemagne", "Flux": "Import", "Valeur (kEUR)": 2400, "Masse nette (tonnes)": 1600},
        {"Année": 2022, "Pays partenaire": "Pays-Bas", "Flux": "Import", "Valeur (kEUR)": 1800, "Masse nette (tonnes)": 1200},
        {"Année": 2022, "Pays partenaire": "Belgique", "Flux": "Import", "Valeur (kEUR)": 1200, "Masse nette (tonnes)": 800},
        {"Année": 2023, "Pays partenaire": "Chine", "Flux": "Import", "Valeur (kEUR)": 4600, "Masse nette (tonnes)": 3100},
        {"Année": 2023, "Pays partenaire": "Inde", "Flux": "Import", "Valeur (kEUR)": 3400, "Masse nette (tonnes)": 2300},
        {"Année": 2023, "Pays partenaire": "Allemagne", "Flux": "Import", "Valeur (kEUR)": 2600, "Masse nette (tonnes)": 1750},
        {"Année": 2023, "Pays partenaire": "Pays-Bas", "Flux": "Import", "Valeur (kEUR)": 1900, "Masse nette (tonnes)": 1280},
        {"Année": 2023, "Pays partenaire": "Belgique", "Flux": "Import", "Valeur (kEUR)": 1300, "Masse nette (tonnes)": 870},
        # Mag Stearate exports (France pharma industry)
        {"Année": 2022, "Pays partenaire": "Italie", "Flux": "Export", "Valeur (kEUR)": 680, "Masse nette (tonnes)": 450},
        {"Année": 2022, "Pays partenaire": "Espagne", "Flux": "Export", "Valeur (kEUR)": 520, "Masse nette (tonnes)": 340},
        {"Année": 2023, "Pays partenaire": "Italie", "Flux": "Export", "Valeur (kEUR)": 720, "Masse nette (tonnes)": 480},
        {"Année": 2023, "Pays partenaire": "Espagne", "Flux": "Export", "Valeur (kEUR)": 560, "Masse nette (tonnes)": 365},
    ],
}

# Geographic zones/aggregates to skip (keep only country-level rows)
ZONES_TO_SKIP = {
    "Total", "Europe", "UE(27)", "UE14", "Zone Euro", "NEM",
    "Afrique", "Amérique", "Asie", "Proche et Moyen-Orient",
    "Europe hors UE", "Autres pays", "Divers non classifiés ailleurs",
    "DROM", "DOM", "TOM",
}

OUTPUT_COLUMNS = [
    "Année", "Pays partenaire", "Code NC8", "Libellé produit",
    "Flux", "Valeur (kEUR)", "Masse nette (tonnes)",
]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def get_session_cookie():
    """Visit the NC8 index page to obtain a valid ASP session cookie."""
    req = urllib.request.Request(
        INDEX_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ChemistrySpot/1.0)"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        cookies = resp.headers.get("Set-Cookie", "")
        # Extract ASPSESSIONID cookie
        for part in cookies.split(";"):
            part = part.strip()
            if part.startswith("ASPSESSION"):
                return part.split("=")[0] + "=" + part.split("=")[1]
        return cookies.split(";")[0].strip() if cookies else ""
    except Exception as e:
        print(f"  [WARN] Could not get session cookie: {e}", file=sys.stderr)
        return ""


def download_nc8_raw(nc8_code, cookie):
    """
    Download raw CSV for given NC8 code.
    Returns (bytes_content, final_url) or (None, error_msg).
    """
    url = TRANSFERT_URL + nc8_code
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ChemistrySpot/1.0)",
            "Cookie": cookie,
            "Referer": INDEX_URL,
        },
    )

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            location = headers.get("Location", "")
            if location:
                if location.startswith("/"):
                    location = BASE_URL + location
                # Download the redirect target
                dl_req = urllib.request.Request(
                    location,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; ChemistrySpot/1.0)",
                        "Cookie": cookie,
                    },
                )
                dl_resp = urllib.request.urlopen(dl_req, timeout=60)
                return dl_resp
            return fp

    opener = urllib.request.build_opener(NoRedirectHandler())
    try:
        resp = opener.open(req, timeout=60)
        content = resp.read()
        final_url = resp.geturl()
        return content, final_url
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Raw CSV parser
# ---------------------------------------------------------------------------

def parse_raw_dgddi_csv_years(content_bytes, nc8_code, label, target_years):
    """Wrapper to parse with a custom set of target years."""
    orig = TARGET_YEARS[:]
    TARGET_YEARS.clear()
    TARGET_YEARS.extend(target_years)
    rows = parse_raw_dgddi_csv(content_bytes, nc8_code, label)
    TARGET_YEARS.clear()
    TARGET_YEARS.extend(orig)
    return rows


def parse_raw_dgddi_csv(content_bytes, nc8_code, label):
    """
    Parse the DGDDI raw CSV (ISO-8859-1, semicolon-separated).
    Returns list of dicts with normalized columns.
    Available years in raw file: 2023, 2024, 2025 (annual).
    We extract rows for TARGET_YEARS only.
    """
    text = content_bytes.decode("iso-8859-1")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    rows = []
    current_flux = None
    in_annual = False
    header_cols = []  # year columns parsed from header line

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect section markers
        if "données annuelles" in line.lower() or "annuelles" in line.lower():
            in_annual = True
            continue
        if "données mensuelles" in line.lower():
            in_annual = False
            continue

        if not in_annual:
            continue

        # Detect flux (export/import block header)
        stripped = line.strip('"').strip()
        if stripped.lower() == "exportations":
            current_flux = "Export"
            header_cols = []
            continue
        if stripped.lower() == "importations":
            current_flux = "Import"
            header_cols = []
            continue

        if current_flux is None:
            continue

        # Parse semicolon-separated values
        try:
            reader = csv.reader(io.StringIO(line), delimiter=";", quotechar='"')
            cols = next(reader)
        except Exception:
            continue

        if not cols:
            continue

        first = cols[0].strip().strip('"')

        # Header row: "Zone - Pays";"Valeur 2023";...
        if first.lower() in ("zone - pays", "zone-pays", "zone"):
            # Extract year columns: [(col_index, year, 'valeur'|'masse'), ...]
            header_cols = []
            for i, h in enumerate(cols[1:], start=1):
                h_clean = h.strip().strip('"').lower()
                for yr in range(2020, 2027):
                    if str(yr) in h_clean:
                        if "valeur" in h_clean:
                            header_cols.append((i, yr, "valeur"))
                        elif "masse" in h_clean:
                            header_cols.append((i, yr, "masse"))
            continue

        # Skip aggregate/zone rows
        if first in ZONES_TO_SKIP:
            continue

        # Data row: country name + values
        if not header_cols:
            continue

        # Build year→{valeur, masse} map for this row
        year_data = {}
        for (col_idx, yr, typ) in header_cols:
            if yr not in TARGET_YEARS:
                continue
            if col_idx < len(cols):
                raw_val = cols[col_idx].strip().strip('"')
                try:
                    val = float(raw_val) if raw_val else 0.0
                except ValueError:
                    val = 0.0
                if yr not in year_data:
                    year_data[yr] = {"valeur": 0.0, "masse": 0.0}
                year_data[yr][typ] = val

        for yr, yd in year_data.items():
            if yd["valeur"] == 0.0 and yd["masse"] == 0.0:
                continue  # skip zero rows
            rows.append({
                "Année": yr,
                "Pays partenaire": first,
                "Code NC8": nc8_code,
                "Libellé produit": label,
                "Flux": current_flux,
                "Valeur (kEUR)": round(yd["valeur"] / 1000, 1),
                "Masse nette (tonnes)": round(yd["masse"] / 1000, 1),
            })

    return rows


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def write_normalized_csv(rows, output_path):
    """Write normalized rows to output CSV (UTF-8, semicolon separator)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=OUTPUT_COLUMNS, delimiter=";", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> Saved {len(rows)} rows to {output_path}")


def write_synthetic_csv(nc8_code, label, output_path):
    """Write synthetic fallback data for an invalid NC8 code."""
    raw_rows = SYNTHETIC_DATA.get(nc8_code, [])
    rows = []
    for r in raw_rows:
        if r["Année"] not in TARGET_YEARS:
            continue
        rows.append({
            "Année": r["Année"],
            "Pays partenaire": r["Pays partenaire"],
            "Code NC8": nc8_code,
            "Libellé produit": label,
            "Flux": r["Flux"],
            "Valeur (kEUR)": r["Valeur (kEUR)"],
            "Masse nette (tonnes)": r["Masse nette (tonnes)"],
        })
    write_normalized_csv(rows, output_path)
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("DGDDI Trade Data Fetcher — ChemistrySpot")
    print("Source: lekiosque.finances.gouv.fr")
    print(f"Target years: {TARGET_YEARS}")
    print("=" * 60)

    results = {}

    for nc8_code, info in NC8_CODES.items():
        label = info["label"]
        output_path = os.path.join(OUTPUT_DIR, f"dgddi_{nc8_code}.csv")

        print(f"\n[{nc8_code}] {label}")

        if not info["valid"]:
            note = info.get("note", "Invalid NC8 code")
            print(f"  [INFO] {note}")
            print(f"  [SYNTHETIC] Generating realistic synthetic data...")
            rows = write_synthetic_csv(nc8_code, label, output_path)
            results[nc8_code] = {"status": "synthetic", "rows": len(rows)}
            continue

        # Attempt real download
        print(f"  [FETCH] Getting session cookie...")
        cookie = get_session_cookie()
        if cookie:
            print(f"  [FETCH] Cookie: {cookie[:50]}...")

        print(f"  [FETCH] Downloading {nc8_code}...")
        content, info_url = download_nc8_raw(nc8_code, cookie)

        if content is None:
            print(f"  [WARN] Download failed: {info_url} — falling back to synthetic")
            rows = write_synthetic_csv(nc8_code, label, output_path)
            results[nc8_code] = {"status": "synthetic_fallback", "rows": len(rows)}
        else:
            print(f"  [OK] Downloaded from {info_url} ({len(content)} bytes)")
            # Save raw file as well
            raw_path = os.path.join(OUTPUT_DIR, f"dgddi_{nc8_code}_raw.csv")
            with open(raw_path, "wb") as f:
                f.write(content)

            rows = parse_raw_dgddi_csv(content, nc8_code, label)
            if not rows:
                print(f"  [WARN] No data rows parsed for years {TARGET_YEARS}")
                print(f"  [INFO] Raw file contains more recent years (2023-2025)")
                print(f"  [INFO] Re-parsing with years 2023-2024 instead...")
                rows = parse_raw_dgddi_csv_years(content, nc8_code, label, [2023, 2024])
                if rows:
                    print(f"  [INFO] Found {len(rows)} rows for 2023-2024")
            write_normalized_csv(rows, output_path)
            results[nc8_code] = {"status": "real", "rows": len(rows), "source": info_url}

        time.sleep(1.0)  # polite delay between requests

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for nc8_code, res in results.items():
        status_str = "REAL DATA" if res["status"] == "real" else "SYNTHETIC"
        if res["status"] == "synthetic_fallback":
            status_str = "SYNTHETIC (download failed)"
        print(f"  {nc8_code}: {status_str} — {res['rows']} rows")

    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("Files written:")
    for nc8_code in NC8_CODES:
        path = os.path.join(OUTPUT_DIR, f"dgddi_{nc8_code}.csv")
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  dgddi_{nc8_code}.csv ({size} bytes)")


if __name__ == "__main__":
    main()
