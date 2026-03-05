#!/usr/bin/env python3
"""
ChemistrySpot — Générateur de sitemap.xml
Fetch les excipients depuis Supabase et génère sitemap.xml + robots.txt à la racine.

Usage: python scripts/generate_sitemap.py
Output: sitemap.xml, robots.txt (racine du projet)
"""

import json
import urllib.request
from datetime import date

# ── Config ──────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI"
BASE_URL     = "https://chemistryspot.com"
TODAY        = date.today().isoformat()

# ── Pages statiques ──────────────────────────────────────────────────────────
STATIC_PAGES = [
    {"loc": "/",                    "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/catalogue.html",      "priority": "0.9", "changefreq": "weekly"},
    {"loc": "/fournisseurs.html",   "priority": "0.8", "changefreq": "weekly"},
    {"loc": "/produit-detail.html", "priority": "0.7", "changefreq": "weekly"},
    {"loc": "/contact.html",        "priority": "0.5", "changefreq": "monthly"},
]


def fetch_excipients() -> list[dict]:
    """Charge id + nom_commun depuis Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/excipients?select=id,nom_commun&order=id"
    req = urllib.request.Request(url, headers={
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def build_sitemap(excipients: list[dict]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"']
    lines.append('        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
    lines.append('        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9')
    lines.append('        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">')

    # Pages statiques
    for p in STATIC_PAGES:
        lines.append(f"""  <url>
    <loc>{BASE_URL}{p['loc']}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{p['changefreq']}</changefreq>
    <priority>{p['priority']}</priority>
  </url>""")

    # Une entrée par excipient
    for exc in excipients:
        eid  = exc["id"]
        name = exc.get("nom_commun", "").replace("&", "&amp;").replace("<", "&lt;")
        lines.append(f"""  <url>
    <loc>{BASE_URL}/produit-detail.html?id={eid}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
    <!-- {name} -->
  </url>""")

    lines.append("</urlset>")
    return "\n".join(lines)


def build_robots() -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""


def main():
    print("═" * 60)
    print("ChemistrySpot — Génération sitemap.xml")
    print("═" * 60)

    print("\n📦 Chargement des excipients depuis Supabase...")
    try:
        excipients = fetch_excipients()
    except Exception as e:
        print(f"❌ Erreur Supabase : {e}")
        return

    print(f"   → {len(excipients)} excipients trouvés")

    sitemap = build_sitemap(excipients)
    robots  = build_robots()

    # Écrire à la racine du projet (scripts/ → ../)
    import os
    root = os.path.join(os.path.dirname(__file__), "..")

    sitemap_path = os.path.normpath(os.path.join(root, "sitemap.xml"))
    robots_path  = os.path.normpath(os.path.join(root, "robots.txt"))

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"\n✅  sitemap.xml → {sitemap_path}")
    print(f"   {len(STATIC_PAGES)} pages statiques + {len(excipients)} excipients = {len(STATIC_PAGES) + len(excipients)} URLs")

    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(robots)
    print(f"✅  robots.txt  → {robots_path}")
    print(f"\n🔗 Sitemap URL : {BASE_URL}/sitemap.xml")


if __name__ == "__main__":
    main()
