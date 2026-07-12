# 🏰 CHEMISTRYSPOT — FEUILLE DE ROUTE CONSOLIDÉE
**Version 7.2 — 12 juillet 2026 (soir) — PHASES A & B TERMINÉES le jour même. Prochaine action : Phase C (vendre).**
*Remplace : Feuille de Route V1, FILROUGE, FILROUGE2, CONV-SYNCHRO, Château d'If roadmap*

---

## 1. ÉTAT DES LIEUX (audit réel du 12/07 — AUDIT.md)

### ✅ Ce qui est FAIT (et bien fait)
| Élément | État |
|---|---|
| Site chemistryspot.com | En ligne, 10 pages, design pro, carte supply chain UN Comtrade, ticker, gazette |
| Base Supabase | 50 excipients, 192 fournisseurs (180 pays), 1 737 relations, 50 prix, 27 formulations |
| **Formulaires → Supabase** | **Vérifié live : INSERT `contact_requests` fonctionne (HTTP 201).** Seule la notification manque |
| **Grades (socle)** | **Colonne `excipients.grades TEXT[]` déjà remplie pour 10/50** — dont 7 des 9 prioritaires (noms seuls, sans specs) |
| Auth Supabase | `js/auth.js` réel et fonctionnel sur catalogue/produit-detail/guides/EN |
| SEO | Sitemap 58 URLs, Schema.org complet, Search Console validée, score GEO 85/100 |
| Réglementaire | **Réponse ANSM officielle : courtage MPUP = aucune obligation.** Verrou juridique levé |
| Concurrence | Analyse Pharmaoffer/Europages faite → gap excipients confirmé, commission 4-6 % viable |
| Prospection (préparé) | Templates emails, tableau acheteurs (24 facs, 32 CHU, labos, CDMO) |

### ❌ Ce qui BLOQUE (mise à jour 12/07 soir)
1. ~~**Capture de leads aveugle**~~ ✅ **LEVÉ (12/07)** — clés EmailJS live sur les 3 formulaires, test bout en bout OK (HTTP 200 + email reçu), honeypot anti-spam posé, table purgée (0 ligne, plus de spam).
2. ~~**Grades sans profondeur**~~ ✅ **LEVÉ (12/07)** — table `product_grades` créée, 36 grades × 9 excipients seedés, section « Grades disponibles » vérifiée en prod (headless Chrome sur chemistryspot.com).
3. **Traction commerciale = 0** — LE seul verrou restant. 0 lead réel en 4 mois. Il n'y a plus AUCUN prétexte technique : Phase C.

~~Bug annexe : auth factice sur index/contact/fournisseurs~~ ✅ corrigé (12/07, modals inline supprimés). Bonus sécurité : clé service_role régénérée + nettoyée de 13 scripts et dashboard.html.

---

## 2. DIAGNOSTIC STRATÉGIQUE

**Le projet n'a plus un problème technique. Il a un problème commercial.**

- La phase "construction" du Château d'If est terminée. Tu es Dantès sorti de prison : le trésor (expertise + plateforme + base de données), tu l'as. Il reste à s'en servir.
- Chaque semaine passée à coder est une semaine où Pharmaoffer peut se réveiller sur les excipients. Fenêtre estimée : 18-24 mois, déjà entamée depuis sept. 2025.
- La thèse a besoin de **transactions réelles** pour sa partie empirique. Personne ne soutient une thèse sur un site parfait sans utilisateur.

**Règle d'or jusqu'à 10 transactions : GEL TOTAL DES FEATURES.**
Exceptions autorisées : Phase A (EmailJS + fix auth + honeypot) et Phase B (product_grades). Rien d'autre. Pas d'ESRI dashboard, pas d'Eurostat, pas de géocodage GPS, pas de blockchain, pas d'IA. Tout ça va dans le backlog post-traction (§ Post-traction).

---

## 3. FEUILLE DE ROUTE GLOBALE — 4 PHASES

```
PHASE A (Sem. 1)        PHASE B (Sem. 2-4)       PHASE C (Sem. 5-12)      PHASE D (continu)
DÉBLOQUER               PROFONDEUR x9            VENDRE                    THÈSE + STRUCTURE
─────────────           ─────────────            ─────────────             ─────────────
• EmailJS fix           • Table product_grades   • 10 emails fournisseurs  • Dossier PEPITE
• Fix auth 3 pages        (specs jsonb)          • 20 emails acheteurs     • Chapitre 1 (sources
• Honeypot anti-spam    • 9 excipients complets  • Relances J+7            •   primaires)
• Test bout en bout     • Affichage dans          • 1er devis facilité      • Micro-entreprise au
• Purge spam (13 l.)      produit-detail.html    • → 10 TRANSACTIONS       •   1er devis signé
```

