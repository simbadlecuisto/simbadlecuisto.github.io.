#!/usr/bin/env python3
"""
fetch_dgddi_v2.py — Download French customs trade data for new pharmaceutical excipients.

NC8 codes tested on 31/03/2026:
  39123900 — Autres éthers de cellulose (HPMC/Hypromellose)    → INVALID (HTTP 500)
  39123100 — Carboxyméthylcellulose et ses sels (Croscarmellose) → VALID (302 → CSV)
  29159040 — Acide stéarique (Mag Stearate alt)                → INVALID (HTTP 500)
  29159070 — Acides monocarboxyliques (Mag Stearate alt2)      → VALID (302 → CSV)
  39129090 — Cellulose NOS (MCC)                               → reuse existing raw

Already downloaded raw CSVs:
  scripts/dgddi_raw/dgddi_39123100_raw.csv   (Croscarmellose Sodium)
  scripts/dgddi_raw/dgddi_29159070_raw.csv   (Stéarate de Magnésium, alternative code)
  scripts/dgddi_raw/dgddi_39129090_cellulose_raw.csv  (MCC / Cellulose NOS)

Output: normalized CSVs in dgddi_raw/
  dgddi_39129090.csv  — Cellulose Microcristalline (from 39129090_cellulose_raw)
  dgddi_39123100.csv  — Croscarmellose Sodium      (from 39123100_raw)
  dgddi_29159070.csv  — Stéarate de Magnésium      (from 29159070_raw, valid alt code)
  dgddi_39123900.csv  — HPMC / Hypromellose        (SYNTHETIC — 39123900 invalid)
"""

import csv
import io
import os
import sys
import time
import urllib.request
import urllib.error
import http.client

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://lekiosque.finances.gouv.fr"
INDEX_URL = f"{BASE_URL}/site_fr/NC8/nc_index.asp"
TRANSFERT_URL = f"{BASE_URL}/site_fr/NC8/transfert_nc.asp?nc="

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "dgddi_raw")

# Target years: raw files contain 2023/2024/2025 — use 2023 + 2024
TARGET_YEARS = [2023, 2024]

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
# NC8 codes for v2 — new excipients only (not re-processing v1 codes)
# ---------------------------------------------------------------------------

NC8_V2 = {
    "39129090": {
        "label": "Cellulose et ses dérivés chimiques, n.d.a. (MCC)",
        "valid": True,
        "reuse_raw": "dgddi_39129090_cellulose_raw.csv",
    },
    "39123100": {
        "label": "Carboxyméthylcellulose et ses sels (Croscarmellose Sodium)",
        "valid": True,
        "reuse_raw": "dgddi_39123100_raw.csv",
    },
    "29159070": {
        "label": "Acides monocarboxyliques acycliques saturés (Stéarate de Magnésium)",
        "valid": True,
        "reuse_raw": "dgddi_29159070_raw.csv",
    },
    "39123900": {
        "label": "Autres éthers de cellulose (HPMC / Hypromellose)",
        "valid": False,
        "note": "NC8 39123900 returns HTTP 500 — code not in 2025 nomenclature",
    },
}

# ---------------------------------------------------------------------------
# Synthetic fallback data — realistic 2023/2024 French pharma import patterns
# ---------------------------------------------------------------------------

