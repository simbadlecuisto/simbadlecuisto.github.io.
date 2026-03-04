#!/usr/bin/env python3
"""
ChemistrySpot — Fetch prix depuis Pharmacompass
Stratégie : scraping HTML avec urllib + html.parser (stdlib uniquement)
Fallback : fourchettes par catégorie si scraping échoue

Usage: python scripts/fetch_prices_pharmacompass.py
Output: data/prices.json
"""

import re
import time
import json
import os
import urllib.request
import urllib.error
from html.parser import HTMLParser

# ── Configuration ──────────────────────────────────────────────
SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI"

USD_TO_EUR = 0.92   # taux de conversion fixe
DELAY_S    = 3      # délai entre requêtes (secondes)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
}

# ── Fourchettes de repli par catégorie ────────────────────────
CATEGORY_FALLBACK = {
    "cellulose":     (1.50, 2.80),
    "hpmc":          (15.0, 30.0),
    "hpc":           (12.0, 22.0),
    "povidone":      (8.00, 15.0),
    "lactose":       (0.80, 1.20),
    "mannitol":      (3.00, 5.00),
    "sorbitol":      (0.80, 1.40),
    "starch":        (0.50, 1.00),
    "amidon":        (0.50, 1.00),
    "talc":          (0.30, 0.80),
    "stearate":      (2.50, 4.00),
    "stéarate":      (2.50, 4.00),
    "glycerol":      (0.90, 1.50),
    "glycérol":      (0.90, 1.50),
    "polysorbate":   (6.00, 10.0),
    "peg":           (2.50, 4.50),
    "macrogol":      (2.50, 4.50),
    "titanium":      (3.00, 6.00),
    "titane":        (3.00, 6.00),
    "silica":        (8.00, 15.0),
    "silice":        (8.00, 15.0),
    "zinc":          (2.00, 4.00),
    "benzalkonium":  (8.00, 18.0),
    "sodium chloride":(0.15, 0.35),
    "calcium":       (0.30, 0.70),
    "citric":        (0.70, 1.30),
    "citrique":      (0.70, 1.30),
    "sucrose":       (0.60, 1.00),
    "saccharose":    (0.60, 1.00),
    "propylene":     (1.20, 2.00),
    "benzyl":        (2.00, 3.50),
    "lauryl":        (1.50, 2.50),
    "ethanol":       (0.80, 1.50),
    "default":       (2.00, 8.00),
}


def slugify(name: str) -> str:
    """Convertit nom_commun → slug URL Pharmacompass."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


class PriceParser(HTMLParser):
    """Extrait les patterns de prix USD depuis le HTML Pharmacompass."""

    def __init__(self):
        super().__init__()
        self._text_chunks = []

    def handle_data(self, data):
        stripped = data.strip()
        if stripped:
            self._text_chunks.append(stripped)

    def get_text(self) -> str:
        return " ".join(self._text_chunks)


def extract_prices_from_text(text: str) -> list[float]:
    """Extrait tous les prix USD trouvés dans le texte brut."""
    # Patterns: $12.50, $ 12.50, $1,234.50
    pattern = r"\$\s*([\d,]+\.?\d*)"
    matches = re.findall(pattern, text)
    prices = []
    for m in matches:
        try:
            val = float(m.replace(",", ""))
            if 0.01 < val < 50000:   # filtre valeurs aberrantes
                prices.append(val)
        except ValueError:
            pass
    return prices


def fetch_pharmacompass_price(nom_commun: str) -> tuple[float, float] | None:
    """
    Tente de scraper les prix depuis Pharmacompass.
    Retourne (prix_min_eur, prix_max_eur) ou None si échec.
    """
    slug = slugify(nom_commun)
    url  = f"https://www.pharmacompass.com/price/{slug}"

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                return None
            raw = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError) as e:
        print(f"  ⚠  Fetch échoué pour '{nom_commun}': {e}")
        return None

    parser = PriceParser()
    parser.feed(raw)
    text = parser.get_text()

    prices = extract_prices_from_text(text)
    if not prices:
        return None

    # Convertir USD → EUR, prendre min et max
    eur_prices = [round(p * USD_TO_EUR, 2) for p in prices]
    return (min(eur_prices), max(eur_prices))


def get_fallback_price(nom_commun: str) -> tuple[float, float]:
    """Retourne une fourchette de repli selon la catégorie."""
    name_lower = nom_commun.lower()
    for key, (mn, mx) in CATEGORY_FALLBACK.items():
        if key in name_lower:
            return (mn, mx)
    return CATEGORY_FALLBACK["default"]


def fetch_excipients_from_supabase() -> list[dict]:
    """Charge tous les excipients depuis Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/excipients?select=id,nom_commun&order=id"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    print("═" * 60)
    print("ChemistrySpot — Fetch Prix Pharmacompass")
    print("═" * 60)

    # Charger excipients
    print("\n📦 Chargement des excipients depuis Supabase...")
    try:
        excipients = fetch_excipients_from_supabase()
    except Exception as e:
        print(f"❌ Erreur Supabase: {e}")
        return

    print(f"   → {len(excipients)} excipients trouvés\n")

    results = []
    scraped_count  = 0
    fallback_count = 0

    for i, exc in enumerate(excipients, 1):
        nom = exc.get("nom_commun", "")
        eid = exc.get("id")

        print(f"[{i:2d}/{len(excipients)}] {nom:<35}", end="", flush=True)

        # Tenter scraping
        price_data = fetch_pharmacompass_price(nom)

        if price_data:
            prix_min, prix_max = price_data
            source = "Pharmacompass"
            scraped_count += 1
            print(f"✅  {prix_min:.2f}–{prix_max:.2f} €/kg  (scraped)")
        else:
            prix_min, prix_max = get_fallback_price(nom)
            source = "Estimate"
            fallback_count += 1
            print(f"⚡  {prix_min:.2f}–{prix_max:.2f} €/kg  (fallback)")

        results.append({
            "excipient_id": eid,
            "nom_commun":   nom,
            "prix_min":     prix_min,
            "prix_max":     prix_max,
            "devise":       "EUR",
            "source":       source,
            "grade":        "Pharmaceutical Grade",
        })

        # Délai pour éviter ban
        if i < len(excipients):
            time.sleep(DELAY_S)

    # Sauvegarder JSON
    os.makedirs("data", exist_ok=True)
    out_path = "data/prices.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "─" * 60)
    print(f"✅  {len(results)} excipients traités")
    print(f"   Scraped  : {scraped_count}")
    print(f"   Fallback : {fallback_count}")
    print(f"   Sauvegardé → {out_path}")
    print("─" * 60)
    print("\n➡  Prochaine étape : python scripts/insert_prices_supabase.py")


if __name__ == "__main__":
    main()