### PHASE A — Débloquer (cette semaine, ~2 h 30)

**A1 — EmailJS (≈1 h, action utilisateur requise pour les clés)**
1. Créer/ouvrir compte EmailJS → copier Service ID, Template ID, Public Key
2. Les coller dans `contact.html:341-343` **et** `catalogue.html:754-756` (SDK browser@4 déjà chargé dans les deux pages)
3. Template EmailJS : variables attendues `source_page, excipient, quantite, email_client, entreprise, message` (déjà envoyées par le code)

**A2 — Fix auth factice (15 min)**
1. Supprimer les modals inline `loginModal`/`registerModal` de `index.html` (~l. 690-710), `contact.html` (~l. 310-335), `fournisseurs.html` (~l. 210-235)
2. Supprimer les handlers no-op `handleLogin`/`handleRegister` (`contact.html:420-421`, `fournisseurs.html:506-507`)
3. `auth.js` injecte alors ses modals fonctionnels automatiquement (comme sur le catalogue)

**A3 — Honeypot anti-spam (30 min)**
1. Champ caché `website` (CSS `position:absolute;left:-9999px`) dans le formulaire contact + modal prix catalogue
2. Si rempli → abandon silencieux avant l'INSERT (les 13 lignes actuelles prouvent que les bots trouvent le formulaire)

**A4 — Test bout en bout + nettoyage**
1. Envoyer une vraie demande depuis le site → vérifier : email reçu + ligne dans `contact_requests` + affichage dashboard (PIN cspot2026)
2. Purger les 13 lignes de spam (service_role)
3. Commit + push après CHAQUE sous-tâche (A1, A2, A3, A4)

**Critère de sortie : tu reçois un email quand quelqu'un remplit le formulaire. Point.**

### PHASE B — Profondeur x9 (semaines 2-4) — option retenue : table dédiée

Les 9 excipients prioritaires : **MCC (11), Lactose (10), Mannitol (19), Croscarmellose (40), Stéarate de Mg (12), Crospovidone (41), SSG (42), PVP/Povidone (13), Talc (14).**
Acquis (audit) : 7/9 ont déjà des noms de grades dans `excipients.grades TEXT[]` — base de départ pour le remplissage. Manquent entièrement : Crospovidone, SSG.

