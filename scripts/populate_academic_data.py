#!/usr/bin/env python3
"""
populate_academic_data.py
Remplit les colonnes académiques de la table `excipients` Supabase pour les 50 excipients.

Colonnes mises à jour :
  - categorie                text     (ex. "Diluant", "Lubrifiant")
  - formes_pharmaceutiques   text[]   (ex. ["Comprimé", "Gélule"])
  - pharmacopees             text[]   (ex. ["Ph.Eur.", "USP", "JP"])
  - concentrations_typiques  text     (ex. "65–85 % (comprimé direct)")
  - mecanisme                text     (mécanisme d'action court)

Prérequis : exécuter scripts/add_academic_columns.sql dans Supabase SQL Editor.

Usage : python3 scripts/populate_academic_data.py
"""

import json
import time
import urllib.request
import urllib.error

# ─── CONFIGURATION SUPABASE ──────────────────────────────────────────────────

SUPABASE_URL      = "https://jkaffpgqbyhuihvyvtld.supabase.co"
SERVICE_ROLE_KEY  = (
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

TABLE_URL = f"{SUPABASE_URL}/rest/v1/excipients"
DELAY     = 0.12   # secondes entre chaque PATCH

# ─── DONNÉES ACADÉMIQUES (50 excipients, IDs 10–59) ──────────────────────────

ACADEMIC_DATA = {
    10: {  # Lactose
        "categorie": "Diluant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Poudre pour inhalation"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "65–85 % (compression directe) ; 50–80 % (gélule)",
        "mecanisme": "Diluant inerte soluble favorisant la désintégration par dissolution rapide en milieu aqueux gastrique.",
    },
    11: {  # Microcrystalline cellulose
        "categorie": "Diluant / Liant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Pellet"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "20–90 % (compression directe) ; 10–30 % (liant granulation)",
        "mecanisme": "Structure fibreuse poreuse absorbant l'eau et créant une expansion mécanique lors de la désintégration par rupture des liaisons H inter-particules.",
    },
    12: {  # Magnesium stearate
        "categorie": "Lubrifiant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Poudre"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,25–1 % (comprimé) ; 0,5–2 % (gélule)",
        "mecanisme": "Film monomoléculaire hydrophobe sur les particules réduisant la friction avec les outils de compression et facilitant l'éjection.",
    },
    13: {  # Povidone (PVP)
        "categorie": "Liant",
        "formes_pharmaceutiques": ["Comprimé", "Solution orale", "Collyre"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,5–5 % (liant granulation humide) ; 1–10 % (complexant)",
        "mecanisme": "Polymère hygroscopique formant des ponts hydrogène avec le PA, améliorant sa solubilité et sa stabilité chimique.",
    },
    14: {  # Talc
        "categorie": "Lubrifiant",
        "formes_pharmaceutiques": ["Comprimé", "Poudre cutanée", "Gélule"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "1–5 % (lubrifiant) ; 5–30 % (poudre cutanée)",
        "mecanisme": "Silicate de magnésium lamellaire réduisant l'adhérence et la friction lors de la compression par interposition entre particules.",
    },
    15: {  # Titanium dioxide
        "categorie": "Opacifiant",
        "formes_pharmaceutiques": ["Comprimé enrobé", "Gélule", "Crème"],
        "pharmacopees": ["Ph.Eur.", "USP"],
        "concentrations_typiques": "0,5–2 % (enrobage) ; 5–25 % (préparations dermatologiques)",
        "mecanisme": "Opacifiant par réflexion et diffusion de la lumière visible, protège le PA de la photolyse. Grade E171 soumis à restriction EU depuis 2022.",
    },
    16: {  # Glycerol
        "categorie": "Humectant / Solvant",
        "formes_pharmaceutiques": ["Solution orale", "Suppositoire", "Crème", "Collyre"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "≤ 30 % (humectant) ; 100 % (suppositoire glycériné)",
        "mecanisme": "Polyol hygroscopique abaissant l'activité thermodynamique de l'eau, prévenant la déshydratation et améliorant la plasticité des formes semi-solides.",
    },
    17: {  # Purified water
        "categorie": "Solvant",
        "formes_pharmaceutiques": ["Toutes formes aqueuses"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "Solvant principal selon la formulation",
        "mecanisme": "Solvant universel polaire dissolvant les solutés ioniques et polaires par solvatation et formation de liaisons hydrogène.",
    },
    18: {  # Ethanol
        "categorie": "Solvant / Conservateur",
        "formes_pharmaceutiques": ["Solution orale", "Teinture", "Solution cutanée", "Solution injectable"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "5–20 % (co-solvant oral) ; 60–90 % (antiseptique)",
        "mecanisme": "Co-solvant amphiphile augmentant la solubilité des PA lipophiles ; dénature les protéines membranaires des micro-organismes à ≥ 60 %.",
    },
    19: {  # Mannitol
        "categorie": "Diluant / Édulcorant",
        "formes_pharmaceutiques": ["Comprimé ODT", "Lyophilisat injectable", "Poudre pour inhalation"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "10–90 % (comprimé ODT) ; 2,5–20 % (solution IV)",
        "mecanisme": "Polyol non métabolisé, osmotiquement actif ; cryo-protecteur en lyophilisation par vitrification et prévention des cristaux de glace intra-protéiques.",
    },
    20: {  # Sorbitol
        "categorie": "Diluant / Édulcorant",
        "formes_pharmaceutiques": ["Sirop", "Suspension orale", "Comprimé à mâcher"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "25–70 % (sirop) ; 10–30 % (comprimé à mâcher)",
        "mecanisme": "Polyol hygroscopique et osmotiquement actif ; édulcorant par stimulation des récepteurs du goût sucré sans métabolisation hépatique significative.",
    },
    21: {  # Starch
        "categorie": "Diluant / Désintégrant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Poudre"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "3–15 % (désintégrant) ; 5–20 % (liant) ; 40–80 % (diluant)",
        "mecanisme": "Gonflement par absorption d'eau entre les granules d'amidon, brisant la cohésion du comprimé par expansion volumique.",
    },
    22: {  # Stearic acid
        "categorie": "Lubrifiant",
        "formes_pharmaceutiques": ["Comprimé", "Suppositoire", "Crème"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "1–3 % (lubrifiant) ; 1–20 % (base crème)",
        "mecanisme": "Acide gras saturé formant un film hydrophobe réduisant les forces de friction lors de l'éjection des comprimés.",
    },
    23: {  # Citric acid
        "categorie": "Acidifiant / Tampon",
        "formes_pharmaceutiques": ["Comprimé effervescent", "Solution orale", "Solution injectable"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "10–40 % (effervescent) ; 0,1–2 % (tampon)",
        "mecanisme": "Acide tricarboxylique chélatant les ions métalliques, tamponnant le pH, et réagissant avec le bicarbonate pour libérer CO₂ dans les formes effervescentes.",
    },
    24: {  # Sucrose
        "categorie": "Diluant / Édulcorant",
        "formes_pharmaceutiques": ["Sirop", "Comprimé enrobé sucré", "Poudre pour solution"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "50–67 % (sirop) ; 60–80 % (enrobage sucré)",
        "mecanisme": "Disaccharide formant des solutions visqueuses protégeant le PA de l'hydrolyse, édulcorant par interaction avec les récepteurs T1R2/T1R3.",
    },
    25: {  # Propylene glycol
        "categorie": "Solvant / Humectant",
        "formes_pharmaceutiques": ["Solution injectable", "Solution orale", "Crème", "Gel"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "10–25 % (co-solvant injectable) ; 1–15 % (humectant topique)",
        "mecanisme": "Diol amphiphile abaissant la tension superficielle de l'eau et solubilisant les PA hydrophobes par co-solvatation. Dose IV ≤ 50 mg/kg/j.",
    },
    26: {  # Benzyl alcohol
        "categorie": "Conservateur",
        "formes_pharmaceutiques": ["Solution injectable", "Solution cutanée"],
        "pharmacopees": ["Ph.Eur.", "USP"],
        "concentrations_typiques": "0,9–2 % (conservateur injectable) ; jusqu'à 10 % (solvant)",
        "mecanisme": "Alcool aromatique perturbant les membranes phospholipidiques bactériennes et fongistatique par dénaturation protéique intracellulaire.",
    },
    27: {  # Sodium lauryl sulfate (SLS)
        "categorie": "Surfactant",
        "formes_pharmaceutiques": ["Comprimé", "Shampooing médicamenteux", "Crème"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,5–2 % (mouillant comprimé) ; 1–3 % (nettoyant topique)",
        "mecanisme": "Tensioactif anionique formant des micelles amphiphiles solubilisant les PA lipophiles et réduisant l'angle de contact eau/solide.",
    },
    28: {  # Calcium stearate
        "categorie": "Lubrifiant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Poudre"],
        "pharmacopees": ["Ph.Eur.", "USP"],
        "concentrations_typiques": "0,5–2 %",
        "mecanisme": "Sel de calcium d'acide stéarique formant un film lubrifiant réduisant l'adhésion aux outils de compression et facilitant l'éjection.",
    },
    29: {  # Dicalcium phosphate
        "categorie": "Diluant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "5–80 %",
        "mecanisme": "Diluant minéral insoluble à compressibilité élevée, compatible avec la majorité des PA et stable à l'humidité et à la chaleur.",
    },
    30: {  # Calcium carbonate
        "categorie": "Diluant / Tampon",
        "formes_pharmaceutiques": ["Comprimé à mâcher", "Suspension orale", "Comprimé"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "5–80 % (diluant) ; 80–95 % (antiacide)",
        "mecanisme": "Carbonate basique neutralisant l'HCl gastrique (CaCO₃ + 2HCl → CaCl₂ + H₂O + CO₂) ; diluant par masse minérale inerte et économique.",
    },
    31: {  # Sodium chloride
        "categorie": "Agent tonifiant",
        "formes_pharmaceutiques": ["Solution injectable", "Solution ophtalmique", "Solution nasale", "Comprimé"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,9 % (isotonie) ; 0,1–0,9 % (ajustement osmolalité)",
        "mecanisme": "Électrolyte ajustant l'osmolalité des solutions aqueuses par dissociation ionique Na⁺/Cl⁻, maintenant l'intégrité cellulaire.",
    },
    32: {  # Potassium chloride
        "categorie": "Agent tonifiant",
        "formes_pharmaceutiques": ["Solution injectable", "Comprimé", "Solution orale"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,015–0,3 % (isotonie) ; jusqu'à 0,15 % (injectable)",
        "mecanisme": "Électrolyte apportant des ions K⁺ et modulant le gradient osmotique ; agent de relargage dans les matrices hydrophiles.",
    },
    33: {  # Zinc oxide
        "categorie": "Opacifiant / Protecteur cutané",
        "formes_pharmaceutiques": ["Crème", "Pommade", "Pâte"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "2–25 % (dermatologique)",
        "mecanisme": "Opacifiant et astringent formant un film protecteur cutané ; activité antibactérienne par libération d'ions Zn²⁺ inhibant les enzymes bactériennes.",
    },
    34: {  # Colloidal silicon dioxide
        "categorie": "Antiagglomérant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Poudre", "Gel"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,1–0,5 % (antiagglomérant) ; 2–10 % (gel thixotrope)",
        "mecanisme": "Silice amorphe nanoscopique adsorbant sur les particules de poudre, créant des forces répulsives électrostatiques améliorant la coulabilité.",
    },
    35: {  # Hydroxypropyl cellulose (HPC)
        "categorie": "Liant / Enrobant",
        "formes_pharmaceutiques": ["Comprimé", "Film orodispersible", "Patch transdermique", "Solution orale"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "2–6 % (liant granulation) ; 5–25 % (pelliculage)",
        "mecanisme": "Polymère cellulosique thermosensible (T_gel ~40 °C) formant un réseau viscoélastique en solution et adhérant aux surfaces par liaisons hydrogène.",
    },
    36: {  # Hypromellose (HPMC)
        "categorie": "Liant / Enrobant / Libération prolongée",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Collyre", "Solution orale"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "2–5 % (enrobage) ; 10–80 % (matrice prolongée) ; 0,5–1 % (collyre)",
        "mecanisme": "Matrice hydrophile gonflant par absorption d'eau, formant un gel de diffusion contrôlant la libération du PA par érosion et diffusion graduelles.",
    },
    37: {  # Macrogol 4000 (PEG 4000)
        "categorie": "Plastifiant / Base de suppositoire",
        "formes_pharmaceutiques": ["Suppositoire", "Comprimé", "Crème", "Solution orale laxative"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "50–100 % (base suppositoire) ; 2–15 % (plastifiant enrobage)",
        "mecanisme": "Polymère hydrosoluble osmotiquement actif retenant l'eau dans le côlon (laxatif osmotique) et plastifiant les films polymériques par insertion entre chaînes.",
    },
    38: {  # Polysorbate 80
        "categorie": "Surfactant / Émulsifiant",
        "formes_pharmaceutiques": ["Solution injectable", "Émulsion", "Solution orale", "Collyre"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,01–0,5 % (injectable) ; 1–15 % (solubilisant oral)",
        "mecanisme": "Tensioactif non ionique amphiphile formant des micelles (HLB = 15) stabilisant les émulsions H/E et solubilisant les PA lipophiles.",
    },
    39: {  # Benzalkonium chloride
        "categorie": "Conservateur",
        "formes_pharmaceutiques": ["Collyre", "Solution nasale", "Solution cutanée"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,004–0,02 % (ophtalmique) ; 0,01–0,1 % (topique)",
        "mecanisme": "Ammonium quaternaire cationique détruisant les membranes bactériennes par interaction électrostatique avec les phospholipides chargés négativement.",
    },
    40: {  # Croscarmellose sodium
        "categorie": "Désintégrant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "1–5 % (intragranulaire) ; 2–5 % (extragranulaire)",
        "mecanisme": "Réseau de carboxyméthylcellulose réticulée absorbant 4–8× son poids en eau, générant une force d'expansion mécanique désintégrante.",
    },
    41: {  # Crospovidone
        "categorie": "Désintégrant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule", "Comprimé ODT"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "2–5 %",
        "mecanisme": "PVP réticulé insoluble capturant l'eau par capillarité et créant une pression de gonflement brisant la structure compacte du comprimé.",
    },
    42: {  # Sodium starch glycolate
        "categorie": "Désintégrant",
        "formes_pharmaceutiques": ["Comprimé", "Gélule"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "2–8 %",
        "mecanisme": "Amidon carboxyméthylé réticulé gonflant jusqu'à 300 % de son volume en présence d'eau, fragmentant le comprimé par expansion rapide.",
    },
    43: {  # Gelatin
        "categorie": "Liant / Enveloppe",
        "formes_pharmaceutiques": ["Gélule dure", "Gélule molle", "Comprimé"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "1–3 % (liant) ; enveloppe gélule (masse totale)",
        "mecanisme": "Protéine collagène dénaturée formant un gel thermoréversible à 35–40 °C, se dissolvant dans le liquide gastrique à 37 °C.",
    },
    44: {  # Acacia (Gum arabic)
        "categorie": "Liant / Émulsifiant",
        "formes_pharmaceutiques": ["Comprimé", "Émulsion orale", "Sirop"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "1–5 % (liant) ; 10–35 % (émulsifiant)",
        "mecanisme": "Polysaccharide complexe formant des films interfaciaux stables autour des gouttelettes d'huile, stabilisant les émulsions de type H/E.",
    },
    45: {  # Xanthan gum
        "categorie": "Agent de suspension / Viscosifiant",
        "formes_pharmaceutiques": ["Suspension orale", "Gel", "Crème", "Comprimé à libération prolongée"],
        "pharmacopees": ["Ph.Eur.", "USP"],
        "concentrations_typiques": "0,1–1 % (suspension) ; 0,5–2 % (gel)",
        "mecanisme": "Polysaccharide à comportement rhéofluidifiant (pseudo-plastique), formant un réseau de chaînes imbriquées suspendant les particules sans sédimentation.",
    },
    46: {  # Carboxymethylcellulose sodium
        "categorie": "Épaississant / Liant",
        "formes_pharmaceutiques": ["Suspension orale", "Gel", "Collyre", "Comprimé"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,1–1,5 % (épaississant) ; 1–6 % (liant granulation)",
        "mecanisme": "Cellulose carboxyméthylée anionique gonflant en milieu aqueux, formant des solutions visqueuses stabilisant les suspensions par répulsion électrostatique.",
    },
    47: {  # Ethyl cellulose
        "categorie": "Enrobant / Libération prolongée",
        "formes_pharmaceutiques": ["Comprimé à libération prolongée", "Granulé enrobé", "Microparticule"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "3–20 % (enrobage prolongé) ; jusqu'à 40 % (matrice)",
        "mecanisme": "Cellulose éthérifiée hydrophobe imperméable à l'eau, contrôlant la diffusion du PA à travers une membrane semi-perméable poreuse.",
    },
    48: {  # Shellac
        "categorie": "Enrobant gastro-résistant",
        "formes_pharmaceutiques": ["Comprimé gastro-résistant", "Granulé enrobé"],
        "pharmacopees": ["Ph.Eur.", "USP"],
        "concentrations_typiques": "5–30 % (enrobage gastro-résistant)",
        "mecanisme": "Résine naturelle insoluble à pH gastrique (< 5) mais soluble à pH intestinal (> 7,3), permettant le transit gastrique intact du PA.",
    },
    49: {  # Carbomer
        "categorie": "Gélifiant / Bioadhésif",
        "formes_pharmaceutiques": ["Gel", "Crème", "Comprimé bioadhésif"],
        "pharmacopees": ["Ph.Eur.", "USP"],
        "concentrations_typiques": "0,1–2 % (gel topique) ; 5–40 % (comprimé bioadhésif)",
        "mecanisme": "Polymère acrylique réticulé expansant à pH > 5 par ionisation des groupes COOH, formant un réseau gel rigide et adhérant aux muqueuses.",
    },
    50: {  # Sodium bicarbonate
        "categorie": "Agent effervescent / Alcalinisant",
        "formes_pharmaceutiques": ["Comprimé effervescent", "Solution orale", "Solution injectable"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "10–50 % (effervescent) ; 0,1–5 % (alcalinisant)",
        "mecanisme": "Base faible réagissant avec les acides organiques (citrique, tartrique) pour libérer CO₂ créant l'effervescence ; neutralise l'acidité gastrique.",
    },
    51: {  # Ascorbic acid
        "categorie": "Antioxydant",
        "formes_pharmaceutiques": ["Comprimé", "Solution injectable", "Solution orale"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,01–0,1 % (antioxydant) ; 250–1 000 mg/unité (dose vitaminique)",
        "mecanisme": "Antioxydant par donation d'électrons aux radicaux libres et réduction des ions métalliques oxydants (Fe³⁺ → Fe²⁺) ; régénéré par le glutathion.",
    },
    52: {  # Alpha-tocopherol
        "categorie": "Antioxydant",
        "formes_pharmaceutiques": ["Capsule molle", "Solution injectable", "Crème", "Émulsion"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,001–0,1 % (antioxydant huiles) ; 50–1 000 mg (dose vitaminique)",
        "mecanisme": "Antioxydant liposoluble piégeant les radicaux peroxydes lipidiques dans les membranes et émulsions, brisant la chaîne d'auto-oxydation.",
    },
    53: {  # Butylated hydroxytoluene (BHT)
        "categorie": "Antioxydant",
        "formes_pharmaceutiques": ["Huile pour injection", "Capsule molle", "Crème"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,0001–0,1 %",
        "mecanisme": "Phénol encombré stériquement cédant son atome H aux radicaux peroxyles, interrompant la propagation de la peroxydation lipidique.",
    },
    54: {  # Methylparaben
        "categorie": "Conservateur",
        "formes_pharmaceutiques": ["Solution orale", "Solution injectable", "Crème"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,02–0,3 %",
        "mecanisme": "Ester de l'acide para-hydroxybenzoïque inhibant la croissance microbienne par perturbation des membranes cellulaires et inhibition enzymatique.",
    },
    55: {  # Propylparaben
        "categorie": "Conservateur",
        "formes_pharmaceutiques": ["Solution orale", "Crème", "Solution injectable"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,01–0,15 % (seul) ; 0,02–0,05 % (en combinaison avec méthylparaben)",
        "mecanisme": "Parabène lipophile plus actif contre les moisissures que le méthylparaben ; synergie par combinaison des propriétés hydro/lipophiles.",
    },
    56: {  # Sorbic acid
        "categorie": "Conservateur",
        "formes_pharmaceutiques": ["Solution orale", "Crème", "Gel"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,05–0,2 %",
        "mecanisme": "Acide gras insaturé inhibant les enzymes fongiques (énoyl-CoA hydratase) et bactériennes ; actif sous forme non dissociée à pH < 4,5.",
    },
    57: {  # Potassium sorbate
        "categorie": "Conservateur",
        "formes_pharmaceutiques": ["Solution orale", "Sirop", "Crème"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "0,1–0,25 %",
        "mecanisme": "Sel de potassium de l'acide sorbique libérant la forme acide active à pH < 4,5, inhibant la croissance fongique et bactérienne.",
    },
    58: {  # Cetyl alcohol
        "categorie": "Émulsifiant / Émollient",
        "formes_pharmaceutiques": ["Crème", "Lotion", "Pommade"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "2–10 %",
        "mecanisme": "Alcool gras amphiphile formant une phase cristalline liquide dans les émulsions, stabilisant l'interface H/E et émollient par film lipidique cutané.",
    },
    59: {  # Mineral oil
        "categorie": "Lubrifiant / Émollient",
        "formes_pharmaceutiques": ["Émulsion", "Laxatif oral", "Crème", "Solution nasale"],
        "pharmacopees": ["Ph.Eur.", "USP", "JP"],
        "concentrations_typiques": "1–32 % (émulsion) ; 15–45 mL (laxatif oral)",
        "mecanisme": "Hydrocarbure inerte non absorbé formant un film lubrifiant sur les muqueuses et retardant l'absorption d'eau du côlon (laxatif lubrifiant).",
    },
}

# ─── VÉRIFICATION DES COLONNES ───────────────────────────────────────────────

def check_columns():
    """Vérifie que les colonnes académiques existent dans la table."""
    url = f"{TABLE_URL}?select=categorie,formes_pharmaceutiques,pharmacopees,concentrations_typiques,mecanisme&limit=1"
    req = urllib.request.Request(url, headers={
        "apikey":        SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    })
    try:
        urllib.request.urlopen(req)
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "does not exist" in body or "42703" in body:
            return False
        raise


def patch_excipient(excipient_id, payload):
    url = f"{TABLE_URL}?id=eq.{excipient_id}"
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=HEADERS, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("ChemistrySpot — Populate Academic Data")
    print("=" * 50)

    # Vérification préalable des colonnes
    print("\n[1/2] Vérification des colonnes dans Supabase...")
    if not check_columns():
        print("\n  COLONNES MANQUANTES. Exécutez d'abord dans Supabase SQL Editor :")
        print("  ─" * 30)
        print("""
  ALTER TABLE excipients
    ADD COLUMN IF NOT EXISTS categorie                text,
    ADD COLUMN IF NOT EXISTS formes_pharmaceutiques   text[],
    ADD COLUMN IF NOT EXISTS pharmacopees             text[],
    ADD COLUMN IF NOT EXISTS concentrations_typiques  text,
    ADD COLUMN IF NOT EXISTS mecanisme                text;
""")
        print("  Puis relancez ce script.")
        return
    print("  Colonnes détectées.")

    # Mise à jour des 50 excipients
    print(f"\n[2/2] Mise à jour de {len(ACADEMIC_DATA)} excipients...")
    ok = err = 0
    for exc_id, payload in sorted(ACADEMIC_DATA.items()):
        status, error = patch_excipient(exc_id, payload)
        if status in (200, 204):
            print(f"  [{exc_id:2}] OK")
            ok += 1
        else:
            print(f"  [{exc_id:2}] ERREUR {status} — {error}")
            err += 1
        time.sleep(DELAY)

    print(f"\nRésultat : {ok} OK, {err} erreur(s) sur {len(ACADEMIC_DATA)} excipients.")


if __name__ == "__main__":
    main()
