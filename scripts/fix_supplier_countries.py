#!/usr/bin/env python3
"""
ChemistrySpot — Corriger les pays des fournisseurs (180/192 = Unknown)
4 niveaux de détection :
  1. Base manuelle (150+ entreprises connues)
  2. TLD URL (60+ TLDs → pays)
  3. Nom de domaine / nom d'entreprise connu
  4. Suffixe légal (GmbH→Germany, Inc→USA, etc.)

Usage: python3 scripts/fix_supplier_countries.py
"""

import re
import json
import urllib.request
import urllib.error

# ── Configuration ──────────────────────────────────────────────
SUPABASE_URL      = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SUPABASE_KEY      = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3MjM0Mzk0fQ.dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0"

BASE_HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

# ══════════════════════════════════════════════════════════════
# NIVEAU 1 — Base manuelle (nom exact → pays)
# Couvre ~150 des 180 Unknown après analyse des noms/domaines
# ══════════════════════════════════════════════════════════════
MANUAL_COUNTRIES: dict[str, str] = {
    # ── USA ───────────────────────────────────────────────────
    "1st Scientific":                         "USA",
    "3WAY PHARM INC":                         "USA",
    "A2B Chem":                               "USA",
    "Aaron Chemicals LLC":                    "USA",
    "Accel Scientific":                       "USA",
    "Accela ChemBio Inc.":                    "USA",
    "Aceschem Inc":                           "USA",
    "Adooq BioScience":                       "USA",
    "AEchem Scientific Corp., USA":           "USA",
    "AK Scientific, Inc. (AKSCI)":            "USA",
    "Amerigo Scientific":                     "USA",
    "Ark Pharm, Inc.":                        "USA",
    "AstaTech, Inc.":                         "USA",
    "Aurora Fine Chemicals LLC":              "USA",
    "Aurum Pharmatech LLC":                   "USA",
    "Avantor Inc":                            "USA",
    "BOC Sciences":                           "USA",
    "BroadPharm":                             "USA",
    "Calbiochem":                             "USA",
    "CATO Research Chemicals Inc.":           "USA",
    "Chem-Impex":                             "USA",
    "Combi-Blocks":                           "USA",
    "CD Formulation":                         "USA",
    "EMD Biosciences":                        "USA",
    "EMD Millipore":                          "USA",
    "eMolecules":                             "USA",
    "Fisher Chemical":                        "USA",
    "GFS Chemicals":                          "USA",
    "iChemical Technology USA Inc":           "USA",
    "InvivoChem":                             "USA",
    "Lorad Chemical Corporation":             "USA",
    "Matrix Scientific":                      "USA",
    "MP Biomedicals":                         "USA",
    "Oakwood Products":                       "USA",
    "OXCHEM CORPORATION":                     "USA",
    "Parchem":                                "USA",
    "Pfanstiehl Inc":                         "USA",
    "Quality Control Solutions (QCS Standards)": "USA",
    "Selleck Chemicals":                      "USA",
    "Strem Chemicals, Inc.":                  "USA",
    "Synblock Inc":                           "USA",
    "SynQuest Laboratories":                  "USA",
    "Thoreauchem":                            "USA",
    "TimTec":                                 "USA",
    "VWR, Part of Avantor":                   "USA",
    "Wilshire Technologies":                  "USA",
    "ZINC":                                   "USA",
    "MedChemexpress MCE":                     "USA",
    "ISpharm":                                "USA",
    "Protheragen":                            "USA",

    # ── China ─────────────────────────────────────────────────
    "001Chemical":                            "China",
    "10X CHEM":                               "China",
    "A&J Pharmtech CO., LTD.":               "China",
    "AA BLOCKS":                              "China",
    "AAA Chemistry":                          "China",
    "AbaChemScene":                           "China",
    "ABBLIS Chemicals":                       "China",
    "ABI Chem":                               "China",
    "AbMole Bioscience":                      "China",
    "Acadechem":                              "China",
    "Achemica":                               "China",
    "Achemtek":                               "China",
    "Active Biopharma":                       "China",
    "AHH Chemical co.,ltd":                   "China",
    "AiFChem, an XtalPi Company":             "China",
    "Aladdin Scientific":                     "China",
    "Alichem":                                "China",
    "Amadis Chemical":                        "China",
    "Ambeed":                                 "China",
    "AN PharmaTech":                          "China",
    "Angel Pharmatech Ltd.":                  "China",
    "Angene Chemical":                        "China",
    "Anward":                                 "China",
    "ApexBio Technology":                     "China",
    "Apexmol":                                "China",
    "AppChem":                                "China",
    "Aribo Reagent":                          "China",
    "Aromalake Chemical":                     "China",
    "Aromsyn catalogue":                      "China",
    "BePharm Ltd.":                           "China",
    "Bic Biotech":                            "China",
    "BioChemPartner":                         "China",
    "BioCrick":                               "China",
    "BLD Pharm":                              "China",
    "Boerchem":                               "China",
    "Boronpharm":                             "China",
    "Cangzhou Enke Pharma Tech Co.,Ltd.":     "China",
    "CAPOT":                                  "China",
    "Career Henan Chemical Co":               "China",
    "Changzhou Highassay Chemical Co., Ltd":  "China",
    "Chembase.cn":                            "China",
    "Chemenu Inc.":                           "China",
    "ChemFaces":                              "China",
    "Chemieliva Pharmaceutical Co., Ltd":     "China",
    "ChemMol":                                "China",
    "China MainChem Co., Ltd":                "China",
    "Cooke Chemical Co., Ltd":               "China",
    "CSNpharm":                               "China",
    "DC Chemicals":                           "China",
    "Debye Scientific Co., Ltd":             "China",
    "eNovation Chemicals":                    "China",
    "Finetech Industry Limited":              "China",
    "Founder Pharma":                         "China",
    "Hairui Chemical":                        "China",
    "Hangzhou APIChem Technology":            "China",
    "Hunan Chemfish Pharmaceutical Co., Ltd.":"China",
    "Hunan Huateng Pharmaceutical Co., Ltd.": "China",
    "J&H Chemical Co.,ltd":                  "China",
    "Jamson Pharmachem Technology":           "China",
    "Kingston Chemistry":                     "China",
    "LabNetwork, a WuXi AppTec Company":      "China",
    "labseeker":                              "China",
    "Lan Pharmatech":                         "China",
    "LEAPCHEM":                               "China",
    "MolCore":                                "China",
    "Molecule Market":                        "China",
    "MuseChem":                               "China",
    "Pi Chemicals":                           "China",
    "Race Chemical":                          "China",
    "Sinfoo Biotech":                         "China",
    "Sinofi Ingredients":                     "China",
    "Smolecule":                              "China",
    "Starshine Chemical":                     "China",
    "Syntree":                                "China",
    "TargetMol":                              "China",
    "Win-Win Chemical":                       "China",
    "Wubei-Biochem":                          "China",
    "Wutech":                                 "China",
    "Yuhao Chemical":                         "China",
    "Zjartschem":                             "China",
    "Elsa Biotechnology":                     "China",
    "Synblock Inc":                           "China",

    # ── Hong Kong ─────────────────────────────────────────────
    "Yick-Vic Chemicals & Pharmaceuticals (HK) Ltd.": "Hong Kong",

    # ── Germany ───────────────────────────────────────────────
    "abcr GmbH":                              "Germany",
    "AKos Consulting & Solutions":            "Germany",
    "Midas Pharma GmbH":                      "Germany",

    # ── UK ────────────────────────────────────────────────────
    "Biorbyt":                                "UK",
    "Key Organics/BIONET":                    "UK",
    "Tocris Bioscience":                      "UK",
    "Nature Science Technologies Ltd":        "UK",
    "Phion Ltd":                              "UK",

    # ── France ────────────────────────────────────────────────
    "Ambinter":                               "France",

    # ── Spain ─────────────────────────────────────────────────
    "CymitQuimica":                           "Spain",

    # ── Turkey ────────────────────────────────────────────────
    "AEZ Kimya":                              "Turkey",
    "Alinda Chemical Trade Company Ltd":      "Turkey",

    # ── Ukraine ───────────────────────────────────────────────
    "Enamine":                                "Ukraine",
    "Innovapharm":                            "Ukraine",
    "Life Chemicals":                         "Ukraine",
    "OtavaChemicals":                         "Ukraine",
    "VladaChem":                              "Ukraine",
    "EvitaChem":                              "Ukraine",

    # ── Russia ────────────────────────────────────────────────
    "INTERBIOSCREEN":                         "Russia",
    "Vitas-M Laboratory":                     "Russia",

    # ── Switzerland ───────────────────────────────────────────
    "Biosynth":                               "Switzerland",

    # ── India ─────────────────────────────────────────────────
    "Clearsynth":                             "India",
    "Veeprho":                                "India",
    "Biocore":                                "India",

    # ── Latvia ────────────────────────────────────────────────
    "Molport":                                "Latvia",
    "Chem-Space.com Database":                "Latvia",

    # ── Hungary ───────────────────────────────────────────────
    "Mcule":                                  "Hungary",

    # ── Poland ────────────────────────────────────────────────
    "BenchChem":                              "Poland",

    # ── Belgium ───────────────────────────────────────────────
    "ChemExper Chemical Directory":           "Belgium",

    # ── Mixed / databases ─────────────────────────────────────
    "AgroIntelBioScan.com":                   "USA",
    "AmicBase - Antimicrobial Activities":    "USA",
    "Chemchart":                              "USA",
    "ChemoSapiens":                           "USA",
    "ChemTik":                                "China",
    "Moldb":                                  "USA",
    "Molepedia":                              "USA",
    "NovoSeek":                               "USA",
    "OChem":                                  "Russia",
    "THE BioTek":                             "USA",
    "Tractus":                                "USA",
    "DempoChem":                              "India",
    "EDASA Scientific":                       "China",
    "SynHet - Synthetic Heterocycles":        "Ukraine",
    "SMID":                                   "China",
    "Aronis":                                 "Greece",
    "King Scientific":                        "USA",
    "Kyfora Bio":                             "USA",
    "Toref Standards":                        "China",
}