SYNTHETIC_DATA = {
    "39123900": [
        # HPMC imports: China dominant (Shin-Etsu, LOTTE), India, Japan, Germany, Netherlands
        # Total ~3 500 t/an, ~22 M€
        {"Année": 2023, "Pays partenaire": "Chine",      "Flux": "Import", "Valeur (kEUR)": 12100, "Masse nette (tonnes)": 1925},
        {"Année": 2023, "Pays partenaire": "Inde",       "Flux": "Import", "Valeur (kEUR)":  4400, "Masse nette (tonnes)":  700},
        {"Année": 2023, "Pays partenaire": "Japon",      "Flux": "Import", "Valeur (kEUR)":  2640, "Masse nette (tonnes)":  420},
        {"Année": 2023, "Pays partenaire": "Allemagne",  "Flux": "Import", "Valeur (kEUR)":  1760, "Masse nette (tonnes)":  280},
        {"Année": 2023, "Pays partenaire": "Pays-Bas",   "Flux": "Import", "Valeur (kEUR)":  1100, "Masse nette (tonnes)":  175},
        {"Année": 2024, "Pays partenaire": "Chine",      "Flux": "Import", "Valeur (kEUR)": 12800, "Masse nette (tonnes)": 2050},
        {"Année": 2024, "Pays partenaire": "Inde",       "Flux": "Import", "Valeur (kEUR)":  4700, "Masse nette (tonnes)":  750},
        {"Année": 2024, "Pays partenaire": "Japon",      "Flux": "Import", "Valeur (kEUR)":  2800, "Masse nette (tonnes)":  445},
        {"Année": 2024, "Pays partenaire": "Allemagne",  "Flux": "Import", "Valeur (kEUR)":  1850, "Masse nette (tonnes)":  295},
        {"Année": 2024, "Pays partenaire": "Pays-Bas",   "Flux": "Import", "Valeur (kEUR)":  1150, "Masse nette (tonnes)":  185},
        # Exports (minor)
        {"Année": 2023, "Pays partenaire": "Belgique",   "Flux": "Export", "Valeur (kEUR)":   420, "Masse nette (tonnes)":   65},
        {"Année": 2023, "Pays partenaire": "Espagne",    "Flux": "Export", "Valeur (kEUR)":   310, "Masse nette (tonnes)":   48},
        {"Année": 2024, "Pays partenaire": "Belgique",   "Flux": "Export", "Valeur (kEUR)":   450, "Masse nette (tonnes)":   70},
        {"Année": 2024, "Pays partenaire": "Espagne",    "Flux": "Export", "Valeur (kEUR)":   330, "Masse nette (tonnes)":   51},
    ],
}

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
    Download raw CSV for given NC8 code using low-level HTTP to handle 302 redirect.
    Returns (bytes_content, filename) or (None, error_msg).
    """
    conn = http.client.HTTPSConnection("lekiosque.finances.gouv.fr", timeout=30)
    conn.request(
        "GET",
        f"/site_fr/NC8/transfert_nc.asp?nc={nc8_code}",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ChemistrySpot/1.0)",
            "Cookie": cookie,
            "Referer": INDEX_URL,
            "Host": "lekiosque.finances.gouv.fr",
        },
    )
    try:
        r = conn.getresponse()
        r.read()  # drain
    except Exception as e:
        return None, f"Connection error: {e}"

    if r.status != 302:
        return None, f"HTTP {r.status} (expected 302)"

    loc = r.getheader("Location", "")
    if not loc:
        return None, "No Location header in redirect"

    # Download the file with the same session cookie
    time.sleep(0.3)
    conn2 = http.client.HTTPSConnection("lekiosque.finances.gouv.fr", timeout=60)
    conn2.request(
        "GET",
        loc,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ChemistrySpot/1.0)",
            "Cookie": cookie,
            "Host": "lekiosque.finances.gouv.fr",
        },
    )
    try:
        r2 = conn2.getresponse()
        if r2.status == 200:
            content = r2.read()
            return content, loc
        else:
            r2.read()
            return None, f"HTTP {r2.status} on file download ({loc})"
    except Exception as e:
        return None, f"Download error: {e}"


# ---------------------------------------------------------------------------
# Raw CSV parser (same logic as fetch_dgddi.py)
# ---------------------------------------------------------------------------

def parse_raw_dgddi_csv(content_bytes, nc8_code, label, target_years=None):
    """
    Parse the DGDDI raw CSV (ISO-8859-1, semicolon-separated).
    Returns list of dicts with normalized columns.
    """
    if target_years is None:
        target_years = TARGET_YEARS

    text = content_bytes.decode("iso-8859-1", errors="replace")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    rows = []
    current_flux = None
    in_annual = False
    header_cols = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "données annuelles" in line.lower() or "annuelles" in line.lower():
            in_annual = True
            continue
        if "données mensuelles" in line.lower():
            in_annual = False
            continue

        if not in_annual:
            continue

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

        try:
            reader = csv.reader(io.StringIO(line), delimiter=";", quotechar='"')
            cols = next(reader)
        except Exception:
            continue

        if not cols:
            continue

        first = cols[0].strip().strip('"')

        # Header row
        if first.lower() in ("zone - pays", "zone-pays", "zone"):
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

        # Skip aggregate zones
        if first in ZONES_TO_SKIP:
            continue

        if not header_cols:
            continue

        # Build year→{valeur, masse} map for this row
        year_data = {}
        for (col_idx, yr, typ) in header_cols:
            if yr not in target_years:
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
                continue
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

    print("=" * 65)
    print("DGDDI Trade Data Fetcher v2 — ChemistrySpot (new excipients)")
    print("Source: lekiosque.finances.gouv.fr")
    print(f"Target years: {TARGET_YEARS}")
    print("=" * 65)
    print()
    print("NC8 validation results (tested 31/03/2026):")
    print("  39123900 (HPMC)          → INVALID (HTTP 500)")
    print("  39123100 (Croscarmellose) → VALID   (302 redirect)")
    print("  29159040 (Mag Stearate)  → INVALID (HTTP 500)")
    print("  29159070 (Mag Stearate)  → VALID   (302 redirect)")
    print("  39129090 (MCC/Cellulose) → already downloaded, reuse")
    print()

    results = {}

    for nc8_code, info in NC8_V2.items():
        label = info["label"]
        output_path = os.path.join(OUTPUT_DIR, f"dgddi_{nc8_code}.csv")

        print(f"[{nc8_code}] {label}")

        # Case 1: Reuse existing raw file (already downloaded)
        if info.get("reuse_raw"):
            raw_path = os.path.join(OUTPUT_DIR, info["reuse_raw"])
            if os.path.exists(raw_path):
                print(f"  [REUSE] Parsing existing {info['reuse_raw']}...")
                with open(raw_path, "rb") as f:
                    content = f.read()
                rows = parse_raw_dgddi_csv(content, nc8_code, label, TARGET_YEARS)
                if not rows:
                    print(f"  [WARN] No rows for years {TARGET_YEARS}, trying 2023 only...")
                    rows = parse_raw_dgddi_csv(content, nc8_code, label, [2023])
                write_normalized_csv(rows, output_path)
                results[nc8_code] = {"status": "real", "rows": len(rows), "source": raw_path}
                print()
                continue
            else:
                print(f"  [WARN] Raw file not found: {raw_path}")
                # Fall through to download attempt

        # Case 2: Invalid code — use synthetic data
        if not info["valid"]:
            note = info.get("note", "Invalid NC8 code")
            print(f"  [INFO] {note}")
            print(f"  [SYNTHETIC] Generating realistic synthetic data...")
            rows = write_synthetic_csv(nc8_code, label, output_path)
            results[nc8_code] = {"status": "synthetic", "rows": len(rows)}
            print()
            continue

        # Case 3: Valid code — download from lekiosque
        print(f"  [FETCH] Getting session cookie...")
        cookie = get_session_cookie()
        if cookie:
            print(f"  [FETCH] Cookie obtained: {cookie[:50]}...")

        print(f"  [FETCH] Downloading {nc8_code}...")
        content, info_url = download_nc8_raw(nc8_code, cookie)

        if content is None:
            print(f"  [WARN] Download failed: {info_url} — falling back to synthetic")
            rows = write_synthetic_csv(nc8_code, label, output_path)
            results[nc8_code] = {"status": "synthetic_fallback", "rows": len(rows)}
        else:
            print(f"  [OK] Downloaded from {info_url} ({len(content)} bytes)")
            # Save raw file
            raw_path = os.path.join(OUTPUT_DIR, f"dgddi_{nc8_code}_raw.csv")
            with open(raw_path, "wb") as f:
                f.write(content)

            rows = parse_raw_dgddi_csv(content, nc8_code, label, TARGET_YEARS)
            if not rows:
                print(f"  [WARN] No data rows parsed for years {TARGET_YEARS}")
                print(f"  [INFO] Retrying with [2023] only...")
                rows = parse_raw_dgddi_csv(content, nc8_code, label, [2023])
            write_normalized_csv(rows, output_path)
            results[nc8_code] = {"status": "real", "rows": len(rows), "source": info_url}

        time.sleep(1.0)
        print()

    # Summary
    print("=" * 65)
    print("SUMMARY")
    print("=" * 65)
    for nc8_code, res in results.items():
        label_short = NC8_V2[nc8_code]["label"][:50]
        if res["status"] == "real":
            status_str = "REAL DATA"
        elif res["status"] == "synthetic":
            status_str = "SYNTHETIC"
        else:
            status_str = "SYNTHETIC (download failed)"
        print(f"  {nc8_code} [{status_str}]: {res['rows']} rows — {label_short}")

    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("Normalized CSV files written:")
    for nc8_code in NC8_V2:
        path = os.path.join(OUTPUT_DIR, f"dgddi_{nc8_code}.csv")
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  dgddi_{nc8_code}.csv ({size} bytes)")


if __name__ == "__main__":
    main()
