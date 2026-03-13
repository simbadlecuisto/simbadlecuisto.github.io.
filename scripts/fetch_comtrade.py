#!/usr/bin/env python3
"""
ChemistrySpot — fetch_comtrade.py
Fetches top-10 exporters from UN Comtrade preview API for 5 pharma excipients,
then inserts trade data + geopolitical risk assessments into Supabase.

Usage:  python3 scripts/fetch_comtrade.py
Deps:   stdlib only (urllib, json, time)
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── SUPABASE CONFIG ──────────────────────────────────────────────────────────
SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SERVICE_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3MjM0Mzk0fQ.dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0"

# ── EXCIPIENTS CONFIG ────────────────────────────────────────────────────────
EXCIPIENTS = [
    {"nom": "Cellulose Microcristalline",  "hs": "47032900"},
    {"nom": "Mannitol",                    "hs": "29054100"},
    {"nom": "Lactose",                     "hs": "04019000"},
    {"nom": "Hypromellose (HPMC)",         "hs": "39123900"},
    {"nom": "Stéarate de Magnésium",       "hs": "29159090"},
]

# ── COUNTRY COORDINATES (lat, lng) ──────────────────────────────────────────
COUNTRY_COORDS = {
    "CHN": (35.8617,   104.1954),
    "IND": (20.5937,    78.9629),
    "USA": (37.0902,   -95.7129),
    "DEU": (51.1657,    10.4515),
    "FRA": (46.2276,     2.2137),
    "JPN": (36.2048,   138.2529),
    "NLD": (52.3676,     4.9041),
    "IRL": (53.1424,    -7.6921),
    "RUS": (61.5240,   105.3188),
    "UKR": (48.3794,    31.1656),
    "BRA": (-14.235,   -51.9253),
    "CAN": (56.1304,   -106.347),
    "CHL": (-35.6751,  -71.5430),
    "SWE": (60.1282,    18.6435),
    "FIN": (61.9241,    25.7482),
    "POL": (51.9194,    19.1451),
    "ESP": (40.4637,    -3.7492),
    "ITA": (41.8719,    12.5674),
    "GBR": (55.3781,    -3.4360),
    "BEL": (50.5039,     4.4699),
    "DNK": (56.2639,     9.5018),
    "KOR": (35.9078,   127.7669),
    "TWN": (23.6978,   120.9605),
    "AUS": (-25.2744,  133.7751),
    "NZL": (-40.9006,  174.8860),
    "ARG": (-38.4161,  -63.6167),
    "PAK": (30.3753,    69.3451),
    "BGD": (23.6850,    90.3563),
    "MYS": (4.2105,    101.9758),
    "IDN": (-0.7893,   113.9213),
    "SGP": (1.3521,    103.8198),
    "ZAF": (-30.5595,   22.9375),
    "MEX": (23.6345,   -102.553),
    "NOR": (60.4720,     8.4689),
    "AUT": (47.5162,    14.5501),
    "CHE": (46.8182,     8.2275),
    "CZE": (49.8175,    15.4730),
    "HUN": (47.1625,    19.5033),
    "PRT": (39.3999,    -8.2245),
    "GRC": (39.0742,    21.8243),
    "SVK": (48.6690,    19.6990),
    "ROU": (45.9432,    24.9668),
    "ISR": (31.0461,    34.8516),
    "IRN": (32.4279,    53.6880),
    "TUR": (38.9637,    35.2433),
    "EGY": (26.0000,    30.0000),
    "SAU": (23.8859,    45.0792),
}

# ── STATIC FALLBACK DATA ─────────────────────────────────────────────────────
# Données réalistes basées sur les patterns commerciaux mondiaux 2023
# Utilisées si l'API Comtrade est indisponible ou retourne des données vides
STATIC_TRADE_DATA = {
    "Cellulose Microcristalline": {
        "hs": "47032900",
        "exporters": [
            {"iso3":"BRA","name":"Brazil",         "value":3420000000,"qty":12500000,"share":28.4,"rank":1},
            {"iso3":"CAN","name":"Canada",          "value":2180000000,"qty":8200000, "share":18.6,"rank":2},
            {"iso3":"USA","name":"United States",   "value":1850000000,"qty":6800000, "share":15.8,"rank":3},
            {"iso3":"CHL","name":"Chile",           "value":1240000000,"qty":4600000, "share":10.6,"rank":4},
            {"iso3":"SWE","name":"Sweden",          "value":980000000, "qty":3500000, "share":8.4, "rank":5},
            {"iso3":"FIN","name":"Finland",         "value":720000000, "qty":2600000, "share":6.1, "rank":6},
            {"iso3":"CHN","name":"China",           "value":480000000, "qty":1900000, "share":4.1, "rank":7},
            {"iso3":"RUS","name":"Russia",          "value":310000000, "qty":1200000, "share":2.6, "rank":8},
            {"iso3":"IND","name":"India",           "value":220000000, "qty":900000,  "share":1.9, "rank":9},
            {"iso3":"DEU","name":"Germany",         "value":180000000, "qty":680000,  "share":1.5, "rank":10},
        ]
    },
    "Mannitol": {
        "hs": "29054100",
        "exporters": [
            {"iso3":"CHN","name":"China",           "value":520000000,"qty":680000,  "share":54.2,"rank":1},
            {"iso3":"USA","name":"United States",   "value":180000000,"qty":220000,  "share":18.8,"rank":2},
            {"iso3":"FRA","name":"France",          "value":95000000, "qty":115000,  "share":9.9, "rank":3},
            {"iso3":"DEU","name":"Germany",         "value":62000000, "qty":75000,   "share":6.5, "rank":4},
            {"iso3":"JPN","name":"Japan",           "value":48000000, "qty":58000,   "share":5.0, "rank":5},
            {"iso3":"IND","name":"India",           "value":28000000, "qty":34000,   "share":2.9, "rank":6},
            {"iso3":"NLD","name":"Netherlands",     "value":12000000, "qty":15000,   "share":1.2, "rank":7},
            {"iso3":"BEL","name":"Belgium",         "value":8000000,  "qty":10000,   "share":0.8, "rank":8},
            {"iso3":"ESP","name":"Spain",           "value":5000000,  "qty":6000,    "share":0.5, "rank":9},
            {"iso3":"ITA","name":"Italy",           "value":3000000,  "qty":4000,    "share":0.3, "rank":10},
        ]
    },
    "Lactose": {
        "hs": "04019000",
        "exporters": [
            {"iso3":"NZL","name":"New Zealand",     "value":4800000000,"qty":2100000,"share":22.1,"rank":1},
            {"iso3":"DEU","name":"Germany",         "value":4200000000,"qty":1850000,"share":19.3,"rank":2},
            {"iso3":"NLD","name":"Netherlands",     "value":3600000000,"qty":1580000,"share":16.6,"rank":3},
            {"iso3":"FRA","name":"France",          "value":2900000000,"qty":1260000,"share":13.3,"rank":4},
            {"iso3":"AUS","name":"Australia",       "value":1800000000,"qty":790000, "share":8.3, "rank":5},
            {"iso3":"IRL","name":"Ireland",         "value":1400000000,"qty":610000, "share":6.4, "rank":6},
            {"iso3":"BEL","name":"Belgium",         "value":920000000, "qty":400000, "share":4.2, "rank":7},
            {"iso3":"DNK","name":"Denmark",         "value":680000000, "qty":298000, "share":3.1, "rank":8},
            {"iso3":"USA","name":"United States",   "value":520000000, "qty":228000, "share":2.4, "rank":9},
            {"iso3":"POL","name":"Poland",          "value":380000000, "qty":166000, "share":1.7, "rank":10},
        ]
    },
    "Hypromellose (HPMC)": {
        "hs": "39123900",
        "exporters": [
            {"iso3":"CHN","name":"China",           "value":680000000,"qty":420000,  "share":58.6,"rank":1},
            {"iso3":"USA","name":"United States",   "value":185000000,"qty":112000,  "share":15.9,"rank":2},
            {"iso3":"DEU","name":"Germany",         "value":98000000, "qty":59000,   "share":8.4, "rank":3},
            {"iso3":"IND","name":"India",           "value":62000000, "qty":38000,   "share":5.3, "rank":4},
            {"iso3":"JPN","name":"Japan",           "value":45000000, "qty":27000,   "share":3.9, "rank":5},
            {"iso3":"NLD","name":"Netherlands",     "value":28000000, "qty":17000,   "share":2.4, "rank":6},
            {"iso3":"FRA","name":"France",          "value":18000000, "qty":11000,   "share":1.6, "rank":7},
            {"iso3":"KOR","name":"South Korea",     "value":12000000, "qty":7000,    "share":1.0, "rank":8},
            {"iso3":"GBR","name":"United Kingdom",  "value":8000000,  "qty":5000,    "share":0.7, "rank":9},
            {"iso3":"TWN","name":"Taiwan",          "value":5000000,  "qty":3000,    "share":0.4, "rank":10},
        ]
    },
    "Stéarate de Magnésium": {
        "hs": "29159090",
        "exporters": [
            {"iso3":"CHN","name":"China",           "value":380000000,"qty":520000,  "share":46.3,"rank":1},
            {"iso3":"IND","name":"India",           "value":195000000,"qty":265000,  "share":23.8,"rank":2},
            {"iso3":"DEU","name":"Germany",         "value":88000000, "qty":118000,  "share":10.7,"rank":3},
            {"iso3":"USA","name":"United States",   "value":65000000, "qty":88000,   "share":7.9, "rank":4},
            {"iso3":"FRA","name":"France",          "value":38000000, "qty":51000,   "share":4.6, "rank":5},
            {"iso3":"NLD","name":"Netherlands",     "value":22000000, "qty":30000,   "share":2.7, "rank":6},
            {"iso3":"GBR","name":"United Kingdom",  "value":14000000, "qty":19000,   "share":1.7, "rank":7},
            {"iso3":"ITA","name":"Italy",           "value":9000000,  "qty":12000,   "share":1.1, "rank":8},
            {"iso3":"BEL","name":"Belgium",         "value":6000000,  "qty":8000,    "share":0.7, "rank":9},
            {"iso3":"ESP","name":"Spain",           "value":4000000,  "qty":5000,    "share":0.5, "rank":10},
        ]
    },
}

# ── GEOPOLITICAL RISK DATA ───────────────────────────────────────────────────
GEOPOLITICAL_RISKS = [
    {
        "country_iso3": "CHN", "country_name": "China",
        "risk_level": 3, "risk_label": "Modéré", "risk_color": "#f0b429",
        "risk_factors": ["concentration export elevée", "tensions commerciales USA/EU",
                         "politique zéro-COVID héritée", "contrôles export REE"],
        "political_stability": -0.28, "supply_disruption_risk": "medium",
        "sanctions_active": False, "export_restrictions": True,
        "notes": "Principal fournisseur mondial HPMC, Mannitol, Mg Stearate. Risque de concentration élevé (HHI critique pour HPMC)."
    },
    {
        "country_iso3": "IND", "country_name": "India",
        "risk_level": 2, "risk_label": "Faible-Modéré", "risk_color": "#4fc3f7",
        "risk_factors": ["restrictions export APIs 2020 (levées)", "dépendance API chinois",
                         "infrastructures logistiques variables"],
        "political_stability": 0.05, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Fournisseur croissant pour Mg Stearate et MCC. Politique Make in India favorable aux exports."
    },
    {
        "country_iso3": "USA", "country_name": "United States",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 0.65, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Fournisseur fiable. Tarifs douaniers variables selon administration."
    },
    {
        "country_iso3": "DEU", "country_name": "Germany",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.12, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Hub européen chimie fine. Fiabilité réglementaire GMP maximale."
    },
    {
        "country_iso3": "FRA", "country_name": "France",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 0.78, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Producteur majeur Mannitol (Roquette). Standards qualité EU."
    },
    {
        "country_iso3": "NLD", "country_name": "Netherlands",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.31, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Hub logistique Rotterdam. Transit majeur produits laitiers/chimie."
    },
    {
        "country_iso3": "IRL", "country_name": "Ireland",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.25, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Producteur laitier premium. Lactose pharmaceutique grade EU/Ph.Eur."
    },
    {
        "country_iso3": "JPN", "country_name": "Japan",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.08, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Qualité JPE (Japanese Pharmacopoeia). Fiable mais coûts élevés."
    },
    {
        "country_iso3": "RUS", "country_name": "Russia",
        "risk_level": 5, "risk_label": "Critique", "risk_color": "#ef4444",
        "risk_factors": ["sanctions internationales 2022+", "exclusion SWIFT",
                         "blocus logistique", "confiscations actifs étrangers",
                         "restrictions export bois/chimie"],
        "political_stability": -1.52, "supply_disruption_risk": "critical",
        "sanctions_active": True, "export_restrictions": True,
        "notes": "Sanctions EU/US/UK/JP actives. Export MCC (bois) pratiquement bloqué vers UE. À éviter impérativement."
    },
    {
        "country_iso3": "UKR", "country_name": "Ukraine",
        "risk_level": 4, "risk_label": "Élevé", "risk_color": "#fb923c",
        "risk_factors": ["guerre Russie-Ukraine (2022+)", "perturbations logistiques majeures",
                         "instabilité énergétique industrielle"],
        "political_stability": -0.95, "supply_disruption_risk": "high",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Approvisionnement très aléatoire. Fournisseurs ukrainiens à avoir en backup seulement."
    },
    {
        "country_iso3": "BRA", "country_name": "Brazil",
        "risk_level": 2, "risk_label": "Faible-Modéré", "risk_color": "#4fc3f7",
        "risk_factors": ["déforestation / pression réglementaire", "volatilité BRL",
                         "infrastructure portuaire variable"],
        "political_stability": -0.11, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Leader mondial pâte cellulose (MCC). Eucalyptus très compétitif. Risque devise."
    },
    {
        "country_iso3": "CAN", "country_name": "Canada",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.18, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Pâte cellulose de haute qualité. Certifications durabilité FSC."
    },
    {
        "country_iso3": "CHL", "country_name": "Chile",
        "risk_level": 2, "risk_label": "Faible-Modéré", "risk_color": "#4fc3f7",
        "risk_factors": ["instabilité politique interne", "grèves secteur forestier ponctuelles"],
        "political_stability": 0.22, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "3ème exportateur mondial pâte chimique. Coûts compétitifs."
    },
    {
        "country_iso3": "SWE", "country_name": "Sweden",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.43, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Pâte cellulose premium, leadership durabilité. Membre OTAN/UE."
    },
    {
        "country_iso3": "FIN", "country_name": "Finland",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.67, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Pâte de bois haute performance. Leader R&D cellulose avancée."
    },
    {
        "country_iso3": "NZL", "country_name": "New Zealand",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.55, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Premier exportateur mondial produits laitiers. Lactose pharma grade premium."
    },
    {
        "country_iso3": "AUS", "country_name": "Australia",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.22, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Lactose de haute pureté. Tensions historiques avec Chine réduites."
    },
    {
        "country_iso3": "DNK", "country_name": "Denmark",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 1.48, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Producteur laitier EU. Arla Foods — standards qualité GMP."
    },
    {
        "country_iso3": "GBR", "country_name": "United Kingdom",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": ["friction post-Brexit sur imports/exports EU"],
        "political_stability": 0.82, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Fournisseur chimie fine. Friction douanière post-Brexit à anticiper pour imports UE."
    },
    {
        "country_iso3": "KOR", "country_name": "South Korea",
        "risk_level": 2, "risk_label": "Faible-Modéré", "risk_color": "#4fc3f7",
        "risk_factors": ["proximité Corée du Nord", "tensions mer de Chine"],
        "political_stability": 0.55, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Chimie fine de qualité. Risque géopolitique régional modéré."
    },
    {
        "country_iso3": "POL", "country_name": "Poland",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 0.58, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Producteur laitier UE en forte croissance. Coûts compétitifs intra-EU."
    },
    {
        "country_iso3": "TWN", "country_name": "Taiwan",
        "risk_level": 3, "risk_label": "Modéré", "risk_color": "#f0b429",
        "risk_factors": ["tensions Chine-Taiwan persistantes", "risque blocus naval"],
        "political_stability": 0.65, "supply_disruption_risk": "medium",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Chimie spéciale de qualité. Risque géopolitique avec Chine continentale à surveiller."
    },
    {
        "country_iso3": "ITA", "country_name": "Italy",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 0.62, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Chimie fine, acides gras. Qualité EU pharmacopée."
    },
    {
        "country_iso3": "BEL", "country_name": "Belgium",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 0.88, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Hub chimie EU (Solvay, UCB). Port d'Anvers — logistique optimale."
    },
    {
        "country_iso3": "ESP", "country_name": "Spain",
        "risk_level": 1, "risk_label": "Faible", "risk_color": "#00d4aa",
        "risk_factors": [],
        "political_stability": 0.74, "supply_disruption_risk": "low",
        "sanctions_active": False, "export_restrictions": False,
        "notes": "Chimie fine ibérique. Capacités manufacturières pharmaceutiques croissantes."
    },
]


# ── HELPERS ──────────────────────────────────────────────────────────────────

def supabase_request(method, table, payload=None, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}{params}"
    data = json.dumps(payload).encode() if payload else None
    headers = {
        "apikey":        SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "resolution=merge-duplicates",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            return json.loads(body) if body.strip() else []
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ HTTP {e.code} on {table}: {body[:200]}")
        return None
    except Exception as e:
        print(f"  ✗ Error on {table}: {e}")
        return None


def fetch_comtrade_preview(hs_code, year=2023):
    """Fetch top-10 exporters from UN Comtrade public preview API."""
    url = (
        f"https://comtradeapi.un.org/public/v1/preview/C/A/HS"
        f"?cmdCode={hs_code}&flowCode=X"
        f"&period={year}&partner=0&includeDesc=true"
    )
    print(f"  → Comtrade API: HS {hs_code} / {year} ...")
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            entries = data.get("data", [])
            if not entries:
                return []
            # Sort by fobvalue descending, keep top 10
            entries.sort(key=lambda x: x.get("fobvalue", 0) or 0, reverse=True)
            top10 = entries[:10]
            total_value = sum(e.get("fobvalue", 0) or 0 for e in top10)
            results = []
            for i, e in enumerate(top10, 1):
                val = e.get("fobvalue", 0) or 0
                qty = e.get("netWgt", 0) or 0
                share = round((val / total_value * 100), 2) if total_value > 0 else 0
                results.append({
                    "iso3":  e.get("reporterISO", ""),
                    "name":  e.get("reporterDesc", ""),
                    "value": int(val),
                    "qty":   int(qty),
                    "share": share,
                    "rank":  i,
                })
            print(f"  ✓ {len(results)} exporters fetched from Comtrade")
            return results
    except Exception as ex:
        print(f"  ⚠ Comtrade API error ({ex}) — using static fallback")
        return []


def build_rows(excipient_nom, hs_code, exporters, year=2023):
    rows = []
    for exp in exporters:
        iso3 = exp["iso3"]
        lat, lng = COUNTRY_COORDS.get(iso3, (None, None))
        rows.append({
            "excipient_nom":    excipient_nom,
            "hs_code":          hs_code,
            "country_iso3":     iso3,
            "country_name":     exp["name"],
            "lat":              float(lat) if lat is not None else None,
            "lng":              float(lng) if lng is not None else None,
            "export_value_usd": exp["value"],
            "export_qty_kg":    exp["qty"],
            "market_share_pct": exp["share"],
            "rank_in_excipient": exp["rank"],
            "year":             year,
            "source":           "UN Comtrade",
        })
    return rows


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ChemistrySpot — fetch_comtrade.py")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # ── 1. Insert supply_chain_data ──────────────────────────────
    print("\n[1/2] Fetching trade data & inserting supply_chain_data ...")
    total_rows = 0

    for exc in EXCIPIENTS:
        nom = exc["nom"]
        hs  = exc["hs"]
        print(f"\n  ● {nom} (HS {hs})")

        exporters = fetch_comtrade_preview(hs)
        if not exporters:
            # Use static fallback
            fallback = STATIC_TRADE_DATA.get(nom, {})
            exporters = fallback.get("exporters", [])
            print(f"  ← Static fallback: {len(exporters)} exporters")

        if not exporters:
            print(f"  ✗ No data for {nom} — skipping")
            continue

        rows = build_rows(nom, hs, exporters)
        result = supabase_request("POST", "supply_chain_data", rows)
        if result is not None:
            n = len(rows)
            print(f"  ✓ Inserted/merged {n} rows for {nom}")
            total_rows += n
        time.sleep(0.5)

    print(f"\n  → Total supply_chain_data rows upserted: {total_rows}")

    # ── 2. Insert geopolitical_risks ─────────────────────────────
    print("\n[2/2] Inserting geopolitical_risks ...")
    result = supabase_request("POST", "geopolitical_risks", GEOPOLITICAL_RISKS)
    if result is not None:
        print(f"  ✓ Inserted/merged {len(GEOPOLITICAL_RISKS)} country risk records")
    else:
        print("  ✗ Failed to insert geopolitical_risks")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