# ══════════════════════════════════════════════════════════════
# NIVEAU 2 — TLD → Pays
# ══════════════════════════════════════════════════════════════
TLD_MAP = {
    ".cn": "China",     ".com.cn": "China",
    ".de": "Germany",   ".com.de": "Germany",
    ".fr": "France",    ".com.fr": "France",
    ".jp": "Japan",     ".co.jp": "Japan",
    ".in": "India",     ".co.in": "India",
    ".kr": "South Korea", ".co.kr": "South Korea",
    ".uk": "UK",        ".co.uk": "UK",
    ".it": "Italy",     ".es": "Spain",
    ".nl": "Netherlands", ".be": "Belgium",
    ".ch": "Switzerland", ".at": "Austria",
    ".se": "Sweden",    ".dk": "Denmark",
    ".no": "Norway",    ".fi": "Finland",
    ".pl": "Poland",    ".cz": "Czech Republic",
    ".hu": "Hungary",   ".ie": "Ireland",
    ".pt": "Portugal",  ".ru": "Russia",
    ".ua": "Ukraine",   ".com.tr": "Turkey",
    ".tr": "Turkey",    ".br": "Brazil",
    ".mx": "Mexico",    ".ca": "Canada",
    ".au": "Australia", ".nz": "New Zealand",
    ".za": "South Africa", ".sg": "Singapore",
    ".hk": "Hong Kong", ".tw": "Taiwan",
    ".il": "Israel",    ".sa": "Saudi Arabia",
    ".ae": "UAE",
}

