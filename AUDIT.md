# 🔍 AUDIT TECHNIQUE — ChemistrySpot
**Date : 12 juillet 2026 — audit réel (code + tests live Supabase), pas théorique.**
Méthode : lecture du code, requêtes live sur l'API Supabase (anon + service_role), test d'INSERT réel dans `contact_requests` (ligne de test supprimée après).

---

## ✅ CE QUI MARCHE (vérifié)

| Élément | Preuve |
|---|---|
| Formulaire contact → Supabase | INSERT anon testé live : **HTTP 201**. `contact.html:385` écrit dans `contact_requests` |
| Formulaire "prix exact" catalogue → Supabase | Même mécanique, `catalogue.html:1314` |
| Policy RLS `contact_requests` | INSERT public OK, SELECT bloqué (conforme à `scripts/create_contact_requests_table.sql:23`) |
| Colonne `excipients.grades TEXT[]` | Existe (migration `scripts/migrate_phase1.sql` passée), remplie pour **10/50 excipients** |
| Affichage grades au catalogue | `catalogue.html:1227` (`renderGrades`) + filtre grade `catalogue.html:1184` |
| Auth Supabase réelle | `js/auth.js` : signIn/signUp/signOut fonctionnels sur catalogue, produit-detail, reglementation, 3 guides, pages EN |
| Liens internes | Aucun lien statique cassé sur les 6 pages principales |
| Base de données | 50 excipients, 192 fournisseurs, 1 737 relations, 50 prix, supply_chain_data 50 lignes |
| Repo git | Propre : les 93 fichiers "M" = changement de permissions uniquement (0 insertion/0 délétion, chmod WSL) |

---

## ❌ CE QUI EST CASSÉ

### Verrou n°1 — Capture de leads aveugle (Phase A)
| Problème | Fichier : ligne |
|---|---|
| Clés EmailJS = placeholders `VOTRE_PUBLIC_KEY` etc. | `contact.html:341-343` |
| Clés EmailJS = placeholders (formulaire prix) | `catalogue.html:754-756` |
| Échec EmailJS avalé silencieusement (`.catch(() => {})`) | `contact.html:407`, `catalogue.html:1337` |
| Aucun anti-spam (ni honeypot ni captcha) | `contact.html:145` (form), `catalogue.html` (modal prix) |

**Constat live** : la table `contact_requests` contient 13 lignes (mars → 9 juillet 2026), **100 % spam bots** (`jmailservice.com`, entreprises aléatoires), **0 lead réel**. Les demandes arrivent en base mais personne n'est notifié, et il n'existe ni policy SELECT ni interface pour les lire (hors service_role).

### Verrou n°2 — Grades sans profondeur (Phase B)
| Problème | Fichier : ligne / preuve |
|---|---|
| Table `product_grades` inexistante | API Supabase → erreur `42P01` (vérifié live) |
| Crospovidone (id 41) et SSG (id 42) : `grades = null` | Requête live `excipients?grades=not.is.null` → 10 lignes, sans eux |
| Grades existants = noms seuls, zéro spec (granulométrie, densité, usage) | Colonne `TEXT[]`, ex. MCC : `['PH-101','PH-102',…]` |
| `produit-detail.html` n'affiche PAS les grades Supabase | Aucun accès JS à `exc.grades` ; seules mentions texte hardcodées lignes ~820-925 |
| 1 prix par excipient, pas par grade | Table `prices` : champ `grade` unique (`scripts/create_prices_table.sql:13`) |

**Point positif** : 7 des 9 excipients prioritaires ont déjà des noms de grades en base — Lactose (10), MCC (11), Stéarate Mg (12), Povidone (13), Talc (14), Mannitol (19), Croscarmellose (40). Bonus déjà remplis : Starch (21), Stéarate Ca (28), HPMC (36).

### Verrou n°3 — Auth factice sur les 3 pages principales (micro-fix Phase A)
`js/auth.js:22` fait un early-return si un `id="loginModal"` existe déjà dans la page → les modals inline résiduels court-circuitent la vraie auth :