**B1 — DDL (action utilisateur : Supabase Dashboard > SQL Editor — le DDL est impossible via l'API REST)**
Générer `scripts/create_product_grades.sql` :
```sql
CREATE TABLE IF NOT EXISTS product_grades (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    excipient_id  BIGINT NOT NULL REFERENCES excipients(id) ON DELETE CASCADE,
    grade_name    VARCHAR(100) NOT NULL,     -- ex. 'PH-102'
    nom_commercial VARCHAR(150),             -- ex. 'Avicel PH-102 (DuPont)'
    specs         JSONB DEFAULT '{}'::jsonb, -- granulométrie µm, densité, humidité %, usage
    pharmacopees  TEXT[],                    -- {Ph.Eur, USP-NF, JP}
    usage_principal TEXT,
    UNIQUE (excipient_id, grade_name)
);
ALTER TABLE product_grades ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read" ON product_grades FOR SELECT USING (true);
```
**B2 — Remplissage** : 3-6 grades par excipient (sources : catalogues publics Roquette/DFE/JRS/IMCD/Ashland, Handbook of Pharmaceutical Excipients, PubChem). Script d'insert via service_role.
**B3 — Affichage** : nouvelle section "Grades disponibles" dans `produit-detail.html` (tab Général ou tab dédié) + les grades du catalogue lisent la nouvelle table.
**B4 — Rythme** : commit + push après CHAQUE excipient terminé (9 commits, pas 1).

**Critère de sortie : un acheteur qui cherche "MCC PH-102" trouve le grade, ses specs et les fournisseurs. Sur 9 produits, l'expérience est parfaite.**

### PHASE C — Vendre (semaines 5-12) — LA PHASE QUI COMPTE — rien à coder
**Séquence fournisseurs (semaine 5) :**
1. 10 cibles : Roquette, JRS Pharma, DFE Pharma, Meggle, BASF, IMCD, Azelis, Seppic, Croda, Gattefossé
2. Template 1 existant, à corriger avant envoi : ~~URL github.io~~ → chemistryspot.com, chiffres réels (50 excipients / 192 fournisseurs, pas "847 produits"), supprimer les "résultats clients" inventés (-25 %…) — **zéro claim invérifiable, ta crédibilité est ton seul capital**
3. Angle : "Votre fiche existe déjà sur la plateforme, voulez-vous la valider/enrichir ?" (bien plus fort qu'un pitch à froid)
4. Relance unique J+7

**Séquence acheteurs (semaines 6-8) :**
1. Cibles chaudes du tableau existant : préparatoires (Cooper, Fareva, Delpharm, Unither), PUI des CHU, facs de pharmacie
2. Commencer par ton propre réseau : ta fac, ton CHU local, tes maîtres de stage — un étudiant en pharmacie a un accès naturel que Pharmaoffer n'aura jamais
3. Offre simple : "Dites-moi quel excipient vous cherchez, je vous trouve 3 fournisseurs avec prix sous 48 h, gratuitement"
4. Chaque demande = la traiter À LA MAIN. Le devis manuel est ta transaction n°1, pas un système automatisé

**KPI unique : 10 transactions facilitées. Rien d'autre ne compte.**
Métriques hebdo : emails envoyés / réponses / demandes de prix / transactions.

### PHASE D — Thèse + structure (en parallèle, continu)
1. **PEPITE / SNEE** : dossier à déposer maintenant (rentrée = commissions de sept.-oct.) → statut étudiant-entrepreneur, couverture sociale maintenue, accès incubateur
2. **Micro-entreprise** : à créer seulement au premier devis signé (Guichet Unique, 30 min, gratuit). SASU plus tard, quand le CA le justifie
3. **Thèse — ordre de rédaction :**
   - Chapitre 1 (historique/multiculturel : Papyrus Ebers, Charaka Samhita, Bencao Gangmu, Canon d'Avicenne) → rédigeable dès maintenant, sources identifiées
   - Cadre réglementaire → matière déjà prête (réponse ANSM = annexe en or, zone grise juridique = contribution originale)
   - Méthodologie → la plateforme comme instrument de recherche
   - Partie empirique → alimentée par les transactions de la Phase C. *Chaque email de prospection est aussi de la collecte de données pour la thèse.*

---

## 4. PLAN DÉTAILLÉ PAR ÉLÉMENT

### 🌐 Site web
- **Ne plus rien ajouter.** Il est meilleur que celui de 90 % des concurrents
- Seules modifs autorisées : Phase A (EmailJS, fix auth, honeypot) + Phase B (grades) + corrections de bugs signalés par de vrais utilisateurs
- Auth : la vraie auth `auth.js` existe déjà — le fix Phase A2 la rétablit partout. Ne PAS développer davantage (pas d'espace client avant traction)

### 🗄️ Base de données Supabase
- Priorité unique : `product_grades` (Phase B, specs jsonb)
- Backlog gelé : Eurostat, géocodage GPS, ESRI dashboard
- Tip : exporte un dump SQL mensuel (Supabase → Database → Backups) — ta base EST ton actif, 1 737 relations ne se reconstruisent pas
- Ménage post-traction : `data/prices.json` + `data/excipients.json` morts (référencés nulle part), descriptions hardcodées de `produit-detail.html` à migrer en base

### 📧 Prospection
- EmailJS d'abord, sinon toute la prospection fuit
- Envois par lots de 10, personnalisés (pas de mass-mailing → spam + image dégradée)
- Depuis contact@chemistryspot.com, pas Gmail
- Tableau de suivi simple : entreprise / contact / date envoi / relance / statut. Pas de CRM avant 50 prospects

### ⚖️ Juridique & structure
- Statut courtage validé ANSM = ton bouclier. Garde l'email ANSM précieusement (annexe thèse + réassurance prospects)
- PEPITE : dossier cette semaine si possible
- Micro-entreprise : au 1er devis signé, pas avant (zéro charge inutile)
- CGU du site : une page simple précisant "mise en relation uniquement, pas de vente directe" — cohérente avec le statut de courtier

### 🎓 Thèse
- 2 sessions/semaine fixes (ex. mar. + jeu. 20h-22h), sanctuarisées
- Commencer par le Chapitre 1 (aucune dépendance, sources prêtes)
- Documenter la prospection au fil de l'eau : taux de réponse, objections, délais = données empiriques
- Objectif : squelette complet + 2 chapitres rédigés avant la 1re transaction

### 💳 Post-traction (backlog gelé — n'y touche pas avant 10 transactions)
Auth avancée/espace client → Stripe Connect (5 %) → Matomo → ESRI dashboard → Eurostat → géocodage → API publique → international → chiffres dynamiques (remplacer les ~20 "50 excipients/192 fournisseurs" hardcodés)

---

## 5. CONSEILS & TIPS

**Stratégie**
1. **Le site parfait est un piège.** 99 % suffit. La transaction n°1 vaut plus que les 100 prochaines features.
2. **Vends le service, pas la plateforme.** Au début, TU es la plateforme : tu reçois une demande, tu trouves les fournisseurs à la main, tu réponds sous 48 h. L'automatisation viendra des patterns observés.
3. **Ton réseau étudiant/officine/CHU est un avantage déloyal.** Pharmaoffer ne peut pas appeler le préparateur de la PUI de ton CHU. Toi si.
4. **Commission 0 % au lancement** (déjà validé) : dis-le explicitement dans chaque email — ça désarme l'objection principale.

**Exécution**
5. **1 action = 1 commit = 1 victoire.** Jamais de journée sans commit pendant les phases A-B, jamais de journée sans email envoyé pendant la phase C.
6. **Rythme hebdo fixe :** lun-mer = exécution phase en cours, jeu = thèse, ven = prospection + relances, revue hebdo 30 min le dimanche (mise à jour REGISTRE.md / MEMORY.md).
7. **Anti-dispersion :** avant d'ouvrir un nouveau chantier, question unique — *"Est-ce que ça rapproche de la transaction n°1 ?"* Non → backlog.

**Crédibilité (secteur pharma = confiance)**
8. Zéro chiffre inventé dans les emails (les templates actuels en contiennent — corrigés en Phase C).
9. Signature : "Simbad X, Doctorant en pharmacie — ChemistrySpot" → le statut académique ouvre plus de portes que "fondateur startup".
10. Réponds à toute demande entrante en < 24 h, même pour dire "je cherche".

**Pièges identifiés dans tes propres documents**
- ⚠️ Le pattern récurrent des sessions : re-planifier au lieu d'exécuter. Cette feuille de route est la dernière — la prochaine session doit être de l'exécution Phase A.
- ⚠️ L'infrastructure distribuée "pool mining" (CONV-SYNCHRO) : idée séduisante, ROI nul avant traction. Supabase tient jusqu'à 10 000 fois ton trafic actuel.
- ⚠️ Blockchain/IA prédictive (anciens plans) : abandonnés à juste titre. Ne pas les ressusciter.

---

## 6. TABLEAU DE BORD — LES SEULS CHIFFRES QUI COMPTENT

| Métrique | Actuel (12/07 soir) | Cible 30j | Cible 90j |
|---|---|---|---|
| EmailJS fonctionnel | ✅ (testé bout en bout) | ✅ | ✅ |
| Auth réelle sur toutes les pages | ✅ | ✅ | ✅ |
| Excipients avec grades complets (specs) | ✅ 9/9 (36 grades en prod) | 9 | 9 |
| Leads réels reçus (hors spam) | 0 | ≥1 | ≥10 |
| Emails prospection envoyés | 0 | 30 | 100 |
| Réponses obtenues | 0 | 5 | 20 |
| Demandes de prix traitées | 0 | 2 | 10 |
| **Transactions facilitées** | **0** | **1** | **10** |
| Dossier PEPITE | ❌ | Déposé | Accepté |
| Chapitres thèse rédigés | ~0,5 | 1 | 2-3 |

---

## 7. LA PROCHAINE ACTION (une seule)

> **Phase C, séquence fournisseurs : corriger le Template 1 (URL chemistryspot.com, chiffres réels 50 excipients / 192 fournisseurs, zéro claim inventé) → envoyer les 10 premiers emails (Roquette, JRS, DFE, Meggle, BASF, IMCD, Azelis, Seppic, Croda, Gattefossé).**
> Angle : « Votre fiche existe déjà — et vos grades aussi (ex. Avicel PH-102 en ligne). Voulez-vous la valider ? »
> Plus rien à coder. Chaque jour sans email envoyé est un jour perdu.

*Document maître — à mettre à jour après chaque session. Version 7.2, 12/07/2026 soir (Phases A+B closes le jour même — AUDIT.md pour le détail).*