# ══════════════════════════════════════════════════════════════
# NIVEAU 3 — Domaine connu / nom d'entreprise
# ══════════════════════════════════════════════════════════════
KNOWN_PATTERNS = {
    # USA
    "sigma-aldrich": "USA", "sigmaaldrich": "USA",
    "millipore": "USA", "thermo fisher": "USA",
    "thermofisher": "USA", "alfa aesar": "USA",
    "alfaaesar": "USA", "spectrum": "USA",
    "acros organics": "USA", "tci america": "USA",
    "strem": "USA", "spi pharma": "USA",
    "emolecules": "USA", "invivochem": "USA",
    "broadpharm": "USA", "bocsci": "USA",
    "boc sciences": "USA", "selleckchem": "USA",
    "selleck": "USA", "matrixscientific": "USA",
    "gfschemicals": "USA", "strem.com": "USA",
    "synquestlabs": "USA",
    # Germany
    "merck kgaa": "Germany", "evonik": "Germany",
    "basf": "Germany", "wacker": "Germany",
    "carl roth": "Germany", "gmbh": "Germany",
    "akosgmbh": "Germany", "abcr.com": "Germany",
    "midas-pharma": "Germany",
    # France
    "arkema": "France", "roquette": "France",
    "sanofi": "France", "gattefosse": "France",
    "ambinter": "France",
    # Japan
    "fujifilm": "Japan", "wako": "Japan",
    "kanto": "Japan", "nacalai": "Japan",
    "shin-etsu": "Japan", "daicel": "Japan",
    # China
    "hairuichem": "China", "bldpharm": "China",
    "angenechemical": "China", "amadischem": "China",
    "capotchem": "China", "boronpharm": "China",
    "chemenu": "China", "ambeed": "China",
    "musechem": "China", "leapchem": "China",
    "chemscene": "China", "aladdinsci": "China",
    "enkepharma": "China", "apichemistry": "China",
    "chemfish": "China", "huatengsci": "China",
    "jhechem": "China", "chemfaces": "China",
    "dcchemicals": "China", "sinfoobiotech": "China",
    "starshinechemical": "China", "smolecule": "China",
    "appchemical": "China", "cookechem": "China",
    "astatechinc": "China",
    # UK
    "biorbyt": "UK", "keyorganics": "UK",
    "tocris": "UK",
    # Ukraine
    "enaminestore": "Ukraine", "enamine": "Ukraine",
    "lifechemicals": "Ukraine", "otavachemicals": "Ukraine",
    "vladachem": "Ukraine", "innovapharm.com.ua": "Ukraine",
    # Switzerland
    "biosynth": "Switzerland", "lonza": "Switzerland",
    # India
    "clearsynth": "India",
    # Spain
    "cymitquimica": "Spain",
    # Latvia
    "molport": "Latvia", "chem-space": "Latvia",
    # Hungary
    "mcule": "Hungary",
    # Poland
    "benchchem": "Poland",
    # Turkey
    "aez.com.tr": "Turkey", "alindachemical": "Turkey",
}

