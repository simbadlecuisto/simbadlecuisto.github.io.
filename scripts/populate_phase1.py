#!/usr/bin/env python3
"""
ChemistrySpot — Phase 1 : Peuplement colonnes avancées pour les 10 excipients prioritaires
Requiert que migrate_phase1.sql ait été exécuté dans Supabase SQL Editor.
Usage : python3 scripts/populate_phase1.py
"""

import urllib.request, urllib.error, json, sys

SUPABASE_URL     = 'https://jkaffpgqbyhuihvyvtld.supabase.co'
SERVICE_ROLE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3MjM0Mzk0fQ.dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0'

HEADERS = {
    'apikey':        SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}

# ── Données pharmaceutiques réalistes ──────────────────────────────────────
EXCIPIENTS = [
    {
        'id': 11,  # Microcrystalline cellulose (MCC)
        'grades':               ['PH-101', 'PH-102', 'PH-105', 'PH-200', 'PH-301', 'PH-302',
                                 'Avicel PH-101', 'Avicel PH-102', 'Comprecel', 'Vivapur'],
        'taille_particule_min': 20,
        'taille_particule_max': 200,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP', 'GMP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Inde', 'Chine', 'USA'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=11',
    },
    {
        'id': 10,  # Lactose monohydraté
        'grades':               ['100M', '200M', '300M', 'Anhydre DT', 'FlowLac 90',
                                 'Tablettose 80', 'Lactochem', 'SuperTab 30GR'],
        'taille_particule_min': 40,
        'taille_particule_max': 315,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Inde'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=10',
    },
    {
        'id': 19,  # Mannitol
        'grades':               ['Pearlitol 25C', 'Pearlitol 100SD', 'Pearlitol 160C',
                                 'Pearlitol 200SD', 'Mannidex 16700', 'DC grade', 'Granulé'],
        'taille_particule_min': 25,
        'taille_particule_max': 400,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Chine', 'Inde'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=19',
    },
    {
        'id': 12,  # Magnesium stearate (Stéarate de magnésium)
        'grades':               ['Végétal', 'Animal', 'Non-bovine', 'HyQual',
                                 'Ligamed MF-2-V', 'Mg-St Extra Fine'],
        'taille_particule_min': 5,
        'taille_particule_max': 50,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP', 'GMP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Inde', 'Chine', 'USA'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=12',
    },
    {
        'id': 36,  # Hypromellose (HPMC)
        'grades':               ['E3', 'E5', 'E15', 'E50', 'K4M', 'K15M', 'K100M',
                                 'HPMC 2910', 'HPMC 2208', 'Methocel K4M'],
        'taille_particule_min': 100,
        'taille_particule_max': 500,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Inde', 'Chine'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=36',
    },
    {
        'id': 13,  # Povidone (PVP)
        'grades':               ['K17', 'K25', 'K30', 'K60', 'K90',
                                 'Kollidon 30', 'Plasdone K-29/32', 'PVP VA64'],
        'taille_particule_min': 50,
        'taille_particule_max': 300,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg'],
        'origine':              ['Europe', 'Inde', 'Chine'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=13',
    },
    {
        'id': 40,  # Croscarmellose sodium
        'grades':               ['Type A', 'Ac-Di-Sol', 'Primellose', 'Nymcel ZSX',
                                 'Explocel', 'standard pharma'],
        'taille_particule_min': 30,
        'taille_particule_max': 200,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg'],
        'origine':              ['Europe', 'Inde', 'Chine'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=40',
    },
    {
        'id': 21,  # Starch (Amidon)
        'grades':               ['Maïs', 'Blé', 'Pomme de terre', 'Riz',
                                 'Starch 1500', 'Lycatab C', 'Pregelatinized'],
        'taille_particule_min': 5,
        'taille_particule_max': 100,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Inde', 'Chine', 'USA'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=21',
    },
    {
        'id': 14,  # Talc
        'grades':               ['Luzenac Pharma S', 'Luzenac Pharma M', 'Luzenac Pharma L',
                                 'IT Extra', 'talc pharma grade'],
        'taille_particule_min': 3,
        'taille_particule_max': 45,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'JP', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Inde', 'Chine'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=14',
    },
    {
        'id': 28,  # Calcium stearate (Stéarate de calcium)
        'grades':               ['Végétal', 'Non-bovine', 'HyQual Ca', 'pharma grade'],
        'taille_particule_min': 5,
        'taille_particule_max': 60,
        'certifications':       ['Ph.Eur.', 'USP/NF', 'BP'],
        'conditionnements':     ['1 kg', '5 kg', '25 kg', 'Big Bag 500 kg'],
        'origine':              ['Europe', 'Inde', 'Chine'],
        'stock_disponible':     True,
        'lien_produit_direct':  'https://chemistryspot.com/produit-detail.html?id=28',
    },
]


def patch_excipient(exc_id, data):
    url = f'{SUPABASE_URL}/rest/v1/excipients?id=eq.{exc_id}'
    body = json.dumps(data).encode()
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method='PATCH')
    try:
        urllib.request.urlopen(req)
        return True, None
    except urllib.error.HTTPError as e:
        return False, e.read().decode()


def verify_columns():
    """Vérifie que les nouvelles colonnes existent (PATCH sur un excipient non-prioritaire échouerait sinon)"""
    ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI'
    url = f'{SUPABASE_URL}/rest/v1/excipients?select=id,grades,certifications,stock_disponible&limit=1'
    req = urllib.request.Request(url, headers={'apikey': ANON, 'Authorization': f'Bearer {ANON}'})
    try:
        data = json.loads(urllib.request.urlopen(req).read())
        return True
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        if '42703' in msg:  # column does not exist
            return False
        return True  # autre erreur, on continue


if __name__ == '__main__':
    print('── ChemistrySpot Phase 1 — Populate excipients ──')

    # Vérification des colonnes
    print('\n[1/3] Vérification des nouvelles colonnes...')
    if not verify_columns():
        print('❌ Les colonnes n\'existent pas encore.')
        print('   → Exécute scripts/migrate_phase1.sql dans Supabase SQL Editor d\'abord.')
        sys.exit(1)
    print('✅ Colonnes détectées.')

    # Peuplement
    print(f'\n[2/3] Peuplement de {len(EXCIPIENTS)} excipients...')
    ok = 0
    for exc in EXCIPIENTS:
        exc_id = exc.pop('id')
        success, err = patch_excipient(exc_id, exc)
        status = '✅' if success else '❌'
        label  = next((e['nom_commun'] for e in []), f'id={exc_id}')
        print(f'  {status} id={exc_id} — {"OK" if success else err[:80]}')
        if success:
            ok += 1

    # Vérification finale
    print(f'\n[3/3] Résultat : {ok}/{len(EXCIPIENTS)} excipients mis à jour.')

    if ok == len(EXCIPIENTS):
        print('\n🎉 Étape 1 terminée avec succès.')
    else:
        print('\n⚠️  Certaines mises à jour ont échoué. Vérifie les erreurs ci-dessus.')
        sys.exit(1)
