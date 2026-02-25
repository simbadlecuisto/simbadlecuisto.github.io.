#!/usr/bin/env python3
"""
enrich_manual.py — Étape 2/3
Fusionne les données PubChem avec les métadonnées pharmaceutiques curées manuellement.
Sortie : data/excipients_complets.json

Usage : python3 scripts/enrich_manual.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

INPUT_FILE  = Path(__file__).parent / "data" / "excipients_pubchem.json"
OUTPUT_FILE = Path(__file__).parent / "data" / "excipients_complets.json"

# ─────────────────────────────────────────────
# MÉTADONNÉES PHARMACEUTIQUES CURÉES
# Clé = nom_commun (doit correspondre exactement à fetch_pubchem.py)
# ─────────────────────────────────────────────

PHARMA_META = {

    "Mannitol": {
        "fonction_principale": "Diluant, édulcorant, agent de remplissage pour comprimés ODT et lyophilisats",
        "utilisation_typique": (
            "10-90% dans comprimés à désintégration orale (ODT) ; "
            "1-20% dans lyophilisats comme agent de lyophilisation ; "
            "2-20% dans comprimés conventionnels"
        ),
        "proprietes_cles": (
            "Non hygroscopique ; Saveur fraîche et légèrement sucrée ; "
            "Faible pouvoir calorique (1.6 kcal/g) ; "
            "Compatible compression directe ; Stable en solution aqueuse ; "
            "Ne réagit pas par réaction de Maillard contrairement au lactose"
        ),
        "precautions": (
            "Effet laxatif osmotique à doses >20g/j ; "
            "Incompatible avec les agents oxydants forts ; "
            "Pour injectables : surveiller osmolalité ; "
            "Éviter chez patients insuffisants rénaux sévères en IV"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Mannitolum) ; "
            "USP-NF <Mannitol> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.509 ; "
            "FDA GRAS status"
        ),
    },

    "Sorbitol": {
        "fonction_principale": "Édulcorant, humectant, diluant pour sirops et formes liquides",
        "utilisation_typique": (
            "20-70% m/v dans sirops ; "
            "25-35% dans pastilles et gommes ; "
            "Humectant topique à 3-10% ; "
            "Plastifiant dans enrobages filmogènes"
        ),
        "proprietes_cles": (
            "Hygroscopique (stocker hermétiquement) ; "
            "60% du pouvoir sucrant du saccharose ; "
            "Stabilisant protéique dans lyophilisats ; "
            "Deux formes cristallines (γ et δ) aux propriétés différentes ; "
            "Métabolisé indépendamment de l'insuline"
        ),
        "precautions": (
            "Effet laxatif osmotique >50g/j ; "
            "Incompatible avec FeCl3 (coloration brune) ; "
            "Peut provoquer diarrhée chez nourrissons si fortes doses ; "
            "Intolérance au sorbitol (fructose malabsorption)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Sorbitolum) ; "
            "USP-NF <Sorbitol> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.754 ; "
            "FDA GRAS status"
        ),
    },

    "Starch": {
        "fonction_principale": "Diluant, désintégrant, liant pour comprimés et gélules",
        "utilisation_typique": (
            "2-10% comme désintégrant dans comprimés ; "
            "10-15% comme liant (empois d'amidon) ; "
            "30-80% comme diluant ; "
            "1-10% comme agent épaississant dans suspensions"
        ),
        "proprietes_cles": (
            "Insoluble dans eau froide, gonfle à 55-70°C (gélatinisation) ; "
            "Bon désintégrant par mécanisme de gonflement ; "
            "Disponible en plusieurs grades (maïs, blé, pomme de terre, riz) ; "
            "Amidon prégélatinisé : compatible compression directe ; "
            "Dégradé par amylases (considérer pour formes gastro-résistantes)"
        ),
        "precautions": (
            "Hygroscopique (stocker <60% HR) ; "
            "Peut favoriser croissance microbienne si humide ; "
            "Amidon de blé : contre-indication maladie cœliaque ; "
            "Incompatible avec oxydants forts et iode"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Amylum maydis, A. solani, etc.) ; "
            "USP-NF <Starch> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.796 ; "
            "FDA GRAS status"
        ),
    },

    "Stearic acid": {
        "fonction_principale": "Lubrifiant de comprimés, agent hydrophobe",
        "utilisation_typique": (
            "1-3% comme lubrifiant dans comprimés et gélules ; "
            "5-15% comme émulsifiant dans crèmes et pommades ; "
            "Agent d'enrobage hydrophobe dans formes à libération prolongée"
        ),
        "proprietes_cles": (
            "Poudre blanche cireuse, point de fusion 69-70°C ; "
            "Insoluble dans eau, très peu soluble dans éthanol froid ; "
            "Activité lubrifiante plus faible que Mg stéarate ; "
            "Moins sensible aux variations de mélange que Mg stéarate"
        ),
        "precautions": (
            "Retarde dissolution si >3% ; "
            "Incompatible avec bases fortes (saponification) et agents oxydants ; "
            "Origine bovine/végétale à préciser (vegan, halal, casher) ; "
            "Mélange court recommandé pour éviter sur-lubrification"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Acidum stearicum) ; "
            "USP-NF <Stearic Acid> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.796"
        ),
    },

    "Citric acid": {
        "fonction_principale": "Acidifiant, chélateur, tampon, agent stabilisant",
        "utilisation_typique": (
            "0.3-2.0% pour ajustement du pH en formes liquides ; "
            "10-40% dans comprimés et sachets effervescents (avec bicarbonate) ; "
            "0.3-2.0% comme chélateur pour stabiliser les oxidants sensibles"
        ),
        "proprietes_cles": (
            "Très soluble dans eau (592g/L à 20°C) et éthanol ; "
            "pKa : 3.09 / 4.75 / 6.40 ; "
            "Forme anhydre et monohydratée (attention aux transitions polymorphiques) ; "
            "Hygroscopique (monohydrate stable de 35-65% HR) ; "
            "Chélate efficacement Fe2+/Fe3+, Cu2+ (protection antioxydante)"
        ),
        "precautions": (
            "Corrosif sur les dents (érosion amélaire) ; "
            "Incompatible avec carbonates/bicarbonates (effervescence) ; "
            "Peut accélérer dégradation oxidative si pH <4 ; "
            "Attention aux transitions polymorphiques anhydre/monohydrate"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Acidum citricum anhydricum) ; "
            "USP-NF <Citric Acid> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.185 ; "
            "FDA GRAS status"
        ),
    },

    "Sucrose": {
        "fonction_principale": "Édulcorant, diluant, agent d'enrobage sucré, conservateur",
        "utilisation_typique": (
            "Sirop simple à 66.7% m/v (conservateur) ; "
            "50-67% dans enrobages sucrés de comprimés ; "
            "Diluant dans comprimés effervescents ; "
            "Agent de granulation et stabilisant lyophilisats"
        ),
        "proprietes_cles": (
            "Très soluble dans eau (200g/100mL à 20°C) ; "
            "Non hygroscopique en-dessous de 85% HR ; "
            "Amorphe hygroscopique après lyophilisation ou broyage ; "
            "Réaction de Maillard avec amines primaires à chaud ; "
            "Pouvoir sucrant de référence (100%)"
        ),
        "precautions": (
            "Cariogène (informer patients) ; "
            "Contre-indiqué dans intol. au fructose/galactose/saccharose ; "
            "Incompatible avec acides forts (hydrolyse en glucose+fructose) ; "
            "Contre-indiqué diabète sans adaptation posologique"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Saccharum) ; "
            "USP-NF <Sucrose> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.802 ; "
            "FDA GRAS status"
        ),
    },

    "Propylene glycol": {
        "fonction_principale": "Solvant, co-solvant, humectant, plastifiant",
        "utilisation_typique": (
            "10-60% co-solvant en injectables et formes orales liquides ; "
            "1-15% humectant en formes topiques ; "
            "1-30% plastifiant dans enrobages filmogènes ; "
            "Véhicule pour principes actifs lipophiles"
        ),
        "proprietes_cles": (
            "Miscible eau, éthanol et chloroforme ; "
            "Viscosité modérée (48.6 mPa·s à 25°C) ; "
            "Non volatil, hygroscopique ; "
            "Point éclair 99°C (moins inflammable que l'éthanol) ; "
            "Solubilise un large spectre de principes actifs"
        ),
        "precautions": (
            "Limite 25mg/kg/j IV chez nourrissons <4 semaines (toxicité rénale/CNS) ; "
            "Peut provoquer irritation cutanée à concentrations élevées ; "
            "Incompatible avec propylène glycol oxydé (peroxyde) ; "
            "Métabolisé en acide lactique et pyruvique"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Propylenglycolum) ; "
            "USP-NF <Propylene Glycol> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.665 ; "
            "FDA GRAS status"
        ),
    },

    "Benzyl alcohol": {
        "fonction_principale": "Conservateur antimicrobien, solvant pour injectables",
        "utilisation_typique": (
            "1-3% conservateur dans injectables multi-doses ; "
            "5-10% solvant pour préparations injectables ; "
            "0.5-1% conservateur en formes topiques"
        ),
        "proprietes_cles": (
            "Partiellement soluble dans eau (4% m/v) ; "
            "Miscible éthanol, éther et chloroforme ; "
            "Activité antimicrobienne large spectre à pH acide ; "
            "Léger anesthésique local (action antidouleur en injectables)"
        ),
        "precautions": (
            "CONTRE-INDIQUÉ chez nourrissons <3 mois : gasping syndrome (toxicité CNS/acidose) ; "
            "Irritant muqueuses oculaires et nasales ; "
            "Incompatible avec agents oxydants et acides minéraux ; "
            "Limiter à 0.9% m/v en injectables (guideline FDA 2022)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Benzalcohol) ; "
            "USP-NF <Benzyl Alcohol> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.79 ; "
            "FDA Safety Comm. benzyl alcohol 2022"
        ),
    },

    "Sodium lauryl sulfate": {
        "fonction_principale": "Surfactant anionique, solubilisant, agent mouillant",
        "utilisation_typique": (
            "0.5-2.0% agent mouillant dans comprimés à libération modifiée ; "
            "1-2% émulsifiant dans crèmes et lotions ; "
            "1-2% agent solubilisant pour principes actifs lipophiles ; "
            "Agent de granulation en mouillant la poudre"
        ),
        "proprietes_cles": (
            "HLB = 40 (très hydrophile, bon agent mouillant) ; "
            "CMC = 8.2 mM dans eau à 25°C ; "
            "Point Kraft < 10°C ; "
            "Stable en pH 4-9 ; "
            "Dénature les protéines (éviter avec macromolécules biologiques)"
        ),
        "precautions": (
            "Irritant muqueuses buccales et gastro-intestinales ; "
            "Incompatible avec surfactants cationiques et sels d'ammonium quaternaire ; "
            "Précipite en présence de cations divalents Ca2+/Mg2+ ; "
            "Limite 2% en usage topique (irritation cutanée)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Natrii laurilsulfas) ; "
            "USP-NF <Sodium Lauryl Sulfate> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.732"
        ),
    },

    "Calcium stearate": {
        "fonction_principale": "Lubrifiant, antiagglomérant pour comprimés et gélules",
        "utilisation_typique": (
            "0.5-2.0% lubrifiant dans comprimés et gélules ; "
            "1-3% antiagglomérant dans poudres et granulés ; "
            "Agent hydrofuge dans enrobages"
        ),
        "proprietes_cles": (
            "Poudre blanche hydrophobe, insoluble dans eau ; "
            "Point de fusion 155-160°C ; "
            "Moins hygroscopique que le stéarate de magnésium ; "
            "Activité lubrifiante comparable au Mg stéarate ; "
            "Origine végétale disponible (vegan/halal)"
        ),
        "precautions": (
            "Retarde dissolution si >2% (film hydrophobe) ; "
            "Incompatible avec acides forts et agents oxydants ; "
            "Origine bovine/végétale à préciser selon réglementation ; "
            "Mélange court recommandé (éviter sur-lubrification)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Calcii stearas) ; "
            "USP-NF <Calcium Stearate> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.121"
        ),
    },

    "Dicalcium phosphate": {
        "fonction_principale": "Diluant minéral, source de calcium et phosphate",
        "utilisation_typique": (
            "15-90% diluant dans comprimés par compression directe ; "
            "10-40% diluant dans gélules ; "
            "Source de calcium dans compléments alimentaires pharmaceutiques"
        ),
        "proprietes_cles": (
            "Insoluble dans eau, soluble dans HCl dilué ; "
            "Compatible compression directe (bon écoulement) ; "
            "Disponible en grade anhydre (CaHPO4) et dihydraté (CaHPO4·2H2O) ; "
            "pH alcalin (5.5-7.0 en suspension aqueuse) ; "
            "Haute densité (bon pour comprimés denses)"
        ),
        "precautions": (
            "Incompatible avec tétracyclines et fluoroquinolones (chélation Ca2+) ; "
            "Réduction biodisponibilité de certains antibiotiques ; "
            "pH alcalin peut dégrader principes actifs acido-labiles ; "
            "Contre-indiqué hypercalcémie, lithiase calcique"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Calcii hydrogenophosphas anhydricus) ; "
            "USP-NF <Dibasic Calcium Phosphate> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.147"
        ),
    },

    "Calcium carbonate": {
        "fonction_principale": "Diluant minéral, agent tampon alcalin, antiacide",
        "utilisation_typique": (
            "0.5-43% diluant dans comprimés ; "
            "Jusqu'à 95% dans comprimés antiacides à mâcher ; "
            "Tampon pH dans formulations orales ; "
            "Source de calcium dans compléments alimentaires"
        ),
        "proprietes_cles": (
            "Insoluble dans eau (0.0013g/L à 20°C) ; "
            "Soluble dans acides (effervescence CO2) ; "
            "pH alcalin en suspension (9-10) ; "
            "Haute densité de poudre ; "
            "Neutralise 10mmol HCl/g"
        ),
        "precautions": (
            "Incompatible avec acides forts (réaction effervescente) ; "
            "Réduit absorption de nombreux médicaments (fluoroquinolones, tétracyclines, fer, zinc) ; "
            "Risque d'hypercalcémie si usage prolongé à fortes doses ; "
            "Syndrome lait-alcali en association avec antiacides"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Calcii carbonas) ; "
            "USP-NF <Calcium Carbonate> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.117 ; "
            "FDA GRAS status"
        ),
    },

    "Sodium chloride": {
        "fonction_principale": "Agent tonifiant, isotonisant pour formes parentérales et ophtalmiques",
        "utilisation_typique": (
            "0.9% solution isotonique (sérum physiologique) ; "
            "0.5-0.9% dans collyres et lavages nasaux ; "
            "Agent de stabilisation dans lyophilisats ; "
            "Modificateur de relargage dans systèmes à libération prolongée"
        ),
        "proprietes_cles": (
            "Très soluble dans eau (360g/L à 20°C) ; "
            "Point de fusion 801°C ; "
            "Osmolarité solution 0.9% ≈ 308 mOsm/kg (iso-osmotique plasma) ; "
            "Stable en solution aqueuse sur large plage de pH ; "
            "Non hygroscopique jusqu'à 75% HR"
        ),
        "precautions": (
            "Incompatible avec sels d'argent (précipitation AgCl) et oxydants forts ; "
            "Peut augmenter TA en usage chronique (charge sodée) ; "
            "Corrosif sur acier inoxydable (attention au matériel) ; "
            "Limite apport Na+ chez insuffisants cardiaques/rénaux"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Natrii chloridum) ; "
            "USP-NF <Sodium Chloride> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.740 ; "
            "FDA GRAS status"
        ),
    },

    "Potassium chloride": {
        "fonction_principale": "Tonifiant, source potassique, modificateur de relargage",
        "utilisation_typique": (
            "0.15-0.45% dans solutions isotoniques (Ringer, etc.) ; "
            "Formes à libération prolongée (matrice KCl 600-750mg) ; "
            "Agent tampon en solutions ophtalmiques"
        ),
        "proprietes_cles": (
            "Soluble dans eau (340g/L à 20°C) ; "
            "Légèrement hygroscopique ; "
            "Goût salé et amer prononcé (nécessite masquage) ; "
            "Stable en solution aqueuse ; "
            "Tensioactif faible (ne mousse pas)"
        ),
        "precautions": (
            "Irritant gastrique grave sans enrobage approprié (risque ulcération) ; "
            "Contre-indiqué hyperkaliémie, insuffisance rénale sévère ; "
            "Surveillance kaliémie en traitement prolongé ; "
            "Incompatible avec permanganate de potassium et oxydants forts"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Kalii chloridum) ; "
            "USP-NF <Potassium Chloride> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.628"
        ),
    },

    "Zinc oxide": {
        "fonction_principale": "Opacifiant, protecteur cutané, astringent dermatologique",
        "utilisation_typique": (
            "1-25% dans crèmes, pâtes et pommades dermatologiques ; "
            "Enrobages opaques blancs dans comprimés ; "
            "Pansements et bandages médicaux ; "
            "Photoprotection physique dans crèmes solaires"
        ),
        "proprietes_cles": (
            "Poudre blanche très fine, insoluble eau ; "
            "Amphotère (soluble dans acides et bases forts) ; "
            "Activité antimicrobienne et anti-inflammatoire légère ; "
            "Stable à la chaleur et UV ; "
            "Indice de réfraction élevé (bon opacifiant)"
        ),
        "precautions": (
            "Éviter inhalation de nanopoudres (fièvre des fondeurs) ; "
            "Incompatible avec acides, alcalis forts, sulfures ; "
            "Usage ophtalmique déconseillé (irritant) ; "
            "Non absorbé per os en usage normal (négligeable)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Zinci oxidum) ; "
            "USP-NF <Zinc Oxide> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.868"
        ),
    },

    "Colloidal silicon dioxide": {
        "fonction_principale": "Antiagglomérant, adsorbant, agent thixotrope pour gels",
        "utilisation_typique": (
            "0.1-0.5% antiagglomérant dans poudres et granulés ; "
            "0.5-5% dans formes liquides comme agent rhéologique ; "
            "Adsorbant pour huiles et liquides dans comprimés ; "
            "Agent d'écoulement pour poudres fines"
        ),
        "proprietes_cles": (
            "Surface spécifique BET : 175-225 m²/g (Aerosil 200) ; "
            "Amorphe, non hygroscopique ; "
            "Faible densité apparente (bulky) ; "
            "Forme des réseaux thixotropes dans solvants aprotiques ; "
            "Compatible avec la majorité des PA et excipients"
        ),
        "precautions": (
            "Éviter inhalation (fibre de silice amorphe, irritation pulmonaire) ; "
            "Peut réduire la biodisponibilité de certains PA par adsorption ; "
            "Incompatible avec agents alcalins forts (dissolution SiO2) ; "
            "Dose ≤1% en usage alimentaire/pharma"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Silica colloidalis anhydrica) ; "
            "USP-NF <Colloidal Silicon Dioxide> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.185"
        ),
    },

    "Hydroxypropyl cellulose": {
        "fonction_principale": "Liant, enrobant filmogène, agent viscosifiant",
        "utilisation_typique": (
            "5-15% liant en granulation humide ; "
            "5-10% enrobage pelliculaire en solution éthanoïque ; "
            "0.5-2% épaississant en formes liquides ; "
            "Agent de libération prolongée matricielle"
        ),
        "proprietes_cles": (
            "Soluble dans eau ET éthanol (rare parmi les dérivés cellulosiques) ; "
            "Thermoplastique : précipite à >40°C (LCST) ; "
            "Large gamme de viscosités (EXF à HF) ; "
            "Bon film formateur ; "
            "Compatible avec la majorité des PA"
        ),
        "precautions": (
            "Incompatible avec phénol et agents réducteurs forts ; "
            "Précipitation au-dessus de 40°C (LCST) à surveiller en process chaud ; "
            "Poudre fine : risque d'inhalation en manipulation ; "
            "Peut interférer avec certains tests de dissolution (viscosité)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Hydroxypropylcellulosum) ; "
            "USP-NF <Hydroxypropyl Cellulose> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.393"
        ),
    },

    "Hypromellose": {
        "fonction_principale": "Liant, enrobant pelliculaire, agent de libération prolongée matricielle",
        "utilisation_typique": (
            "2-5% liant en granulation humide et compression directe ; "
            "5-15% matrice hydrophile pour libération prolongée ; "
            "2-5% enrobage filmogène aqueux (Opadry-like) ; "
            "0.5-1% épaississant collyres (larmes artificielles)"
        ),
        "proprietes_cles": (
            "Soluble dans eau froide (<20°C) et insoluble eau chaude (gélification thermique) ; "
            "Forme des gels hydrophiles robustes au contact de l'eau ; "
            "Viscosité très large gamme (15 à 100 000 mPa·s selon grade) ; "
            "Grades K (LP) et E (enrobage) aux comportements différents ; "
            "Biodégradable, non absorbé per os"
        ),
        "precautions": (
            "Incompatible avec oxydants forts et sels de métaux lourds ; "
            "Gélification thermique peut poser problème en process chaud ; "
            "Hydrolyse possible en pH extrêmes (<3 ou >11) ; "
            "Peut retarder libération de PA très lipophiles"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Hypromellosum) ; "
            "USP-NF <Hypromellose> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.407"
        ),
    },

    "Macrogol 4000": {
        "fonction_principale": "Plastifiant, base de suppositoires, laxatif osmotique",
        "utilisation_typique": (
            "1-5% plastifiant dans enrobages filmogènes ; "
            "50-100% base de suppositoires (Tm ~56°C) ; "
            "Solubilisant pour PA lipophiles ; "
            "10-50% base de pommades et gels hydrophiles"
        ),
        "proprietes_cles": (
            "Soluble dans eau et éthanol (50%) ; "
            "Point de fusion 53-58°C (PEG 4000) ; "
            "Hygroscopique (humectant) ; "
            "Non ionique, compatible large gamme de PA et excipients ; "
            "Augmente perméabilité membranaire à hautes concentrations"
        ),
        "precautions": (
            "Incompatible avec phénol, tanins, sels de métaux lourds ; "
            "Peut augmenter perméabilité intestinale (prudence formes orales à doses élevées) ; "
            "PEG de faible PM plus hygroscopiques et purgatives ; "
            "Éviter contact prolongé sur peau lésée (accumulation rénale)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Macrogolum 4000) ; "
            "USP-NF <Polyethylene Glycol> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.613"
        ),
    },

    "Polysorbate 80": {
        "fonction_principale": "Surfactant non ionique, émulsifiant, solubilisant pour injectables",
        "utilisation_typique": (
            "0.1-3.0% émulsifiant dans émulsions huile/eau ; "
            "0.04-0.4% solubilisant en injectables IV ; "
            "0.1-1% agent mouillant en formes solides ; "
            "Stabilisant de protéines en biothérapeutiques (0.02-0.1%)"
        ),
        "proprietes_cles": (
            "HLB = 15 (hydrophile, préfère phase aqueuse) ; "
            "Liquide visqueux jaune-ambré à 25°C ; "
            "CMC = 0.012 mM ; "
            "Compatible avec large gamme de PA dont biologiques ; "
            "Non ionique : stable en pH 1-9 et en présence d'électrolytes"
        ),
        "precautions": (
            "Réactions anaphylactiques rares mais décrites (prémédicaments si historique) ; "
            "Incompatible avec phénol et tannins ; "
            "Oxydation possible (peroxyde) : stocker à l'abri de la lumière/O2 ; "
            "Peut favoriser solubilisation d'impuretés lipophiles (lixiviation)"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Polysorbatum 80) ; "
            "USP-NF <Polysorbate 80> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.640"
        ),
    },

    "Benzalkonium chloride": {
        "fonction_principale": "Conservateur antimicrobien cationique pour formes ophtalmiques et nasales",
        "utilisation_typique": (
            "0.004-0.02% conservateur dans collyres et solutions ophtalmiques ; "
            "0.01-0.02% conservateur dans gouttes nasales et auriculaires ; "
            "0.02-0.1% désinfectant de surface cutanée dilué"
        ),
        "proprietes_cles": (
            "Mélange de chlorures d'alkyltriméthylammonium (C8 à C18) ; "
            "Activité bactéricide large spectre (Gram+, Gram-, fungi) ; "
            "Stable sur large plage de pH (4-10) ; "
            "Soluble dans eau et éthanol ; "
            "Faible toxicité systémique aux concentrations conservatrices"
        ),
        "precautions": (
            "Incompatible avec surfactants anioniques (SLS), savons, agents réducteurs ; "
            "Irritant oculaire si >0.025% (dommages épithélium cornéen chroniques) ; "
            "Peut être absorbé par les lentilles de contact (déconseiller port pendant le traitement) ; "
            "Précipite avec sels de phosphate en conditions alcalines"
        ),
        "references_pharma": (
            "Pharmacopée Européenne 10.0 (Benzalkonii chloridum) ; "
            "USP-NF <Benzalkonium Chloride> ; "
            "Handbook of Pharmaceutical Excipients 8th Ed p.73"
        ),
    },

}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  ENRICH MANUAL — ChemistrySpot")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"\n❌ Fichier introuvable : {INPUT_FILE}")
        print("   Lancez d'abord : python3 scripts/fetch_pubchem.py")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        excipients = json.load(f)

    print(f"\n📂 {len(excipients)} excipients chargés depuis {INPUT_FILE.name}")

    now_iso = datetime.now(timezone.utc).isoformat()
    resultats = []
    non_trouves = []

    for exc in excipients:
        nom = exc["nom_commun"]
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
    print("\n→ Étape suivante : python3 scripts/insert_supabase.py")


if __name__ == "__main__":
    main()