# ══════════════════════════════════════════════════════════════
# NIVEAU 4 — Suffixe légal
# ══════════════════════════════════════════════════════════════
LEGAL_SUFFIX_MAP = [
    (r"\bGmbH\b",                "Germany"),
    (r"\bAG\b",                  "Germany"),
    (r"\bKG\b",                  "Germany"),
    (r"\bSAS\b",                 "France"),
    (r"\bSARL\b",                "France"),
    (r"\bS\.p\.A\.",             "Italy"),
    (r"\bS\.r\.l\.",             "Italy"),
    (r"\bSpA\b",                 "Italy"),
    (r"\bSrl\b",                 "Italy"),
    (r"\bPLC\b",                 "UK"),
    (r"\bLLP\b",                 "UK"),
    (r"\bInc\.?\b",              "USA"),
    (r"\bCorp\.?\b",             "USA"),
    (r"\bLLC\b",                 "USA"),
    (r"\bLP\b",                  "USA"),
    (r"\bPvt\.?\s*Ltd\b",        "India"),
    (r"\bPrivate\s+Limited\b",   "India"),
]


# ══════════════════════════════════════════════════════════════
# DÉTECTION
# ══════════════════════════════════════════════════════════════
def extract_host(url: str) -> str | None:
    if not url:
        return None
    url = url.lower().strip().rstrip("/")
    m = re.search(r"https?://([^/]+)", url)
    if not m:
        return None
    host = re.sub(r":\d+$", "", m.group(1))
    host = re.sub(r"^www\.", "", host)
    return host


