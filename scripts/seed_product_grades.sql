-- ═══════════════════════════════════════════════════════════════
-- ChemistrySpot — Seed product_grades (Phase B, feuille de route v7.1)
-- 36 grades × 9 excipients prioritaires — généré depuis
-- scripts/data/product_grades_seed.json (source de vérité)
-- Prérequis : scripts/create_product_grades.sql déjà exécuté
-- Exécuter dans Supabase Dashboard > SQL Editor — idempotent (upsert)
-- ═══════════════════════════════════════════════════════════════

INSERT INTO product_grades
    (excipient_id, grade_name, nom_commercial, fabricant, specs, pharmacopees, usage_principal)
VALUES
    (11, 'PH-101', 'Avicel PH-101 / Vivapur 101', 'IFF (ex-DuPont) / JRS Pharma', '{"d50_um": "~50", "densite_vrac_g_ml": "0.26–0.31", "humidite_pct_max": "5.0"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Granulation humide, extrusion-sphéronisation — grade de référence historique'),
    (11, 'PH-102', 'Avicel PH-102 / Vivapur 102', 'IFF (ex-DuPont) / JRS Pharma', '{"d50_um": "~100", "densite_vrac_g_ml": "0.28–0.33", "humidite_pct_max": "5.0"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe — meilleur écoulement que PH-101, grade le plus utilisé'),
    (11, 'PH-105', 'Avicel PH-105', 'IFF (ex-DuPont)', '{"d50_um": "~20", "densite_vrac_g_ml": "0.20–0.30", "humidite_pct_max": "5.0"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe de PA fins, compactage à rouleaux — compressibilité maximale'),
    (11, 'PH-200', 'Avicel PH-200', 'IFF (ex-DuPont)', '{"d50_um": "~180", "densite_vrac_g_ml": "0.29–0.36", "humidite_pct_max": "5.0"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe haut débit — écoulement optimal, uniformité de masse'),
    (11, 'PH-302', 'Avicel PH-302', 'IFF (ex-DuPont)', '{"d50_um": "~100", "densite_vrac_g_ml": "0.35–0.46", "humidite_pct_max": "5.0"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Comprimés de petite taille — densité élevée, dose massique accrue'),
    (10, 'Monohydrate 200M', 'GranuLac 200 / Pharmatose 200M', 'Meggle / DFE Pharma', '{"d50_um": "~30–40", "type": "broyé (milled)", "humidite_pct_max": "0.5 (eau libre)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Granulation humide — grade broyé fin, le plus courant'),
    (10, 'Monohydrate 100M', 'GranuLac 100 / Pharmatose 100M', 'Meggle / DFE Pharma', '{"d50_um": "~100–160", "type": "tamisé/broyé", "humidite_pct_max": "0.5 (eau libre)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Granulation humide, remplissage gélules — écoulement supérieur au 200M'),
    (10, 'Spray-dried', 'FlowLac 90 / SuperTab 11SD', 'Meggle / DFE Pharma', '{"d50_um": "~110–140", "type": "atomisé (spray-dried), particules sphériques", "humidite_pct_max": "0.5 (eau libre)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe — excellent écoulement et compressibilité'),
    (10, 'Aggloméré', 'Tablettose 80', 'Meggle', '{"d50_um": "~180–250", "type": "aggloméré (granulated)", "humidite_pct_max": "0.5 (eau libre)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe — bon compromis écoulement/compressibilité'),
    (10, 'Anhydre DC', 'SuperTab 21AN', 'DFE Pharma', '{"type": "anhydre (β-lactose majoritaire)", "humidite_pct_max": "0.5"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe de PA sensibles à l''humidité'),
    (19, 'Pearlitol 25C', 'Pearlitol 25C', 'Roquette', '{"d50_um": "~25", "type": "cristallin, poudre fine"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Granulation humide, formes orodispersibles (ODT)'),
    (19, 'Pearlitol 160C', 'Pearlitol 160C', 'Roquette', '{"d50_um": "~160", "type": "cristallin granulaire"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Mélange direct, remplissage gélules et sachets — bon écoulement'),
    (19, 'Pearlitol 100SD', 'Pearlitol 100SD', 'Roquette', '{"d50_um": "~100", "type": "atomisé (spray-dried)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe — compressibilité élevée, non hygroscopique'),
    (19, 'Pearlitol 200SD', 'Pearlitol 200SD', 'Roquette', '{"d50_um": "~180", "type": "atomisé (spray-dried)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Compression directe haut débit — écoulement optimal'),
    (40, 'Ac-Di-Sol SD-711', 'Ac-Di-Sol SD-711', 'IFF (ex-DuPont)', '{"d50_um": "~35–50", "concentration_usage_pct": "2–5", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant de référence — compression directe et granulation'),
    (40, 'Primellose', 'Primellose', 'DFE Pharma', '{"concentration_usage_pct": "2–5", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant — alternative européenne à l''Ac-Di-Sol'),
    (40, 'Vivasol', 'Vivasol GF', 'JRS Pharma', '{"concentration_usage_pct": "2–5", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant — grade à écoulement amélioré (GF = good flow)'),
    (12, 'Végétal MF-2-V', 'Ligamed MF-2-V', 'Peter Greven', '{"origine": "végétale", "concentration_usage_pct": "0.25–1", "remarque": "mélange court (<5 min) pour éviter la sur-lubrification"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Lubrifiant de compression — grade végétal de référence (halal/casher/vegan)'),
    (12, 'Végétal MF-3-V', 'Ligamed MF-3-V', 'Peter Greven', '{"origine": "végétale", "concentration_usage_pct": "0.25–1", "remarque": "granulométrie plus fine que MF-2-V, surface spécifique accrue"}'::jsonb, ARRAY['Ph.Eur.','USP-NF']::text[], 'Lubrifiant de compression — efficacité accrue à dose réduite'),
    (12, 'HyQual végétal', 'HyQual Magnesium Stearate', 'Avantor (Mallinckrodt)', '{"origine": "végétale", "concentration_usage_pct": "0.25–1"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Lubrifiant de compression — qualité constante lot à lot, marché US'),
    (41, 'Kollidon CL', 'Kollidon CL', 'BASF', '{"d50_um": "~110–130", "concentration_usage_pct": "2–5", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant standard — comprimés et gélules'),
    (41, 'Kollidon CL-F', 'Kollidon CL-F', 'BASF', '{"d50_um": "~20–40", "concentration_usage_pct": "2–5", "type": "Type B (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF']::text[], 'Désintégrant fin — meilleure uniformité dans les comprimés de petite taille'),
    (41, 'Kollidon CL-SF', 'Kollidon CL-SF', 'BASF', '{"d50_um": "~10–30", "concentration_usage_pct": "2–5", "type": "Type B (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF']::text[], 'Formes orodispersibles (ODT) — sensation en bouche optimale'),
    (41, 'Polyplasdone XL', 'Polyplasdone XL', 'Ashland', '{"d50_um": "~100–130", "concentration_usage_pct": "2–5", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant standard — alternative au Kollidon CL'),
    (41, 'Polyplasdone XL-10', 'Polyplasdone XL-10', 'Ashland', '{"d50_um": "~25–40", "concentration_usage_pct": "2–5", "type": "Type B (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Désintégrant fin — gélules, petits comprimés, suspensions'),
    (42, 'Primojel', 'Primojel', 'DFE Pharma', '{"d50_um": "~35–55", "concentration_usage_pct": "2–8", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant de référence en Europe — comprimés et gélules'),
    (42, 'Explotab', 'Explotab', 'JRS Pharma', '{"concentration_usage_pct": "2–8", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant historique — large antériorité réglementaire'),
    (42, 'Vivastar P', 'Vivastar P', 'JRS Pharma', '{"concentration_usage_pct": "2–8", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF']::text[], 'Superdésintégrant — granulation humide et compression directe'),
    (42, 'Glycolys', 'Glycolys', 'Roquette', '{"concentration_usage_pct": "2–8", "type": "Type A (Ph.Eur.)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Superdésintégrant — offre européenne, variantes LV (basse viscosité)'),
    (13, 'K25', 'Kollidon 25', 'BASF', '{"k_value": "22.5–27.0", "concentration_usage_pct": "2–5 (liant)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Liant de granulation basse viscosité — solutions concentrées possibles'),
    (13, 'K30', 'Kollidon 30 / Plasdone K-29/32', 'BASF / Ashland', '{"k_value": "27.0–32.4", "concentration_usage_pct": "2–5 (liant)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Liant de référence pour granulation humide — libération immédiate'),
    (13, 'K90', 'Kollidon 90 F', 'BASF', '{"k_value": "85.5–95.0", "concentration_usage_pct": "2–5 (liant)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Liant haute viscosité — matrices à libération prolongée'),
    (13, 'K12 PF', 'Kollidon 12 PF', 'BASF', '{"k_value": "10.2–13.8", "remarque": "PF = pyrogen-free"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Formes parentérales — solubilisant, faible masse molaire'),
    (14, 'Luzenac Pharma', 'Luzenac Pharma', 'Imerys', '{"concentration_usage_pct": "1–5", "conformite": "Ph.Eur. 2.4.28 (absence d''amiante)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Glidant / anti-adhérent de référence — compression et enrobage'),
    (14, 'Micronisé', 'Talc pharma micronisé', 'Imerys / divers', '{"d50_um": "~5–15", "concentration_usage_pct": "1–5", "conformite": "Ph.Eur. 2.4.28 (absence d''amiante)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Anti-collage dans les enrobages pelliculaires (HPMC) et pelliculage de gélules'),
    (14, 'Standard tamisé', 'Talc pharma standard', 'divers', '{"d50_um": "~20–40", "concentration_usage_pct": "1–5", "conformite": "Ph.Eur. 2.4.28 (absence d''amiante)"}'::jsonb, ARRAY['Ph.Eur.','USP-NF','JP']::text[], 'Lubrifiant secondaire / glidant — formes sèches classiques')
ON CONFLICT (excipient_id, grade_name) DO UPDATE SET
    nom_commercial  = EXCLUDED.nom_commercial,
    fabricant       = EXCLUDED.fabricant,
    specs           = EXCLUDED.specs,
    pharmacopees    = EXCLUDED.pharmacopees,
    usage_principal = EXCLUDED.usage_principal;

SELECT e.nom_commun, COUNT(*) AS nb_grades
FROM product_grades pg JOIN excipients e ON e.id = pg.excipient_id
GROUP BY e.nom_commun ORDER BY e.nom_commun;
