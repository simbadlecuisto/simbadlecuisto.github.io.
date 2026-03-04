#!/usr/bin/env python3
"""
ChemistrySpot — Corriger les pays des fournisseurs (180/192 = Unknown)
3 niveaux de détection : TLD URL → nom de domaine connu → suffixe légal

Usage: python scripts/fix_supplier_countries.py
"""

import re
import json
import urllib.request
import urllib.error

# ── Configuration ──────────────────────────────────────────────
SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI"

BASE_HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

# ── Niveau 1 : TLD → Pays ─────────────────────────────────────
TLD_MAP = {
    ".cn": "China",     ".com.cn": "China",
    ".de": "Germany",   ".com.de": "Germany",
    ".fr": "France",    ".com.fr": "France",
    ".jp": "Japan",     ".co.jp": "Japan",
    ".in": "India",     ".co.in": "India",
    ".kr": "South Korea", ".co.kr": "South Korea",
    ".uk": "UK",        ".co.uk": "UK",
    ".it": "Italy",
    ".es": "Spain",
    ".nl": "Netherlands",
    ".be": "Belgium",
    ".ch": "Switzerland",
    ".at": "Austria",
    ".se": "Sweden",
    ".dk": "Denmark",
    ".no": "Norway",
    ".fi": "Finland",
    ".pl": "Poland",
    ".cz": "Czech Republic",
    ".hu": "Hungary",
    ".ie": "Ireland",
    ".pt": "Portugal",
    ".ru": "Russia",
    ".ua": "Ukraine",
    ".br": "Brazil",
    ".mx": "Mexico",
    ".ar": "Argentina",
    ".ca": "Canada",
    ".au": "Australia",
    ".nz": "New Zealand",
    ".za": "South Africa",
    ".sg": "Singapore",
    ".hk": "Hong Kong",
    ".tw": "Taiwan",
    ".il": "Israel",
    ".sa": "Saudi Arabia",
    ".ae": "UAE",
    ".tr": "Turkey",
}

# ── Niveau 2 : Domaine/nom connu ──────────────────────────────
KNOWN_COMPANIES = {
    # USA
    "sigma-aldrich":  "USA", "sigmaaldrich":  "USA",
    "millipore":      "USA", "emdmillipore":  "USA",
    "alfa aesar":     "USA", "alfaaesar":     "USA",
    "thermo fisher":  "USA", "thermofisher":  "USA",
    "spectrum":       "USA",
    "acros":          "USA",
    "tci america":    "USA",
    "strem":          "USA",
    "combi-blocks":   "USA",
    "cayman":         "USA",
    "chemdea":        "USA",
    "clearsynth":     "USA",
    "boc sciences":   "USA", "bocsciences":   "USA",
    "chempacific":    "USA",
    "akos":           "USA",
    "enamine":        "USA",
    "oakwood":        "USA",
    "spi pharma":     "USA",
    "ibi scientific": "USA",
    # Germany
    "merck kgaa":     "Germany", "merckkgaa": "Germany",
    "evonik":         "Germany",
    "basf":           "Germany",
    "wacker":         "Germany",
    "chemipan":       "Germany",
    "fluorochem":     "Germany",
    "carl roth":      "Germany",
    # France
    "arkema":         "France",
    "roquette":       "France",
    "sanofi":         "France",
    "gattefossé":     "France", "gattefosse": "France",
    # Japan
    "tci":            "Japan",
    "fujifilm":       "Japan",
    "wako":           "Japan",
    "kanto":          "Japan",
    "nacalai":        "Japan",
    "daicel":         "Japan",
    "shin-etsu":      "Japan",
    # China
    "bocsci":         "China",
    "hb chemical":    "China",
    "energy chemical":"China",
    "combi blocks":   "China",
    "glpbio":         "China",
    "macklin":        "China",
    "aladdin":        "China",
    "titan scientific":"China",
    # UK
    "fluorochem uk":  "UK",
    "manchester organics": "UK",
    # India
    "molport":        "India",
    "pvt":            "India",
    # Switzerland
    "lonza":          "Switzerland",
    "novartis":       "Switzerland",
    # Netherlands
    "dsm":            "Netherlands",
    "corbion":        "Netherlands",
}

# ── Niveau 3 : Suffixe légal ──────────────────────────────────
LEGAL_SUFFIX_MAP = [
    # Allemagne
    (r"\bGmbH\b",     "Germany"),
    (r"\bAG\b",       "Germany"),
    (r"\bKG\b",       "Germany"),
    (r"\bGbR\b",      "Germany"),
    # France
    (r"\bSAS\b",      "France"),
    (r"\bSARL\b",     "France"),
    (r"\bSA\b",       "France"),
    # Italie
    (r"\bS\.p\.A\.",  "Italy"),
    (r"\bS\.r\.l\.",  "Italy"),
    (r"\bSrl\b",      "Italy"),
    (r"\bSpA\b",      "Italy"),
    # UK
    (r"\bLtd\b",      "UK"),
    (r"\bPLC\b",      "UK"),
    (r"\bLLP\b",      "UK"),
    # USA
    (r"\bInc\b",      "USA"),
    (r"\bCorp\b",     "USA"),
    (r"\bLLC\b",      "USA"),
    (r"\bLP\b",       "USA"),
    # Inde
    (r"\bPvt\.?\s*Ltd\b", "India"),
    (r"\bPrivate Limited\b", "India"),
    # Japon / Chine / Corée (Co. Ltd. → ambigu, on met Unknown)
    # (r"\bCo\.,?\s*Ltd\b", "Japan"),  # trop ambigu
]