def detect_by_tld(host: str | None) -> str | None:
    if not host:
        return None
    for tld in sorted(TLD_MAP.keys(), key=len, reverse=True):
        if host.endswith(tld):
            return TLD_MAP[tld]
    return None


def detect_by_pattern(name: str, website: str | None) -> str | None:
    text = (name or "").lower() + " " + (website or "").lower()
    for kw, country in KNOWN_PATTERNS.items():
        if kw in text:
            return country
    return None


def detect_by_suffix(name: str) -> str | None:
    for pattern, country in LEGAL_SUFFIX_MAP:
        if re.search(pattern, name, re.IGNORECASE):
            return country
    return None


def detect_country(sup: dict) -> tuple[str | None, str]:
    """Retourne (pays, niveau_détection)."""
    name    = (sup.get("name") or "").strip()
    website = (sup.get("website") or "").strip()
    host    = extract_host(website)

    # Niveau 1 — base manuelle
    if name in MANUAL_COUNTRIES:
        return MANUAL_COUNTRIES[name], "manual"

    # Niveau 2 — TLD
    c = detect_by_tld(host)
    if c:
        return c, "tld"

    # Niveau 3 — patterns
    c = detect_by_pattern(name, website)
    if c:
        return c, "pattern"

    # Niveau 4 — suffixe légal
    c = detect_by_suffix(name)
    if c:
        return c, "suffix"

    return None, "none"


# ══════════════════════════════════════════════════════════════
# SUPABASE
# ══════════════════════════════════════════════════════════════
def fetch_unknown_suppliers() -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/suppliers?country=eq.Unknown&select=id,name,website&order=name&limit=500"
    req = urllib.request.Request(url, headers=BASE_HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def update_country(sid: int, country: str) -> bool:
    url     = f"{SUPABASE_URL}/rest/v1/suppliers?id=eq.{sid}"
    payload = json.dumps({"country": country}).encode()
    hdrs    = {**BASE_HEADERS, "Prefer": "return=minimal"}
    req     = urllib.request.Request(url, data=payload, headers=hdrs, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"  ❌ PATCH id={sid}: HTTP {e.code}")
        return False


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    print("═" * 62)
    print("ChemistrySpot — Fix Supplier Countries (v2)")
    print("═" * 62)

    print("\n📦 Chargement des fournisseurs Unknown...")
    try:
        suppliers = fetch_unknown_suppliers()
    except Exception as e:
        print(f"❌ Erreur Supabase : {e}")
        return
    print(f"   → {len(suppliers)} fournisseurs Unknown\n")

    counts   = {"manual": 0, "tld": 0, "pattern": 0, "suffix": 0, "none": 0}
    updated  = 0
    by_country: dict[str, int] = {}

    for sup in suppliers:
        country, level = detect_country(sup)

        if country:
            counts[level] += 1
            by_country[country] = by_country.get(country, 0) + 1
            ok = update_country(sup["id"], country)
            if ok:
                updated += 1
                tag = f"[{level:7s}]"
                print(f"  ✅ {tag} {sup['name'][:48]:<48} → {country}")
            else:
                print(f"  ❌          {sup['name'][:48]}")
        else:
            counts["none"] += 1
            print(f"  ❓ [n/a    ] {sup['name'][:48]:<48} → Unknown (conservé)")

    print("\n" + "─" * 62)
    print("Détection par niveau :")
    print(f"  Base manuelle : {counts['manual']}")
    print(f"  TLD URL       : {counts['tld']}")
    print(f"  Patterns      : {counts['pattern']}")
    print(f"  Suffixe légal : {counts['suffix']}")
    print(f"  Toujours Unknown : {counts['none']}")
    print(f"\nTotal mis à jour : {updated}/{len(suppliers)}")

    print("\nRépartition par pays :")
    for country, n in sorted(by_country.items(), key=lambda x: -x[1]):
        print(f"  {country:<25} {n:3d}")
    print("─" * 62)


if __name__ == "__main__":
    main()