| Page | Modal inline | Handler | Comportement réel |
|---|---|---|---|
| `index.html` | ligne 690 | `handleLogin` **non défini** (`index.html:694`) | ReferenceError → soumission GET par défaut, reload avec l'email dans l'URL |
| `contact.html` | ligne ~310 | no-op `contact.html:420-421` | Ferme le modal, fausse connexion silencieuse |
| `fournisseurs.html` | ligne ~210 | no-op `fournisseurs.html:506-507` | idem |

**Fix** : supprimer les modals inline `loginModal`/`registerModal` + handlers no-op de ces 3 pages ; `auth.js` injecte alors ses propres modals fonctionnels (comme sur le catalogue). ~15 min.

---

## 🔴 ADDENDUM SÉCURITÉ (découvert en Phase B, 12/07)

**La clé `service_role` Supabase est hardcodée dans au moins 5 scripts Python d'un repo GitHub PUBLIC** (`scripts/geocode_suppliers.py`, `insert_dgddi_supabase.py`, `populate_excipient_suppliers.py`, `populate_formulations.py`, `fetch_comtrade.py`). Cette clé contourne le RLS : n'importe qui peut lire, modifier ou **supprimer toute la base** (1 737 relations, 192 fournisseurs…).

**Action requise (utilisateur, Dashboard Supabase)** :
1. Settings → API → **régénérer la clé service_role** (la clé actuelle restera exposée dans l'historique git même après nettoyage des fichiers)
2. Ne plus jamais committer la nouvelle clé — la passer en variable d'environnement (`SUPABASE_SERVICE_KEY`), comme le fait `scripts/insert_product_grades.py`
3. Nettoyer les 5 scripts (remplacer la clé en dur par `os.environ`)

La clé anon dans le front-end est normale (conçue pour être publique, protégée par RLS).

---

## ⚠️ CE QUI MANQUE / INCOHÉRENCES (hors verrous — ne pas traiter avant traction)

| Constat | Détail |
|---|---|
| `data/prices.json`, `data/excipients.json` | Référencés nulle part → fichiers morts (candidats à suppression) |
| Chiffres hardcodés « 50 excipients / 192 fournisseurs » | ~20 occurrences (dont 10 dans `index.html` : lignes 8, 12, 19, 309, 333, 359, 419, 482, 564, 668) — justes aujourd'hui, mais figés |
| Descriptions produit en dur | `produit-detail.html:~800-930` : gros objet JS dupliquant des infos qui devraient venir de Supabase |
| ~~Fichier `" FEUILLE-DE-ROUTE-2026.md"` avec espace en tête~~ | ✅ Corrigé lors de cet audit → `FEUILLE-DE-ROUTE-2026.md` |
| Fichiers non trackés | `DASHBOARD.html`, `ChemistrySpot_Dashboard.xlsx` (+ lockfile LibreOffice `.~lock…#`), `PROMPT-*.md`, `.claude/` |
| Bruit git permissions | 93 fichiers en mode-change ; option : `git config core.fileMode false` |

---

## 📊 ÉTAT GIT (12/07/2026)

- Branche `main`, dernier commit : `8f531d6` — feat(dgddi): add HPMC, Croscarmellose, MCC-v2 customs data pipeline
- 20 derniers commits : pipeline DGDDI (douanes), refonte carte supply chain 70/30, filtres catalogue, palette rose, gazette PubMed — **aucun commit lié à la vente depuis le début du repo**
- Working tree : rien de substantiel en attente (mode-changes uniquement)

---

## 🎯 CONCLUSION

Le site est techniquement sain à ~99 %. Les 3 verrous sont **petits** (2 h + 3 semaines de données + 15 min) et tous documentés avec fichier:ligne ci-dessus. Le vrai déficit reste commercial : 0 lead réel en 4 mois de mise en ligne, dans une table que personne ne lit.

→ Plan d'exécution : voir `FEUILLE-DE-ROUTE-2026.md` (v7.1, mise à jour post-audit).