def extract_tld(url: str) -> str | None:
    """Extrait le TLD d'une URL."""
    if not url:
        return None
    # Normaliser
    url = url.lower().strip().rstrip("/")
    # Extraire le hostname
    match = re.search(r"https?://([^/]+)", url)
    if not match:
        return None
    host = match.group(1)
    # Supprimer port et www
    host = re.sub(r":\d+$", "", host)
    host = re.sub(r"^www\.", "", host)
    return host


def detect_country_from_tld(host: str) -> str | None:
    """Niveau 1 : détection via TLD."""
    if not host:
        return None
    # Chercher le TLD le plus long en premier
    for tld in sorted(TLD_MAP.keys(), key=len, reverse=True):
        if host.endswith(tld):
            return TLD_MAP[tld]
    return None


def detect_country_from_name(name: str, website: str | None) -> str | None:
    """Niveau 2 : détection via nom de domaine ou nom d'entreprise."""
    text = (name or "").lower()
    if website:
        text += " " + website.lower()

    for keyword, country in KNOWN_COMPANIES.items():
        if keyword in text:
            return country
    return None


def detect_country_from_suffix(name: str) -> str | None:
    """Niveau 3 : détection via suffixe légal dans le nom."""
    for pattern, country in LEGAL_SUFFIX_MAP:
        if re.search(pattern, name, re.IGNORECASE):
            return country
    return None


def detect_country(supplier: dict) -> str | None:
    """Essaie les 3 niveaux de détection."""
    name    = supplier.get("name", "")
    website = supplier.get("website", "") or ""
    host    = extract_tld(website)

    # Niveau 1 : TLD
    if host:
        c = detect_country_from_tld(host)
        if c:
            return c

    # Niveau 2 : domaine connu / nom entreprise
    c = detect_country_from_name(name, website)
    if c:
        return c

    # Niveau 3 : suffixe légal
    c = detect_country_from_suffix(name)
    if c:
        return c

    return None


def fetch_all_suppliers() -> list[dict]:
    """Charge tous les fournisseurs Unknown depuis Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/suppliers?country=eq.Unknown&select=id,name,website&order=id"
    req = urllib.request.Request(url, headers=BASE_HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def update_supplier_country(supplier_id: int, country: str) -> bool:
    """PATCH le pays d'un fournisseur."""
    url     = f"{SUPABASE_URL}/rest/v1/suppliers?id=eq.{supplier_id}"
    payload = json.dumps({"country": country}).encode("utf-8")
    headers = {**BASE_HEADERS, "Prefer": "return=minimal"}
    req     = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"  ❌  PATCH échoué (id={supplier_id}): HTTP {e.code}")
        return False


def main():
    print("═" * 60)
    print("ChemistrySpot — Fix Supplier Countries")
    print("═" * 60)

    print("\n📦 Chargement des fournisseurs Unknown...")
    try:
        suppliers = fetch_all_suppliers()
    except Exception as e:
        print(f"❌ Erreur Supabase: {e}")
        return

    print(f"   → {len(suppliers)} fournisseurs avec pays='Unknown'\n")

    # Compteurs par niveau
    counts = {"tld": 0, "name": 0, "suffix": 0, "unknown": 0}
    updated = 0

    for sup in suppliers:
        name    = sup.get("name", "—")
        website = sup.get("website", "") or ""
        host    = extract_tld(website)

        # Niveau 1
        c = detect_country_from_tld(host) if host else None
        level = "tld"

        # Niveau 2
        if not c:
            c = detect_country_from_name(name, website)
            level = "name"

        # Niveau 3
        if not c:
            c = detect_country_from_suffix(name)
            level = "suffix"

        if c:
            counts[level] += 1
            ok = update_supplier_country(sup["id"], c)
            if ok:
                updated += 1
                print(f"  ✅  [{level:6s}] {name[:45]:<45} → {c}")
            else:
                print(f"  ❌         {name[:45]}")
        else:
            counts["unknown"] += 1
            print(f"  ❓  [n/a   ] {name[:45]:<45} → Unknown (conservé)")

    print("\n" + "─" * 60)
    print(f"Résultats :")
    print(f"  Identifiés via TLD    : {counts['tld']}")
    print(f"  Identifiés via Nom    : {counts['name']}")
    print(f"  Identifiés via Suffixe: {counts['suffix']}")
    print(f"  Toujours Unknown      : {counts['unknown']}")
    print(f"  Total mis à jour      : {updated}")
    print("─" * 60)


if __name__ == "__main__":
    main()
