#!/usr/bin/env python3
"""
enrich_manual_b3.py — Batch 3 (IDs 40-59)
Fusionne les données PubChem avec les métadonnées pharmaceutiques curées.
Sortie : data/excipients_complets_b3.json

Usage : python3 scripts/enrich_manual_b3.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

INPUT_FILE  = Path(__file__).parent / "data" / "excipients_pubchem_b3.json"
OUTPUT_FILE = Path(__file__).parent / "data" / "excipients_complets_b3.json"

# ─────────────────────────────────────────────
# MÉTADONNÉES PHARMACEUTIQUES — BATCH 3
# ─────────────────────────────────────────────

PHARMA_META = {

    "Croscarmellose sodium": {
        "fonction_principale": "Superdésintégrant pour comprimés et gélules",
        "utilisation_typique": (
            "1-5% superdésintégrant dans comprimés par compression directe ou granulation ; "
            "0.5-2% dans gélules ; "
            "Préféré au SSG pour formulations à faible teneur en eau"
        ),
        "proprietes_cles": (
            "Gonflement rapide et important au contact de l'eau (>10x son volume) ; "
            "Mécanisme de désintégration par gonflement ET capillarité ; "
            "Insoluble dans eau, éthanol et solvants organiques ; "
            "Compatible compression directe et granulation humide ; "
            "Efficace même à faibles concentrations (1-2%)"
        ),
        "precautions": (
            "Incompatible avec acides forts et oxydants ; "
            "Légère hygroscopicité : stocker hermétiquement ; "
            "Peut réduire l'effet de certains lubrifiants (interaction ionique) ; "
            "Teneur en sodium à surveiller chez patients hypertendus"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Carmellosum natricum conexum) ; "
            "USP-NF <Croscarmellose Sodium> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.220"
        ),
    },

    "Crospovidone": {
        "fonction_principale": "Superdésintégrant insoluble dans l'eau pour formes solides orales",
        "utilisation_typique": (
            "2-5% superdésintégrant dans comprimés (compression directe et granulation) ; "
            "2-3% dans gélules à libération immédiate ; "
            "Agent de complexation pour améliorer la solubilité de PA lipophiles"
        ),
        "proprietes_cles": (
            "Insoluble dans eau et solvants organiques (réticulation totale) ; "
            "Absorption d'eau très rapide (mécanisme capillarité) ; "
            "Non hygroscopique (stockage moins contraignant que SSG) ; "
            "Compatible compression directe ; "
            "Peut former des complexes avec des molécules aromatiques et phénoliques"
        ),
        "precautions": (
            "Incompatible avec agents oxydants forts ; "
            "Interaction possible avec certains PA aromatiques (complexation PVP) ; "
            "Vérifier l'effet sur la dissolution si utilisé à >5% ; "
            "Poudre fine : utiliser EPI en manipulation"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Crospovidonum) ; "
            "USP-NF <Crospovidone> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.225"
        ),
    },

    "Sodium starch glycolate": {
        "fonction_principale": "Superdésintégrant, agent gonflant pour formes solides orales",
        "utilisation_typique": (
            "2-8% superdésintégrant dans comprimés et gélules ; "
            "Préféré en granulation humide pour formulations aqueuses ; "
            "Efficace dans formes effervescentes à faibles concentrations"
        ),
        "proprietes_cles": (
            "Gonflement très rapide (300-1000x son volume selon grade) ; "
            "Trois grades : A (pH neutre), B (faible Na), C (réticulé) ; "
            "Légèrement hygroscopique ; "
            "Compatible granulation humide et compression directe ; "
            "Désintégration rapide même dans milieux visqueux"
        ),
        "precautions": (
            "Incompatible avec acides et sel d'acide fort ; "
            "Sensible à l'humidité (stocker <60% HR) ; "
            "Peut augmenter la viscosité à >10% ; "
            "Teneur en sodium variable selon grade (surveiller chez cardiaques)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Carmellosum natricum, Amylum solani) ; "
            "USP-NF <Sodium Starch Glycolate> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.743"
        ),
    },

    "Gelatin": {
        "fonction_principale": "Enveloppe de gélules, liant, agent de suspension et gélifiant",
        "utilisation_typique": (
            "Capsules dures (gélules) : enveloppe à 100% ; "
            "Capsules molles (softgel) : enveloppe en mélange avec glycérol ; "
            "2-15% liant en granulation humide ; "
            "1-5% agent de suspension en formes liquides"
        ),
        "proprietes_cles": (
            "Protéine d'origine animale (collagène hydrolysé) ; "
            "Soluble dans eau chaude (>35°C), gélifie en refroidissant ; "
            "Point de gélification 25-30°C (proche température corporelle) ; "
            "Bloom value 75-280 selon grade (résistance gel) ; "
            "Compatible large gamme de PA hydrophiles et lipophiles"
        ),
        "precautions": (
            "Origine porcine ou bovine : problèmes éthiques/religieux (halal, casher, vegan) ; "
            "Incompatible avec agents oxydants forts, acides minéraux concentrés ; "
            "Peut altérer dissolution si réticulée (aldéhydes, lumière UV) ; "
            "Allergie protéique rare mais documentée"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Gelatina) ; "
            "USP-NF <Gelatin> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.349"
        ),
    },

    "Acacia": {
        "fonction_principale": "Liant, agent émulsifiant, agent de suspension (gomme arabique)",
        "utilisation_typique": (
            "1-5% liant en granulation humide (solution aqueuse) ; "
            "1-5% agent émulsifiant dans émulsions H/E ; "
            "35-50% agent de microencapsulation ; "
            "10-40% agent de suspension dans suspensions orales"
        ),
        "proprietes_cles": (
            "Polysaccharide naturel (Acacia senegal et seyal) ; "
            "Soluble dans eau (solution visqueuse 50% m/v) ; "
            "Excellent agent émulsifiant grâce aux protéines associées ; "
            "Stable sur large gamme de pH (2-10) ; "
            "Non toxique, GRAS FDA"
        ),
        "precautions": (
            "Peut contenir des traces de métaux lourds (contrôle qualité essentiel) ; "
            "Incompatible avec éthanol, acides forts, tanins, sels de métaux lourds ; "
            "Hygroscopique (stocker hermétiquement) ; "
            "Réaction allergique rare (rhinite professionnelle documentée)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Acaciae gummi) ; "
            "USP-NF <Acacia> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.1 ; "
            "FDA GRAS status"
        ),
    },

    "Xanthan gum": {
        "fonction_principale": "Agent viscosifiant, suspenseur, stabilisant dans formes liquides",
        "utilisation_typique": (
            "0.1-0.5% agent viscosifiant dans suspensions et sirops ; "
            "0.1-0.25% stabilisant dans émulsions ; "
            "Formes topiques : gel et crème 0.5-1% ; "
            "0.5-2% dans formes à libération prolongée (matrice)"
        ),
        "proprietes_cles": (
            "Polysaccharide bactérien (Xanthomonas campestris) ; "
            "Comportement pseudo-plastique (rhéofluidifiant) ; "
            "Stable de pH 1 à 13 et de 0 à 80°C ; "
            "Compatible avec sels, sucres, alcools ; "
            "Synergique avec gomme de caroube et de guar"
        ),
        "precautions": (
            "Incompatible avec oxydants forts et solvants organiques anhydres ; "
            "Peut être fermenté par flore intestinale (flatulences fortes doses) ; "
            "Origine microbienne : contrôle endotoxines pour injectables ; "
            "Hydratation lente dans solutions très froides"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Xanthani gummi) ; "
            "USP-NF <Xanthan Gum> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.855 ; "
            "FDA GRAS status"
        ),
    },

    "Carboxymethylcellulose sodium": {
        "fonction_principale": "Liant, épaississant, agent suspenseur, désintégrant",
        "utilisation_typique": (
            "1-6% désintégrant et liant dans comprimés ; "
            "0.25-1% épaississant et suspenseur en formes liquides orales ; "
            "0.5-1.5% dans collyres (larmes artificielles) ; "
            "Base de gels hydrophiles 1-3%"
        ),
        "proprietes_cles": (
            "Polymère cellulosique soluble dans eau froide ; "
            "Viscosité élevée selon grade (25-25000 mPa·s) ; "
            "Gonfle dans eau sans dissolution totale pour grades réticulés ; "
            "Stable pH 4-10 ; "
            "Anionique : interactions ioniques avec PA cationiques"
        ),
        "precautions": (
            "Incompatible avec sels de métaux lourds, acides forts et alcools concentrés ; "
            "Peut former complexes avec PA cationiques (précipitation) ; "
            "Grade et viscosité à préciser (influence biopharmaceutique) ; "
            "Hygroscopique (humidité peut affecter la viscosité)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Carmellosum natricum) ; "
            "USP-NF <Carboxymethylcellulose Sodium> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.130"
        ),
    },

    "Ethyl cellulose": {
        "fonction_principale": "Enrobage à libération prolongée, liant hydrophobe",
        "utilisation_typique": (
            "3-20% enrobage de microbilles ou comprimés pour libération prolongée ; "
            "5-20% matrice hydrophobe pour libération prolongée ; "
            "3-10% liant par granulation à sec ou humide avec solvant organique ; "
            "Film de protection contre humidité"
        ),
        "proprietes_cles": (
            "Insoluble dans eau, soluble dans solvants organiques (éthanol, acétone) ; "
            "Film souple et résistant (bonne barrière à l'eau) ; "
            "Large gamme de viscosités (7 à 100 cps) ; "
            "Stable chimiquement et thermiquement ; "
            "Point de ramollissement 140-150°C (extrusion à chaud possible)"
        ),
        "precautions": (
            "Solvants organiques nécessaires : procédés avec contrôles HAP ; "
            "Dispersion aqueuse (Aquacoat, Surelease) comme alternative ; "
            "Incompatible avec cires et PEG à hautes températures ; "
            "Peut retarder excessivement la libération si >20%"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Ethylcellulosum) ; "
            "USP-NF <Ethylcellulose> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.298"
        ),
    },

    "Shellac": {
        "fonction_principale": "Enrobage gastro-résistant entérique, pelliculage brillant",
        "utilisation_typique": (
            "5-20% solution éthanoïque pour enrobage entérique de comprimés et granules ; "
            "Agent de brillantage (polish) sur comprimés sucrés ; "
            "Enrobage de protection contre humidité et lumière"
        ),
        "proprietes_cles": (
            "Résine naturelle sécrétée par Laccifer lacca ; "
            "Insoluble en milieu gastrique (pH <5), soluble à pH >7 (intestin grêle) ; "
            "Excellent film imperméable à l'humidité et aux gaz ; "
            "Bonne adhérence à de nombreux substrats ; "
            "Biodégradable et d'origine naturelle"
        ),
        "precautions": (
            "Origine animale : problèmes éthiques (vegan, végétarien) ; "
            "Peut ralentir dissolution si épaisseur d'enrobage >20 mg/cm² ; "
            "Vieillissement : polymérisation progressive (altère dissolution) ; "
            "Incompatible avec bases fortes ; stocker à l'abri chaleur et humidité"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Lacca) ; "
            "USP-NF <Shellac> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.720"
        ),
    },

    "Carbomer": {
        "fonction_principale": "Agent gélifiant, agent viscosifiant, bioadhésif pour formes topiques et muqueuses",
        "utilisation_typique": (
            "0.5-2% formateur de gel dans préparations topiques et vaginales ; "
            "0.1-0.5% agent viscosifiant dans suspensions ophtalmiques ; "
            "0.5-5% agent bioadhésif dans systèmes à libération mucoadhésive ; "
            "Base de gels aqueux pour principes actifs hydrophiles"
        ),
        "proprietes_cles": (
            "Polymère acrylique réticulé (acide polyacrylique) ; "
            "Forme des gels clairs à pH 6-10 (neutralisation avec NaOH ou TEA) ; "
            "Excellent agent bioadhésif mucoadhésif ; "
            "Large gamme : 934, 940, 974P, 980 (viscosités différentes) ; "
            "Stable en dispersion aqueuse après neutralisation"
        ),
        "precautions": (
            "Incompatible avec acides forts (précipitation), phénol, résines cationiques ; "
            "Poudre très fine (irritant respiratoire) : utiliser masque en manipulation ; "
            "Doit être neutralisé avant usage (pH acide non neutralisé inutilisable) ; "
            "Incompatible avec électrolytes à fortes concentrations (réduction viscosité)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Carbomerum) ; "
            "USP-NF <Carbomer> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.110"
        ),
    },

    "Sodium bicarbonate": {
        "fonction_principale": "Agent effervescent, alcalinisant, agent tampon",
        "utilisation_typique": (
            "10-40% dans comprimés et sachets effervescents (avec acide citrique/tartrique) ; "
            "0.5-2% alcalinisant et tampon dans formes liquides ; "
            "Agent générateur de CO2 dans comprimés à désintégration rapide ; "
            "Antiacide gastrique à 0.3-2g par prise"
        ),
        "proprietes_cles": (
            "Soluble dans eau (96g/L à 20°C) ; "
            "pH solution 1% ≈ 8.3 (légèrement alcalin) ; "
            "Décomposition thermique >50°C (libère CO2) ; "
            "Réagit avec acides (effervescence) ; "
            "Non hygroscopique en conditions normales"
        ),
        "precautions": (
            "Incompatible avec acides (réaction effervescente) et sels de Ca, Mg ; "
            "Décomposition à la chaleur : procédé à froid ou granulation sèche ; "
            "Charge sodée significative (surveiller chez cardiaques/hypertendus) ; "
            "Alcalinisation gastrique peut affecter absorption de certains PA"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Natrii hydrogenocarbonas) ; "
            "USP-NF <Sodium Bicarbonate> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.736 ; "
            "FDA GRAS status"
        ),
    },

    "Ascorbic acid": {
        "fonction_principale": "Antioxydant, acidifiant, vitamine C",
        "utilisation_typique": (
            "0.01-0.1% antioxydant dans formes liquides et solides ; "
            "0.1-0.5% acidifiant et chélateur synergique (avec EDTA) ; "
            "250-1000mg PA dans comprimés vitaminiques ; "
            "Agent réducteur pour stabiliser PA facilement oxydables"
        ),
        "proprietes_cles": (
            "Soluble dans eau (330g/L à 20°C), peu soluble dans éthanol ; "
            "pKa : 4.17 (acide L-ascorbique, forme L naturelle) ; "
            "Puissant réducteur (E° = +0.08V) ; "
            "Se dégrade à la chaleur, lumière et en présence d'O2 ; "
            "Synergie antioxydante avec tocophérols et BHA/BHT"
        ),
        "precautions": (
            "Incompatible avec bases fortes, oxydants, sels de Fe et Cu (catalysent oxydation) ; "
            "Instable en solution aqueuse en présence d'oxygène dissous ; "
            "Doses >2g/j : risque de calculs rénaux oxaliques ; "
            "Peut réduire efficacité de certains antibiotiques (pH)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Acidum ascorbicum) ; "
            "USP-NF <Ascorbic Acid> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.57 ; "
            "FDA GRAS status"
        ),
    },

    "Alpha-tocopherol": {
        "fonction_principale": "Antioxydant liposoluble, vitamine E, stabilisant pour huiles et émulsions",
        "utilisation_typique": (
            "0.001-0.05% antioxydant dans huiles, émulsions et formes lipophiles ; "
            "0.01-0.05% stabilisant d'émulsions lipidiques injectables ; "
            "PA vitamine E dans suppléments et médicaments"
        ),
        "proprietes_cles": (
            "Liquide huileux jaune clair, insoluble dans eau ; "
            "Soluble dans huiles, éthanol et chloroforme ; "
            "Très puissant antioxydant liposoluble (piégeur de radicaux libres) ; "
            "Forme naturelle (d-α) plus active que synthétique (dl-α) ; "
            "Se dégrade par oxydation à la lumière et chaleur"
        ),
        "precautions": (
            "S'oxyde lui-même à l'air (utiliser sous atmosphère inerte) ; "
            "Incompatible avec sels de Fe et Cu, peroxyde d'hydrogène ; "
            "À fortes doses orales : antagoniste de vitamine K (prudence anticoagulants) ; "
            "Non miscible à l'eau : nécessite émulsification ou solubilisant"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Alpha-tocopherolum) ; "
            "USP-NF <Vitamin E> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.31 ; "
            "FDA GRAS status"
        ),
    },

    "Butylated hydroxytoluene": {
        "fonction_principale": "Antioxydant liposoluble pour huiles, cires et matières grasses",
        "utilisation_typique": (
            "0.0075-0.1% antioxydant dans huiles végétales et minérales ; "
            "0.02-0.1% stabilisant d'excipients lipophiles (cires, graisses) ; "
            "En association avec BHA pour effet synergique"
        ),
        "proprietes_cles": (
            "Poudre cristalline blanche, point de fusion 70°C ; "
            "Insoluble dans eau, très soluble dans huiles et solvants organiques ; "
            "Antioxydant par mécanisme radical (phénol encombré) ; "
            "Volatile à température élevée (peut se perdre en process chaud) ; "
            "Synergique avec BHA et acide citrique (chélation métaux)"
        ),
        "precautions": (
            "Usage alimentaire limité (E321) : dose ADI 0.3 mg/kg/j ; "
            "Incompatible avec agents oxydants et sels de Fe ; "
            "Peut induire activité enzymatique hépatique à fortes doses ; "
            "Pas pour injectables ou produits muqueux sensibles"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Butylis hydroxytoluenum) ; "
            "USP-NF <Butylated Hydroxytoluene> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.113 ; "
            "FDA GRAS status"
        ),
    },

    "Methylparaben": {
        "fonction_principale": "Conservateur antimicrobien (parabène) pour formes liquides et semi-solides",
        "utilisation_typique": (
            "0.015-0.2% conservateur dans formes liquides orales et topiques ; "
            "0.015-0.2% en combinaison avec propylparaben (ratio 4:1 typique) ; "
            "0.065-0.25% dans formes semi-solides (crèmes, gels)"
        ),
        "proprietes_cles": (
            "Actif contre bactéries Gram+ et moisissures ; "
            "Spectre élargi en combinaison avec propylparaben ; "
            "Stable de pH 3 à 6 (activité optimale) ; "
            "Faiblement soluble dans eau froide (2.5g/L à 20°C) ; "
            "Non ionique, compatible large gamme d'excipients"
        ),
        "precautions": (
            "Activité antimicrobienne réduite en présence de surfactants non ioniques (partitionnement) ; "
            "Allergie de contact documentée (tests épicutanés) ; "
            "Controverse perturbateurs endocriniens (données non concluantes en usage pharma) ; "
            "Mention obligatoire dans liste des excipients (réglementation EU)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Methylis parahydroxybenzoas) ; "
            "USP-NF <Methylparaben> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.527 ; "
            "Directive 2014/95/EU (mention obligatoire)"
        ),
    },

    "Propylparaben": {
        "fonction_principale": "Conservateur antimicrobien (parabène) lipophile, en combinaison avec méthylparaben",
        "utilisation_typique": (
            "0.01-0.02% conservateur dans formes liquides orales ; "
            "0.01-0.6% dans formes topiques semi-solides ; "
            "Toujours utilisé en combinaison avec méthylparaben (ratio 1:4)"
        ),
        "proprietes_cles": (
            "Plus lipophile et plus actif sur champignons que méthylparaben ; "
            "Très peu soluble dans eau froide (0.5g/L à 20°C) ; "
            "Activité maximale à pH 4-6 ; "
            "Spectre bactéricide plus limité que méthylparaben seul ; "
            "Synergie marquée avec méthylparaben"
        ),
        "precautions": (
            "Même profil de sécurité que méthylparaben (allergie, controverse endocrinien) ; "
            "Solubilité limitée dans eau : dissoudre dans éthanol avant incorporation ; "
            "Partitionnement dans phase lipidique des émulsions (réduire concentration active) ; "
            "Mention obligatoire dans liste des excipients (EU)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Propylparahydroxybenzoas) ; "
            "USP-NF <Propylparaben> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.671 ; "
            "Directive 2014/95/EU (mention obligatoire)"
        ),
    },

    "Sorbic acid": {
        "fonction_principale": "Conservateur antifongique et antibactérien pour formes à pH acide",
        "utilisation_typique": (
            "0.05-0.2% conservateur dans suspensions, sirops et formes liquides acides ; "
            "0.05-0.3% dans formes semi-solides topiques ; "
            "Préféré aux parabènes pour formes à pH <6 (bonnes solubilité et efficacité)"
        ),
        "proprietes_cles": (
            "Activité antifongique excellente (levures et moisissures) ; "
            "Efficace sous forme non dissociée (pH <6 optimal) ; "
            "pKa = 4.76 ; inactif au-dessus de pH 6.5 ; "
            "Peu soluble dans eau froide (1.6g/L à 20°C), mieux à chaud ; "
            "Métabolisé par voie normale des acides gras (non toxique)"
        ),
        "precautions": (
            "Perd son efficacité à pH >6 (utiliser sel de potassium à pH >6) ; "
            "Incompatible avec agents oxydants et bases fortes ; "
            "Peut développer résistances (rares) avec Candida sp. ; "
            "Irritation légère muqueuses à concentrations >0.5%"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Acidum sorbicum) ; "
            "USP-NF <Sorbic Acid> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.762 ; "
            "FDA GRAS status"
        ),
    },

    "Potassium sorbate": {
        "fonction_principale": "Conservateur antifongique hydrosoluble, sel de potassium de l'acide sorbique",
        "utilisation_typique": (
            "0.1-0.2% conservateur dans formes aqueuses à pH 3-6 ; "
            "Préféré à l'acide sorbique pour sa meilleure solubilité dans l'eau ; "
            "0.1-0.3% conservateur dans collyres et solutions ophtalmiques"
        ),
        "proprietes_cles": (
            "Très soluble dans eau (580g/L à 20°C) — avantage sur acide sorbique ; "
            "Libère l'acide sorbique en solution acide (forme active) ; "
            "Efficace à pH 3-6 (pKa 4.76) ; "
            "Spectre : levures, moisissures, bactéries ; "
            "Moins irritant que l'acide sorbique"
        ),
        "precautions": (
            "Inactif à pH >6 (hydrolyse insuffisante en acide sorbique) ; "
            "Incompatible avec ions métalliques divalents (Ca2+, Mg2+) ; "
            "Peut réagir avec agents réducteurs et chlorures en solution ; "
            "Charge potassique à surveiller chez insuffisants rénaux"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Kalii sorbas) ; "
            "USP-NF <Potassium Sorbate> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.633 ; "
            "FDA GRAS status"
        ),
    },

    "Cetyl alcohol": {
        "fonction_principale": "Alcool gras émollient, agent d'émulsification, stabilisant de crèmes",
        "utilisation_typique": (
            "2-15% co-émulsifiant et stabilisant dans crèmes H/E ; "
            "1-10% émollient et modificateur de texture en topiques ; "
            "2-5% agent d'émulsion dans pommades ; "
            "Modificateur de rhéologie dans lotions"
        ),
        "proprietes_cles": (
            "Alcool gras C16 (1-hexadécanol), paillettes blanches, PM 242.44 ; "
            "Insoluble dans eau, soluble dans huiles et éthanol chaud ; "
            "Point de fusion 45-52°C ; "
            "Non irritant et non sensitisant pour la peau ; "
            "Confère texture cireuse et onctuosité aux émulsions"
        ),
        "precautions": (
            "Incompatible avec agents oxydants forts ; "
            "Solidification à température ambiante : procédé à chaud requis (>55°C) ; "
            "Peut obstruer pores cutanés à fortes concentrations ; "
            "Rare : allergie de contact (testing épicutané recommandé si antécédent)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Alcohol cetylicus) ; "
            "USP-NF <Cetyl Alcohol> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.157"
        ),
    },

    "Mineral oil": {
        "fonction_principale": "Lubrifiant, émollient, solvant lipophile pour formes topiques et orales",
        "utilisation_typique": (
            "1-30% base émolliente dans crèmes, pommades et lotions ; "
            "Laxatif lubrifiant oral (15-45 mL/prise adulte) ; "
            "Lubrifiant de capsules molles (softgel) ; "
            "Phase huileuse dans émulsions et semi-solides"
        ),
        "proprietes_cles": (
            "Mélange complexe d'hydrocarbures saturés C15-C40 ; "
            "Insoluble dans eau et éthanol ; "
            "Chimiquement inerte (excellent stabilité) ; "
            "Viscosité variable selon grade (légère à lourde) ; "
            "Non absorbé par voie cutanée (film occlusif sur la peau)"
        ),
        "precautions": (
            "Usage oral chronique : déficit en vitamines liposolubles (A, D, E, K) par partitionnement ; "
            "Pneumonie lipoïde si inhalation (déglutition difficile) ; "
            "Incompatible avec agents oxydants forts ; "
            "Grades USP requis pour usage pharmaceutique (impuretés HAP contrôlées)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Paraffinum liquidum) ; "
            "USP-NF <Mineral Oil> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.539"
        ),
    },

}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  ENRICH MANUAL — Batch 3 (IDs 40-59)")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"\n❌ Fichier introuvable : {INPUT_FILE}")
        print("   Lancez d'abord : python3 scripts/fetch_pubchem_b3.py")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        excipients = json.load(f)

    print(f"\n📂 {len(excipients)} excipients chargés depuis {INPUT_FILE.name}")

    now_iso  = datetime.now(timezone.utc).isoformat()
    resultats    = []
    non_trouves  = []

    for exc in excipients:
        nom  = exc["nom_commun"]
        meta = PHARMA_META.get(nom)

        if meta:
            complet = {**exc, **meta, "date_extraction": now_iso}
            print(f"  ✅ {nom}")
        else:
            complet = {**exc, "date_extraction": now_iso}
            non_trouves.append(nom)
            print(f"  ⚠️  {nom} — métadonnées pharma manquantes")

        resultats.append(complet)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"  ✅ {len(resultats) - len(non_trouves)}/{len(resultats)} enrichis")
    if non_trouves:
        print(f"  ⚠️  Métadonnées manquantes : {', '.join(non_trouves)}")
    print(f"  💾 Sauvegardé → {OUTPUT_FILE}")
    print("=" * 60)
    print("\n→ Étape suivante : python3 scripts/insert_supabase_b3.py")


if __name__ == "__main__":
    main()
