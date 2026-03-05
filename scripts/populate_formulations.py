#!/usr/bin/env python3
"""
populate_formulations.py
Insère 2-3 formulations de référence par excipient dans la table `formulations`.
Couvre 10 excipients prioritaires (IDs 10-14, 19, 21, 27, 36, 39).

Prérequis : exécuter scripts/create_formulations.sql dans Supabase SQL Editor.

Usage : python3 scripts/populate_formulations.py
"""

import json
import time
import urllib.request
import urllib.error

# ─── CONFIGURATION SUPABASE ──────────────────────────────────────────────────

SUPABASE_URL     = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SERVICE_ROLE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwi"
    "cm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTY1ODM5NCwiZXhwIjoyMDY3"
    "MjM0Mzk0fQ.dgU2hQsRW0kWKriCNwx_SMES5GWO25Wl7Y-jmes05b0"
)

HEADERS = {
    "apikey":        SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

TABLE_URL = f"{SUPABASE_URL}/rest/v1/formulations"
DELAY     = 0.10

# ─── DONNÉES DE FORMULATIONS ─────────────────────────────────────────────────
# Chaque entrée : excipient_id, nom_formulation, type_forme, role_excipient,
#                 concentration, pa_exemple, autres_excipients[], notes

FORMULATIONS = [

    # ── 10 · Lactose ─────────────────────────────────────────────────────────
    {
        "excipient_id": 10,
        "nom_formulation": "Poudre pour inhalation DPI — Salmétérol",
        "type_forme": "Poudre pour inhalation",
        "role_excipient": "Véhicule / Porteur",
        "concentration": "99 %",
        "pa_exemple": "Salmétérol xinafoate",
        "autres_excipients": [],
        "notes": "Le lactose micronisé (grade DPI) adhère au PA par forces de van der Waals puis se sépare lors de l'inhalation. Taille des particules porteuses : 50-150 µm.",
    },
    {
        "excipient_id": 10,
        "nom_formulation": "Comprimé Amoxicilline 500 mg",
        "type_forme": "Comprimé",
        "role_excipient": "Diluant",
        "concentration": "35 %",
        "pa_exemple": "Amoxicilline trihydrate",
        "autres_excipients": ["Croscarmellose sodium", "Stéarate de magnésium", "Silice colloïdale"],
        "notes": "Lactose monohydraté grade compression directe. Incompatibilité potentielle avec les amines primaires (réaction de Maillard) — surveiller à l'accélération.",
    },
    {
        "excipient_id": 10,
        "nom_formulation": "Gélule Vitamines B complexe",
        "type_forme": "Gélule",
        "role_excipient": "Diluant",
        "concentration": "55 %",
        "pa_exemple": "Thiamine HCl / Pyridoxine HCl / Cyanocobalamine",
        "autres_excipients": ["Cellulose microcristalline", "Stéarate de magnésium"],
        "notes": "Grade lactose spray-dried pour remplissage direct de gélules sans granulation. Surveiller la compatibilité avec B1 (sensible à l'humidité résiduelle).",
    },

    # ── 11 · Microcrystalline cellulose ──────────────────────────────────────
    {
        "excipient_id": 11,
        "nom_formulation": "Comprimé Metformine 500 mg — Compression directe",
        "type_forme": "Comprimé",
        "role_excipient": "Diluant / Liant",
        "concentration": "70 %",
        "pa_exemple": "Metformine HCl",
        "autres_excipients": ["Crospovidone", "Stéarate de magnésium", "Silice colloïdale"],
        "notes": "Grade Avicel PH-102 (taille ~100 µm). PA à forte dose (50 %), la MCC compense la faible compressibilité de la metformine. Dureté cible : 12-18 kP.",
    },
    {
        "excipient_id": 11,
        "nom_formulation": "Gélule Oméprazole 20 mg",
        "type_forme": "Gélule",
        "role_excipient": "Diluant",
        "concentration": "58 %",
        "pa_exemple": "Oméprazole",
        "autres_excipients": ["Croscarmellose sodium", "Mannitol", "Stéarate de magnésium"],
        "notes": "Grade PH-101 (taille ~50 µm) pour meilleure coulabilité en remplissage de gélules. pH alcalin nécessaire pour la stabilité de l'oméprazole.",
    },
    {
        "excipient_id": 11,
        "nom_formulation": "Pellets Pantoprazole LP — Noyau inerte",
        "type_forme": "Pellet / Granulé enrobé",
        "role_excipient": "Noyau inerte (support)",
        "concentration": "82 %",
        "pa_exemple": "Pantoprazole sodique",
        "autres_excipients": ["Éthylcellulose", "HPMC", "Talc"],
        "notes": "Sphéronisation MCC/eau (rapport 80:20), puis enrobage gastro-résistant. Taille des pellets : 700-900 µm. Permet la libération entérique.",
    },

    # ── 12 · Magnesium stearate ───────────────────────────────────────────────
    {
        "excipient_id": 12,
        "nom_formulation": "Comprimé Paracétamol 500 mg",
        "type_forme": "Comprimé",
        "role_excipient": "Lubrifiant",
        "concentration": "0,5 %",
        "pa_exemple": "Paracétamol",
        "autres_excipients": ["Cellulose microcristalline", "Amidon de maïs", "Povidone"],
        "notes": "Ajout en fin de mélange (2 min max). Sur-lubrification → réduction de la dureté et de la vitesse de dissolution. Temps de mélange validé en QC.",
    },
    {
        "excipient_id": 12,
        "nom_formulation": "Gélule Ibuprofène 200 mg",
        "type_forme": "Gélule",
        "role_excipient": "Lubrifiant",
        "concentration": "1 %",
        "pa_exemple": "Ibuprofène",
        "autres_excipients": ["Lactose monohydraté", "Cellulose microcristalline", "Croscarmellose sodium"],
        "notes": "Concentration plus élevée en gélule (vs comprimé) car friction avec les parois de la trémie de remplissage. Grade végétal disponible si requis.",
    },
    {
        "excipient_id": 12,
        "nom_formulation": "Comprimé Metformine LP 850 mg",
        "type_forme": "Comprimé à libération prolongée",
        "role_excipient": "Lubrifiant",
        "concentration": "0,75 %",
        "pa_exemple": "Metformine HCl",
        "autres_excipients": ["HPMC K100M", "Cellulose microcristalline", "Silice colloïdale"],
        "notes": "Matrice HPMC hydrophile. Le stéarate de magnésium doit être ajouté après le polymère pour ne pas enrober les particules de HPMC (risque de retard de libération).",
    },

    # ── 13 · Povidone ─────────────────────────────────────────────────────────
    {
        "excipient_id": 13,
        "nom_formulation": "Comprimé Aspirine 500 mg — Granulation humide",
        "type_forme": "Comprimé",
        "role_excipient": "Liant de granulation",
        "concentration": "3 %",
        "pa_exemple": "Acide acétylsalicylique",
        "autres_excipients": ["Amidon de maïs", "Talc", "Stéarate de magnésium"],
        "notes": "Solution de povidone K30 dans l'éthanol (5 % p/v). L'éthanol évite l'hydrolyse de l'aspirine vs eau. Séchage à 40 °C max (perte en eau ≤ 2 %).",
    },
    {
        "excipient_id": 13,
        "nom_formulation": "Comprimé Chlorure de potassium LP 600 mg",
        "type_forme": "Comprimé à libération prolongée",
        "role_excipient": "Liant",
        "concentration": "2 %",
        "pa_exemple": "Chlorure de potassium",
        "autres_excipients": ["Éthylcellulose", "Cire de carnauba", "Stéarate de magnésium"],
        "notes": "Matrice cire/éthylcellulose. Le PVP améliore la cohésion du granulé avant enrobage. Profil de libération : 70 % en 8 h (USP dissolution apparatus II).",
    },
    {
        "excipient_id": 13,
        "nom_formulation": "Solution antiseptique Bétadine 10 %",
        "type_forme": "Solution cutanée",
        "role_excipient": "Complexant / Vecteur",
        "concentration": "10 % (complexe PVP-I)",
        "pa_exemple": "Iode (complexé PVP)",
        "autres_excipients": ["Eau purifiée", "Glycérol", "Acide citrique"],
        "notes": "La povidone K90 complexe l'iode (1:1) pour libération contrôlée. La complexation réduit la toxicité de l'iode libre tout en maintenant l'activité antimicrobienne.",
    },

    # ── 14 · Talc ────────────────────────────────────────────────────────────
    {
        "excipient_id": 14,
        "nom_formulation": "Comprimé Magnésium 300 mg",
        "type_forme": "Comprimé",
        "role_excipient": "Lubrifiant / Anti-adhérent",
        "concentration": "2 %",
        "pa_exemple": "Oxyde de magnésium",
        "autres_excipients": ["Cellulose microcristalline", "Stéarate de magnésium", "Croscarmellose sodium"],
        "notes": "Association talc + stéarate de magnésium (ratio 4:1) pour synergie lubrifiante. Grade talc amiante-free contrôlé Ph.Eur. 2.4.28 obligatoire.",
    },
    {
        "excipient_id": 14,
        "nom_formulation": "Poudre cutanée pédiatrique",
        "type_forme": "Poudre pour application cutanée",
        "role_excipient": "Base absorbante / Excipient principal",
        "concentration": "95 %",
        "pa_exemple": "Oxyde de zinc (5 %)",
        "autres_excipients": ["Oxyde de zinc"],
        "notes": "Base talc minérale inerte, grande surface spécifique (absorption sudorale). Risque d'inhalation chez le nourrisson — conditionnement sécurisé obligatoire.",
    },
    {
        "excipient_id": 14,
        "nom_formulation": "Gélule Oméprazole 20 mg (granulés enrobés)",
        "type_forme": "Gélule",
        "role_excipient": "Anti-adhérent (enrobage pellets)",
        "concentration": "3 %",
        "pa_exemple": "Oméprazole",
        "autres_excipients": ["Éthylcellulose", "HPMC", "Cellulose microcristalline"],
        "notes": "Ajout dans le bain d'enrobage pour éviter l'agglomération des pellets lors du processus Wurster. Concentration contrôlée — excès de talc peut réduire la perméabilité de l'enrobage.",
    },

    # ── 19 · Mannitol ─────────────────────────────────────────────────────────
    {
        "excipient_id": 19,
        "nom_formulation": "Comprimé ODT Ondansétron 4 mg",
        "type_forme": "Comprimé orodispersible (ODT)",
        "role_excipient": "Diluant principal ODT",
        "concentration": "72 %",
        "pa_exemple": "Chlorhydrate d'ondansétron",
        "autres_excipients": ["Crospovidone", "Aspartam", "Menthol", "Stéarate de magnésium"],
        "notes": "Grade Pearlitol SD200 (spray-dried) pour compression directe. Faible hygroscopicité du mannitol = stabilité en ambiance humide. Désintégration buccale < 30 s.",
    },
    {
        "excipient_id": 19,
        "nom_formulation": "Lyophilisat IV Amphotéricine B",
        "type_forme": "Poudre pour solution injectable",
        "role_excipient": "Cryoprotecteur / Agent de masse",
        "concentration": "9 % (p/v en solution)",
        "pa_exemple": "Amphotéricine B",
        "autres_excipients": ["Désoxycholate de sodium", "Eau pour injection"],
        "notes": "Le mannitol cristallise lors de la lyophilisation (excipient cristallin) et protège la structure d'Ampho B par exclusion préférentielle. Cycle de lyophilisation critique.",
    },
    {
        "excipient_id": 19,
        "nom_formulation": "Poudre pour inhalation DPI — Fluticasone",
        "type_forme": "Poudre pour inhalation",
        "role_excipient": "Véhicule porteur",
        "concentration": "80 %",
        "pa_exemple": "Propionate de fluticasone",
        "autres_excipients": [],
        "notes": "Mannitol D50 = 100-150 µm (porteur) + PA micronisé D50 < 5 µm. Meilleure tolérance respiratoire que le lactose chez certains patients (pas de β-galactosidase requise).",
    },

    # ── 21 · Starch ──────────────────────────────────────────────────────────
    {
        "excipient_id": 21,
        "nom_formulation": "Comprimé Paracétamol 500 mg — Granulation humide",
        "type_forme": "Comprimé",
        "role_excipient": "Désintégrant / Diluant",
        "concentration": "10 % (désintégrant extragranulaire)",
        "pa_exemple": "Paracétamol",
        "autres_excipients": ["Cellulose microcristalline", "Povidone", "Stéarate de magnésium"],
        "notes": "Amidon de maïs préféré à l'amidon de blé (risque gluten). Doit être sec (HR < 12 %) avant compression. Efficacité désintégrante inférieure aux superdésintégrants modernes.",
    },
    {
        "excipient_id": 21,
        "nom_formulation": "Gélule Ibuprofène 200 mg",
        "type_forme": "Gélule",
        "role_excipient": "Diluant",
        "concentration": "25 %",
        "pa_exemple": "Ibuprofène",
        "autres_excipients": ["Lactose monohydraté", "Stéarate de magnésium", "Silice colloïdale"],
        "notes": "Amidon partiellement prégélatinisé (Starch 1500®) pour meilleure coulabilité sans granulation préalable. Compatible avec remplissage automatique de gélules.",
    },
    {
        "excipient_id": 21,
        "nom_formulation": "Pommade à l'oxyde de zinc (Lassar)",
        "type_forme": "Pommade",
        "role_excipient": "Base absorbante",
        "concentration": "30 %",
        "pa_exemple": "Oxyde de zinc (25 %) + Acide salicylique (2 %)",
        "autres_excipients": ["Oxyde de zinc", "Vaseline blanche", "Acide salicylique"],
        "notes": "L'amidon confère la consistance et absorbe les exsudats cutanés. Formulation historique (Pharmacopée Européenne). Pastèque : amidon + oxyde de zinc = phase particulaire.",
    },

    # ── 27 · Sodium lauryl sulfate ───────────────────────────────────────────
    {
        "excipient_id": 27,
        "nom_formulation": "Comprimé Spironolactone 100 mg",
        "type_forme": "Comprimé",
        "role_excipient": "Mouillant / Solubilisant",
        "concentration": "1 %",
        "pa_exemple": "Spironolactone",
        "autres_excipients": ["Lactose monohydraté", "Cellulose microcristalline", "Stéarate de magnésium"],
        "notes": "PA BCS classe II (faible solubilité, bonne perméabilité). Le SLS améliore la mouillabilité du PA hydrophobe en milieu gastrique, augmentant la dissolution et la biodisponibilité.",
    },
    {
        "excipient_id": 27,
        "nom_formulation": "Shampoing médicamenteux Kétoconazole 2 %",
        "type_forme": "Shampoing médicamenteux",
        "role_excipient": "Tensioactif nettoyant principal",
        "concentration": "15 %",
        "pa_exemple": "Kétoconazole",
        "autres_excipients": ["Cocamide DEA", "Chlorure de sodium", "Acide citrique"],
        "notes": "Association SLS (anionique) + cocamide DEA (amphotère) pour réduire l'irritation. pH ajusté à 5,5 pour compatibilité cutanée. Viscosité modulée par NaCl.",
    },
    {
        "excipient_id": 27,
        "nom_formulation": "Gélule Dutastéride 0,5 mg (dissolution forcée)",
        "type_forme": "Gélule molle",
        "role_excipient": "Mouillant / Solubilisant",
        "concentration": "0,5 %",
        "pa_exemple": "Dutastéride",
        "autres_excipients": ["Butyrate de glycérol monocaprylocaprate", "Butylhydroxytoluène"],
        "notes": "PA BCS classe II lipophile. Le SLS dans la phase de remplissage améliore la solubilisation in vivo. Concentration faible pour éviter l'hémolyse potentielle.",
    },

    # ── 36 · Hypromellose (HPMC) ─────────────────────────────────────────────
    {
        "excipient_id": 36,
        "nom_formulation": "Comprimé Métoprolol LP 100 mg — Matrice hydrophile",
        "type_forme": "Comprimé à libération prolongée",
        "role_excipient": "Agent de matrice LP",
        "concentration": "30 %",
        "pa_exemple": "Succinate de métoprolol",
        "autres_excipients": ["Cellulose microcristalline", "Stéarate de magnésium", "Silice colloïdale"],
        "notes": "Grade HPMC K100M (viscosité ~100 000 mPa·s). Contact eau → gel de surface → diffusion + érosion contrôlées. Libération sur 24 h. Paramètres critiques : taux HPMC et rapport PA/HPMC.",
    },
    {
        "excipient_id": 36,
        "nom_formulation": "Pelliculage aqueux Paracétamol 500 mg",
        "type_forme": "Comprimé enrobé",
        "role_excipient": "Agent filmogène (enrobage)",
        "concentration": "3 % (par rapport au noyau)",
        "pa_exemple": "Paracétamol",
        "autres_excipients": ["Dioxyde de titane", "Macrogol 400", "Talc"],
        "notes": "Grade HPMC E5 (faible viscosité) en solution aqueuse 8 %. Système équivalent Opadry II White. Température entrée air 60 °C, sortie 40 °C. Prise de masse cible : 3-4 %.",
    },
    {
        "excipient_id": 36,
        "nom_formulation": "Collyre substituts lacrymaux 0,3 %",
        "type_forme": "Solution ophtalmique",
        "role_excipient": "Viscosifiant / Agent de rétention",
        "concentration": "0,3–0,5 %",
        "pa_exemple": "Sans PA (larmes artificielles)",
        "autres_excipients": ["Chlorure de sodium", "Chlorure de potassium", "Chlorure de benzalkonium 0,01 %"],
        "notes": "HPMC E4M ou K4M en solution tamponnée pH 7,4 (phosphate). Viscosité 15-25 mPa·s pour prolonger le temps de contact cornéen. Osmolalité 285-310 mOsm/kg.",
    },

    # ── 39 · Benzalkonium chloride ───────────────────────────────────────────
    {
        "excipient_id": 39,
        "nom_formulation": "Collyre bêtabloquant — Timolol 0,5 %",
        "type_forme": "Solution ophtalmique",
        "role_excipient": "Conservateur antimicrobien",
        "concentration": "0,01 %",
        "pa_exemple": "Maléate de timolol",
        "autres_excipients": ["Monohydrogénophosphate disodique", "Dihydrogénophosphate monosodique", "NaCl"],
        "notes": "BAK à 0,01 % assure la stérilité multi-doses (Ph.Eur. 5.1.3 critères A). Risque de toxicité cornéenne à long terme → tendance aux préparations sans conservateur (ABAK®).",
    },
    {
        "excipient_id": 39,
        "nom_formulation": "Solution nasale décongestionnante — Oxymétazoline",
        "type_forme": "Solution nasale",
        "role_excipient": "Conservateur",
        "concentration": "0,02 %",
        "pa_exemple": "Chlorhydrate d'oxymétazoline",
        "autres_excipients": ["Phosphate de sodium", "Chlorure de sodium", "Eau purifiée"],
        "notes": "pH 5,5-6,5 pour compatibilité muqueuse nasale. BAK actif sur Pseudomonas aeruginosa et Staphylococcus aureus (spectre large). Inactivé par les savons et les anioniques.",
    },
    {
        "excipient_id": 39,
        "nom_formulation": "Solution auriculaire — Ciprofloxacine 0,3 %",
        "type_forme": "Solution auriculaire",
        "role_excipient": "Conservateur",
        "concentration": "0,015 %",
        "pa_exemple": "Chlorhydrate de ciprofloxacine",
        "autres_excipients": ["Acide lactique", "NaCl", "Eau purifiée"],
        "notes": "BAK à 0,015 % pour conservation du flacon multidose. pH 3,5-4,5 pour stabilité ciprofloxacine. Contre-indiqué en cas de perforation tympanique (toxicité cochlée).",
    },
]

# ─── VÉRIFICATION DE LA TABLE ────────────────────────────────────────────────

def check_table():
    url = f"{TABLE_URL}?select=id&limit=1"
    req = urllib.request.Request(url, headers={
        "apikey":        SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    })
    try:
        urllib.request.urlopen(req)
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "does not exist" in body or "42P01" in body:
            return False
        raise


def insert_formulation(payload):
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(TABLE_URL, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def clear_existing():
    """Supprime les lignes existantes pour éviter les doublons au re-run."""
    url = f"{TABLE_URL}?id=gte.1"
    req = urllib.request.Request(url, headers={
        "apikey":        SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Prefer":        "return=minimal",
    }, method="DELETE")
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(f"  Avertissement suppression : {e.read().decode()[:100]}")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("ChemistrySpot — Populate Formulations")
    print("=" * 50)

    print("\n[1/3] Vérification de la table formulations...")
    if not check_table():
        print("\n  TABLE MANQUANTE. Exécutez d'abord dans Supabase SQL Editor :")
        print("  ─" * 30)
        with open("scripts/create_formulations.sql") as f:
            print(f.read())
        print("  Puis relancez ce script.")
        return
    print("  Table détectée.")

    print("\n[2/3] Suppression des données existantes (idempotent)...")
    clear_existing()
    print("  OK.")

    print(f"\n[3/3] Insertion de {len(FORMULATIONS)} formulations...")
    ok = err = 0
    for f in FORMULATIONS:
        exc_id = f["excipient_id"]
        status, error = insert_formulation(f)
        if status in (200, 201):
            print(f"  [{exc_id:2}] OK — {f['nom_formulation'][:55]}")
            ok += 1
        else:
            print(f"  [{exc_id:2}] ERREUR {status} — {error[:80] if error else ''}")
            err += 1
        time.sleep(DELAY)

    print(f"\nRésultat : {ok} OK, {err} erreur(s) sur {len(FORMULATIONS)} formulations.")


if __name__ == "__main__":
    main()
