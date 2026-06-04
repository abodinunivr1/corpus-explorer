# Corpus Explorer — Guide utilisateur

Outil d'exploration interactive d'un corpus d'entretiens codés (recherche qualitative sur le déplacement de la valeur en deeptech).

---

## Démarrage

Au premier chargement, l'app demande d'uploader trois fichiers Excel :

| Fichier | Contenu |
|---|---|
| `master_corpus.xlsx` | Table des codings (un coding = un code appliqué à un extrait) |
| `index_passages.xlsx` | Table des passages (regroupements d'extraits contigus) |
| `CODE_BOOK_v10.xlsx` | Définitions du codebook |

Une fois les trois fichiers chargés, l'écran d'upload disparaît et l'app est opérationnelle. **Les données restent en mémoire et ne sont jamais envoyées ni stockées.**

---

## Vues disponibles

### 🏷 Codings

Exploration des codings individuels (un coding = un code appliqué à un extrait d'entretien).

**Filtres disponibles**
- Entretien(s), groupe analytique, code spécifique
- Niveau de confiance (high / medium / low)
- Recherche plein texte dans les extraits
- Tri par confiance, groupe ou entretien

**Navigation croisée** — chaque coding affiche un bouton `→ N passages` pour basculer directement sur les passages de l'entretien concerné.

**Export** — bouton `⬇ Export` pour télécharger les codings filtrés en `.xlsx`.

---

### 📄 Passages

Exploration des passages (blocs de texte contenant plusieurs codes).

**Filtres disponibles**
- Entretien(s), groupe présent, code présent
- Confiance minimale
- Plage de densité : nombre de codes et de groupes par passage
- Recherche plein texte dans les extraits

**Navigation croisée** — depuis un passage, accès direct aux codings de l'entretien ou à la fiche entretien.

**Export** — téléchargement des passages filtrés en `.xlsx`.

---

### 📊 Analytique

Tableaux de bord statistiques sur le corpus (filtrables par entretien et groupe).

| Visualisation | Description |
|---|---|
| Top codes | Codes les plus fréquents (barres horizontales colorées par groupe) |
| Répartition groupes | Distribution des codings par groupe analytique (donut) |
| Codings par entretien × groupe | Barres empilées — densité thématique de chaque entretien |
| Confiance des codings | Distribution high / medium / low |
| Densité codes / passage | Histogramme du nombre de codes par passage |
| Heatmap codes × entretiens | Présence des top codes dans chaque entretien |
| Courbe de saturation théorique | Codes uniques cumulés par entretien (ordre chronologique) |

---

### 📖 Codebook

Référentiel complet des codes avec leurs définitions.

**Filtres** — recherche par mot-clé (nom ou définition), filtre par groupe, tri par groupe / fréquence / alphabétique.

Chaque code affiche sa fréquence d'occurrence et donne accès direct à ses codings, ses passages, ou à l'analyse par entretien (via les boutons sous chaque entrée).

**Tooltip** — dans les vues Codings et Passages, survoler un code-chip affiche sa définition codebook.

---

### 🗺 Carto

Deux visualisations structurelles du corpus.

**Carte factorielle (Analyse des Correspondances)**
- Positionnement des entretiens dans un espace à N dimensions (calculé sur la matrice entretiens × codes)
- Axes configurables (Dim 1–5) depuis la sidebar
- Taille des points proportionnelle au nombre de codings
- Couleur = groupe analytique dominant de l'entretien
- Option : superposer les 30 codes les plus fréquents (losanges)

**Réseau de co-occurrence**
- Graphe interactif des codes qui apparaissent ensemble dans les mêmes passages
- Paramètres : top N codes (20–80), co-occurrence minimale (1–15)
- Taille des nœuds proportionnelle à la fréquence, couleur par groupe analytique
- Navigation interactive (zoom, drag, hover)

---

### 🔍 Entretien

Fiche détaillée par entretien.

- KPIs : nombre de codings, passages, codes uniques, groupes couverts, % confiance high
- Top 20 codes de l'entretien (barres)
- Répartition des groupes analytiques (donut)
- Liste complète des passages avec extraits, codes et niveaux de confiance

---

## Extractions possibles

| Ce que tu veux exporter | Comment faire |
|---|---|
| Tous les codings d'un entretien | Vue **Codings** → filtrer par entretien → `⬇ Export` |
| Tous les codings d'un code | Vue **Codebook** → `→ N codings` → `⬇ Export` |
| Passages multi-codes (densité élevée) | Vue **Passages** → slider "Nb de codes" → `⬇ Export` |
| Passages d'un groupe thématique | Vue **Passages** → filtre groupe → `⬇ Export` |
| Codings basse confiance à réviser | Vue **Codings** → décocher high et medium → `⬇ Export` |
| Tableau codes × entretiens | Vue **Analytique** → heatmap (visuel uniquement) |
| Coordonnées factorielles | Vue **Carto** (visuel uniquement, pas d'export direct) |

---

## Notes techniques

- Les données chargées restent en cache mémoire pour toute la session (pas de rechargement à chaque filtre).
- Un rechargement de page nécessite de ré-uploader les fichiers.
- La carte factorielle requiert le package `prince` (inclus dans `requirements.txt`).
- Le réseau de co-occurrence requiert `networkx` et `pyvis` (inclus dans `requirements.txt`).
