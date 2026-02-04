# 🇫🇷 Théorie des Jeux pour la Prise de Décision Stratégique sous Incertitude : Guide Pratique

## Introduction

Ce tutoriel explique pourquoi et comment la théorie des jeux fournit un cadre supérieur pour modéliser les dépendances stratégiques, particulièrement face à des acteurs adverses ou semi-aléatoires comme "la Nature" (risque politique, changements réglementaires, conditions de marché). Nous nous concentrons sur le modèle de souveraineté comme exemple concret.

---

## 1. Brève Histoire de la Théorie des Jeux

### Les Fondations (1920-1950)

**John von Neumann** a posé les fondations mathématiques dans les années 1920, en prouvant le **théorème du minimax** (1928) : dans les jeux à somme nulle à deux joueurs, il existe une stratégie mixte optimale pour chaque joueur. C'était révolutionnaire car cela montrait que le comportement rationnel sous conflit a une structure mathématique.

**Theory of Games and Economic Behavior** (1944, von Neumann & Morgenstern) a formalisé la théorie des jeux comme domaine, introduisant :
- Les jeux sous forme normale (matrices de gains)
- Les jeux sous forme extensive (arbres de jeu)
- Le comportement de coalition dans les jeux à n joueurs

### La Révolution Nash (1950)

**John Nash** a généralisé les résultats de von Neumann aux jeux à somme non-nulle, en prouvant que tout jeu fini possède au moins un **équilibre de Nash** (1950). Cela était profond : même lorsque les intérêts des joueurs ne sont pas parfaitement opposés, il existe des profils de stratégies stables où aucun joueur ne peut améliorer unilatéralement son résultat.

L'équilibre de Nash est devenu le concept de solution central en économie, montrant que des agents rationnels peuvent atteindre des résultats prévisibles même sans coordination.

### Explosion des Applications (1960-présent)

- **Économie** : Théorie des enchères, théorie des contrats, organisation industrielle (Harsanyi, Selten, Myerson)
- **Science politique** : Théorie du vote, relations internationales, résolution de conflits
- **Biologie** : Théorie des jeux évolutionniste (Maynard Smith) - stratégies stables dans les populations
- **Informatique** : Théorie algorithmique des jeux, design de mécanismes, marchés en ligne

**Jeux dynamiques** (1970+) : Shapley, Aumann et d'autres ont étendu aux jeux répétés et jeux stochastiques, permettant l'analyse d'interactions stratégiques de long terme avec incertitude.

### Développements Modernes

- **Théorie comportementale des jeux** (1990+) : Incorporation de la rationalité limitée, préférences sociales
- **Théorie algorithmique des jeux** (2000+) : Complexité computationnelle, apprentissage dans les jeux
- **Théorie robuste des jeux** (2010+) : Jeux sous ambiguïté sur les types d'opposants ou les gains

---

## 2. Pourquoi la Théorie des Jeux pour les Dépendances et Acteurs Adverses ?

### La Nature des Dépendances Stratégiques

La théorie de la décision traditionnelle suppose un **environnement passif** : vous faites des choix, la nature génère des résultats aléatoires à partir d'une distribution connue. Cela échoue quand :

1. **Des acteurs adverses existent** : Les régulateurs répondent à vos stratégies, les concurrents réagissent à vos mouvements, les fournisseurs peuvent exploiter les dépendances
2. **La Nature est semi-adverse** : Le risque politique n'est pas purement aléatoire - les mauvais résultats se regroupent, les politiques persistent, les pires cas arrivent quand vous êtes vulnérable
3. **Les boucles de rétroaction comptent** : Votre action (ex : démarrer une migration) change l'environnement (le fournisseur peut augmenter les prix, le régulateur peut le remarquer)

### Pourquoi Pas Simplement Utiliser des Probabilités ?

**Problème** : Assigner une probabilité unique $p$ à "tarif arrive" suppose :
- Vous connaissez $p$ précisément (souvent faux - les prévisions politiques sont difficiles)
- La probabilité de tarif est indépendante de vos actions (faux - une migration visible peut déclencher une réponse politique)
- Les scénarios catastrophes sont juste des "événements de queue" (faux - une Nature adverse peut déplacer les probabilités contre vous)

**Solution théorie des jeux** : Modéliser la Nature comme un **joueur** qui :
- Choisit parmi un ensemble de stratégies (régimes tarifaires, timing)
- A un objectif (à somme nulle : vous nuire ; en optimisation robuste : déplacer les probabilités adversement)
- Réagit à vos choix (au minimum, dans les contraintes structurelles)

### Les Trois Couches d'Incertitude

1. **Risque** (Niveau 0) : Distribution de probabilité connue
   - Exemple : Pile ou face équitable, données historiques bien calibrées
   - Outil : Espérance, variance

2. **Risque stratégique** (Niveau 1) : Stratégie de l'opposant inconnue mais rationnelle
   - Exemple : Prix concurrent, négociation fournisseur
   - Outil : Équilibre de Nash, minimax

3. **Ambiguïté** (Niveau 2) : Distribution de probabilité elle-même incertaine
   - Exemple : Risque politique sous nouveau régime, crise inédite
   - Outil : Optimisation robuste, DRO de Wasserstein, utilité espérée maxmin

**Ce modèle traite les trois** : Nous utilisons CVaR pour l'aversion au risque, le cadre de jeu pour les interactions stratégiques, et les boules de Wasserstein pour l'ambiguïté.

### Quand Utiliser la Théorie des Jeux vs. Optimisation Simple

**Utiliser la théorie des jeux quand :**
- Les résultats dépendent des choix d'autrui (concurrents, régulateurs, fournisseurs)
- L'"opposant" a des objectifs (même si juste intérêt personnel)
- L'avantage du premier mouvement ou valeur d'engagement compte
- Vous avez besoin de stratégies robustes contre les pires réponses

**Utiliser l'optimisation simple quand :**
- L'environnement est vraiment passif (météo, défaillance machine par usure)
- Vous avez un avantage informationnel écrasant
- La vitesse compte plus que la robustesse (décisions tactiques)

---

## 3. Ce Premier Exemple Simple : L'Approche Min-Max

### La Structure du Jeu à Deux Joueurs

**Joueurs** :
- **Entreprise** (joueur minimisant) : Choisit actions $a \in \{\text{attendre}, \text{investir}, \text{couvrir}, \text{accélérer}, \text{sortir}\}$
- **Nature** (joueur maximisant) : Contrôle le régime tarifaire et (sous ambiguïté) les probabilités de transition

**Pourquoi "Nature" comme Joueur ?**

La Nature n'est pas malveillante, mais modéliser le risque politique/réglementaire comme un joueur adverse :
1. **Protège contre la loi de Murphy** : "Tout ce qui peut mal tourner tournera mal, au pire moment possible"
2. **Capture le regroupement** : Les mauvais événements se corrèlent - les tarifs persistent, les crises s'approfondissent
3. **Conservateur mais rationnel** : Mieux vaut sur-préparer pour le risque politique que d'être pris au dépourvu

### La Fonction de Valeur : Équation de Bellman Minimax

À chaque temps $t$ et état $s$, nous résolvons :

$$V_t(s) = \min_{a \in \mathcal{A}} \max_{p \in \mathcal{P}_\varepsilon(p_0)} \text{CVaR}_\alpha^p\left[\gamma_t \ell(s,a) + V_{t+1}(S')\right]$$

**Traduction** :
- **L'entreprise minimise** en choisissant l'action $a$
- **La Nature maximise** en déplaçant la distribution d'état suivant $p$ dans la boule de Wasserstein $\mathcal{P}_\varepsilon$
- **CVaR** capture le risque de queue (pires résultats $1-\alpha$)
- **$\ell(s,a)$** est le coût par étape (CAPEX + OPEX + tarif)
- **$V_{t+1}$** est le coût futur

### Pourquoi Minimax Fonctionne Ici

**Conservateur mais pas paranoïaque** : La contrainte de Wasserstein $\varepsilon$ limite à quel point la Nature peut être adverse. Pensez-y comme :
- $\varepsilon = 0$ : Faites totalement confiance à vos prévisions (DP standard)
- $\varepsilon = 0.1$ : Permettez à la Nature de déplacer légèrement les probabilités (robuste)
- $\varepsilon = \infty$ : Pire cas pur (trop conservateur)

Nous calibrons $\varepsilon(t)$ aux indicateurs de risque politique, rendant l'ambiguïté variable dans le temps et observable.

### Le Résultat : Une Politique, Pas une Décision

**Insight clé** : Nous n'obtenons pas "investir maintenant" ou "attendre pour toujours" - nous obtenons une **politique conditionnelle à l'état** $\pi(t, s)$ qui dit :
- **Si** tarif désactivé, migration à 0, pas de couverture → attendre
- **Si** tarif s'active, migration à 0, pas de couverture → couvrir
- **Si** tarif persiste, migration à 2, couverture active → accélérer puis sortir

C'est une **stratégie adaptive**, pas un plan rigide. Beaucoup plus précieux qu'une décision unique.

---

## 4. Pourquoi C'est Différent d'une Simulation

### Approche par Simulation

**Ce qu'elle fait** :
1. Spécifier un modèle de probabilité pour les transitions tarifaires (ex : chaîne de Markov)
2. Générer plusieurs trajectoires d'échantillons aléatoires (Monte Carlo)
3. Pour chaque trajectoire, appliquer une politique heuristique (ex : "couvrir si tarif actif 2 ans")
4. Moyenner les coûts sur les simulations

**Résultats** : Distribution de résultats, coût moyen, percentiles

**Limitations** :
- **Suppose que vous connaissez le modèle de probabilité** : Et si votre $P(\text{tarif} | \text{pré-élection})$ est faux ?
- **Évalue une politique donnée** : Ne dit pas s'il existe une meilleure politique
- **Pas de robustesse adversariale** : Si la Nature peut être légèrement plus adverse que votre modèle, la simulation donne une fausse confiance

### Approche d'Optimisation par Théorie des Jeux

**Ce qu'elle fait** :
1. Spécifier un modèle de probabilité **nominal** $p_0$ et un ensemble d'incertitude (boule de Wasserstein)
2. Résoudre pour la **politique optimale** $\pi^*$ qui minimise le coût du pire cas
3. La Nature choisit simultanément la pire distribution $p^*$ dans l'ensemble d'incertitude
4. Équilibre : $(\pi^*, p^*)$ est un point-selle

**Résultats** : Politique optimale, coût du pire cas, prime de souveraineté (valeur de la robustesse)

**Avantages** :
- **Optimise la politique** : Dit quoi faire, pas juste évalue ce que vous avez proposé
- **Robuste à l'erreur de modèle** : Protège contre les déplacements distributionnels dans la boule-$\varepsilon$
- **Interprétable** : La politique $\pi^*$ est une règle de décision que vous pouvez implémenter

### Quand Utiliser Chaque Approche

| Approche | Utiliser Quand | Exemple |
|----------|----------------|---------|
| **Simulation** | Modèle fiable, vouloir comprendre la variabilité, communiquer la distribution de risque | Risque climatique avec bonnes données historiques, planification opérationnelle |
| **Théorie des jeux** | Modèle incertain, besoin de stratégie optimale, environnement adversarial | Risque politique, marchés concurrentiels, incertitude réglementaire |
| **Hybride** | Utiliser théorie des jeux pour trouver politique, simulation pour la tester | Optimiser avec jeu robuste, puis Monte Carlo sur scénarios extrêmes |

### Exemple : Risque Tarifaire

**Approche simulation** (évalue une politique donnée) :
- Input : "Si tarif arrive, attendre 2 ans puis couvrir" (heuristique choisie)
- Processus : Simuler 10,000 trajectoires avec $P(\text{tarif année 2}) = 15\%$
- Output : "Coût moyen = 42 unités, P90 = 51 unités, voici la distribution"

**Approche théorie des jeux** (optimise la politique) :
- Input : Modèle nominal avec $\varepsilon=0.3$ d'ambiguïté
- Processus : Résoudre minimax pour trouver $\pi^*(t,s)$ optimal contre Nature adversariale
- Output : "Politique optimale = couvrir immédiatement si tarif arrive + accélérer si $m \geq 2$. Coût pire cas robuste = 47.7 unités."

**Différence clé** : Simulation teste VOTRE stratégie. Théorie des jeux TROUVE la meilleure stratégie sous adversité.

**Laquelle est plus utile ?** Si vous ne savez pas quelle politique choisir ET vous ne faites pas confiance à vos prévisions, la théorie des jeux optimise pour vous.

---

## 5. Généralisation aux Jeux à N Joueurs

### Modèle Actuel : Jeu à Deux Joueurs

- **Entreprise** vs. **Nature**
- Somme nulle (presque) : L'entreprise minimise le coût, la Nature maximise sous contrainte
- Séquentiel : L'entreprise joue en premier chaque période, la Nature révèle l'état suivant

### Extension 1 : Oligopole Multi-Entreprises

**Configuration** : $n$ entreprises font face au même risque politique, doivent décider de stratégies de migration

**Question clé** : Migrez-vous tôt (signaler préoccupation, possiblement déclencher régulation) ou tard (profiter de la migration des autres, mais faire face à des contraintes de capacité) ?

**Structure du jeu** :
- **Joueurs** : Entreprises $i = 1, \ldots, n$ + Nature
- **Stratégies** : Chaque entreprise $i$ choisit politique $\pi_i(t, s_i, s_{-i})$ où $s_{-i}$ inclut les actions observées des autres entreprises
- **Gain** : Le coût de l'entreprise $i$ dépend de :
  - Propre progrès de migration
  - Migration agrégée de l'industrie (affecte prix fournisseur, attention politique)
  - Réponse de la Nature (peut dépendre de l'exode industriel visible)

**Concept de solution** : **Équilibre Parfait en Sous-Jeux de Markov (MPE)**
- La politique de chaque entreprise est optimale étant données les politiques des autres
- Pas de déviations crédibles (parfait en sous-jeux)
- La Nature joue adversement dans les contraintes

**Nouveaux phénomènes** :
- **Désavantage du premier joueur** : Les premiers migrateurs signalent faiblesse, paient une prime
- **Mimétisme** : Si d'autres migrent, je devrais aussi (multiplicité d'équilibres)
- **Échec de coordination** : Toutes les entreprises attendent, collectivement pires

**Défi computationnel** : Espace d'états maintenant inclut $s = (s_1, \ldots, s_n, \tau)$ - explosion avec $n$. Besoin :
- Approximation en champ moyen (grand $n$) : Suivre distribution des états d'entreprises
- MPE approché : Dynamiques de meilleure réponse, itération de politique
- Réduction de dimension : Statistiques agrégées (ex : "fraction de l'industrie migrée")

### Extension 2 : Gouvernement comme Joueur Stratégique

**Configuration** : Le gouvernement choisit une politique tarifaire anticipant les réponses des entreprises

**Structure du jeu** :
- **Joueur 1 (Gouvernement)** : Choisit trajectoire tarifaire $\{\tau_t\}$ pour maximiser objectif (soutien politique, balance commerciale, emploi domestique)
- **Joueur 2 (Entreprise)** : Choisit politique de migration $\pi$ pour minimiser coût donnée trajectoire tarifaire
- **Nature** : Chocs exogènes (résultats électoraux, relations internationales)

**Concept de solution** : **Équilibre de Stackelberg**
- Le gouvernement s'engage sur politique tarifaire (leader)
- L'entreprise répond optimalement avec politique de migration (suiveur)
- La Nature joue en dernier (ou simultanément)

**Induction à rebours** :
1. Résoudre problème entreprise pour toute trajectoire tarifaire : $\pi^*(\tau)$
2. Le gouvernement choisit $\tau^*$ optimal anticipant $\pi^*(\tau)$
3. Équilibre : $(\tau^*, \pi^*(\tau^*))$

**Implications politiques** :
- **La crédibilité compte** : Si le gouvernement ne peut s'engager (incohérence temporelle), l'entreprise s'attend à renégociation ex-post
- **Migration partielle comme assurance** : L'entreprise maintient flexibilité, le gouvernement perd levier
- **Négociation** : La politique tarifaire peut être résultat de négociation de Nash

### Extension 3 : Réseau de Chaîne d'Approvisionnement

**Configuration** : Chaîne d'approvisionnement multi-niveaux avec dépendances à chaque niveau

**Structure de graphe** :
- **Nœuds** : Entreprises à différents niveaux (Niveau 0 = assembleur final, Niveau 1 = fournisseurs directs, Niveau 2 = fabricants composants)
- **Arêtes** : Relations d'approvisionnement avec risque (exposition tarifaire, dépendances source unique)
- **Nature** : Les chocs se propagent à travers le réseau

**Dynamiques de jeu** :
- **Mouvements simultanés** : Toutes les entreprises choisissent stratégies de migration
- **Externalités de réseau** : La migration de votre fournisseur affecte vos coûts
- **Risque de cascade** : L'échec du Niveau 1 force migration d'urgence du Niveau 0

**Approche de solution** :
- **Équilibre de jeu de réseau** : Le gain de l'entreprise $i$ dépend des actions des voisins
- **Jeux potentiels** : Si le jeu a fonction potentielle, équilibre de Nash pur existe
- **Analyse de contagion** : Tester la résilience du réseau sous Nature adversariale

### Stratégies Computationnelles pour Jeux à N Joueurs

1. **Décomposition** : Séparer en sous-jeux (par géographie, horizon temporel)
2. **Approximation en champ moyen** : Remplacer interactions entreprises par statistiques agrégées
3. **Échantillonnage** : Monte Carlo Tree Search, modélisation opposant
4. **Apprentissage** : Apprentissage par renforcement multi-agents (si équilibre inconnu)

**Recommandation pratique** : Commencer avec version 2-3 joueurs pour comprendre mécanismes, puis passer à l'échelle avec approximations.

---

## 6. Étapes pour Connecter au Monde Réel des Affaires

### Étape 1 : Alignement des Parties Prenantes

**Objectif** : S'assurer que la direction comprend le cadre et adhère à l'approche

**Actions** :
1. **Briefing exécutif** : Présenter résultats du modèle jouet comme "preuve de concept"
   - Mettre l'accent sur la sortie politique (règles de décision) pas juste chiffres de coût
   - Montrer la prime de souveraineté comme coût d'ambiguïté quantifié
   - Démontrer sensibilité : comment résultats changent avec hypothèses

2. **Définir critères de succès** : Quelles décisions cela informera ?
   - Allocation budget diversification fournisseurs
   - Points de déclenchement pour accélérer migration
   - Termes contrat couverture (durée, clauses de rupture)

3. **Identifier sceptiques et adresser préoccupations** :
   - "Pourquoi pas juste utiliser notre modèle de risque existant ?" → Montrer théorie jeux gère Nature adversariale
   - "N'est-ce pas trop complexe ?" → Démontrer que politique est interprétable
   - "Pouvons-nous faire confiance ?" → Tester avec scénarios historiques

### Étape 2 : Collection de Données et Calibration

**Probabilités de transition tarifaire** $(p_{01}, p_{10})$ :
- **Données historiques** : Événements tarifaires secteurs pertinents sur 20 ans
- **Élicitation d'experts** : Enquête analystes politique commerciale, équipe relations gouvernementales
- **Indicateurs avancés** : Cycles électoraux, balance commerciale, tensions géopolitiques
- **Mise à jour bayésienne** : Commencer avec priors, mettre à jour quand régime se déroule

**Paramètres de coût** :
- **CAPEX (investissement, coûts sortie)** : Estimations ingénierie, devis vendeurs
  - Configuration programme investissement : Systèmes IT, contrats double source
  - Frais résiliation : Clauses rupture contrat, coûts dénouement
  - Coûts bascule : Logistique, reconversion, recertification
- **OPEX (coûts récurrents)** : Données comptables, prime projetée fournisseurs alternatifs
  - Période migration : Coûts double exécution, gestion projet, déplacements
  - Coûts tarifaires : Données douanes, estimations équipe politique
  - Coûts tarifaires couverts : Termes contrats (achat à terme, accords contenu local)

**Taux d'actualisation (WACC)** : Équipe finance fournit, typiquement 8-12% pour corporate

**Aversion au risque ($\alpha$ pour CVaR)** :
- Enquête appétit risque conseil/CFO : "Quelle probabilité de mauvais résultat est acceptable ?"
- Typique : $\alpha = 0.90$ (protéger pires 10%) à $\alpha = 0.95$ (pires 5%)

**Rayon d'ambiguïté** $\varepsilon(t)$ :
- Lier à **Indice d'Incertitude de Politique Économique (EPU)** (Baker et al. 2016)
- Mapper EPU vers $\varepsilon \in [0.02, 0.40]$ basé sur erreur prévision historique
- Variable dans temps : $\varepsilon$ plus élevé autour élections, négociations commerciales

### Étape 3 : Raffinement du Modèle

**Enrichir espace d'états** :
- **Tarifs multi-niveaux** : Pas binaire, mais bas/moyen/haut ($\tau \in \{0, 0.15, 0.25, 0.40\}$)
- **Migration partielle** : Progrès migration comme continu (% volume déplacé)
- **Capacité fournisseur** : Capacité fournisseur alternatif limitée (prime rareté)
- **Désagrégation régionale** : Sourcing Europe vs. Asie comme pistes migration séparées

**Ajouter actions réalistes** :
- **Sourcing hybride** : Diviser volume entre sources avec risque/coût différents
- **Renégociation contrat** : Payer prime pour ajouter clauses flexibilité
- **Lobbying politique** : Action coûteuse pour influencer $p_{10}$ (probabilité suppression tarif)
- **Construire propre capacité** : Option intensive en CAPEX pour éliminer dépendance fournisseur entièrement

**Engagement multi-périodes** :
- **Irréversibilité investissement** : Une fois migration démarrée, coûts irrécupérables partiels
- **Verrouillage couverture** : Contrats couverture multi-années limitent flexibilité future
- **Apprentissage par la pratique** : Migration devient moins chère/plus rapide quand organisation gagne expérience

### Étape 4 : Validation et Backtesting

**Contrefactuels historiques** :
- Appliquer modèle à épisodes passés (guerre commerciale 2018, règlementations UE)
- Comparer politique recommandée aux décisions réelles de l'entreprise
- Quantifier "regret" : Combien mieux aurait performé politique théorique des jeux ?

**Tests de stress** :
- **Analyse scénarios** : "Et si tarif=1 persistait pour horizon entier ?"
- **Chocs adversariaux** : Nature pire cas dans boule-$\varepsilon$ - la politique survit-elle ?
- **Sensibilité paramètres** : Si CAPEX est 50% plus élevé, l'action optimale change-t-elle ?

**Validation externe** :
- Comparer aux pairs industrie : Nos coûts migration sont-ils raisonnables ?
- Benchmark rayon ambiguïté : $\varepsilon$ impliqué par EPU vs. notre calibration
- Consulter experts : Les déclencheurs politique (ex : "couvrir si tarif persiste 2 ans") ont-ils sens business ?

### Étape 5 : Intégration aux Processus de Décision

**Mises à jour trimestrielles** :
- Re-résoudre modèle avec état mis à jour $(t, \tau, m, i, h, e)$ et dernier $\varepsilon(t)$ d'EPU
- Vérifier si action optimale a changé ("couvrir" → "accélérer" signifie seuil franchi)
- Rapporter tendance prime souveraineté au CFO

**Surveillance déclencheurs** :
- Implémenter tableau de bord suivant indicateurs pertinents politique :
  - Régime tarifaire actuel : Off/On
  - Progrès migration : X% complet
  - Indice EPU : Au-dessus/en-dessous seuil
- Alertes automatisées : "Politique optimale a changé - révision recommandée"

**Budgétisation et planification** :
- Intégrer prime souveraineté dans scénarios stress budget
- Allouer budget migration basé sur recommandations modèle
- Mettre de côté fonds contingence pour accélération si déclencheurs atteints

### Étape 6 : Amélioration Continue

**Boucle d'apprentissage** :
1. **Observer résultats** : Le tarif a-t-il évolué comme prévu ? Le coût migration était-il précis ?
2. **Mettre à jour croyances** : Mise à jour bayésienne sur $(p_{01}, p_{10})$, recalibrer fonctions coût
3. **Ré-optimiser** : Résoudre modèle mis à jour, comparer à politique précédente
4. **Itérer** : Réinjecter apprentissages dans Étape 2 (collection données)

**Extensions modèle selon besoin** :
- Ajouter nouveaux états (étapes conformité réglementaire, verrouillage technologique)
- Raffiner espace actions (vitesses migration granulaires)
- Version multi-joueurs si actions concurrents deviennent stratégiques

**Gouvernance** :
- **Propriétaire modèle** : Assigner équipe dédiée (stratégie/FP&A/risque)
- **Cadence révision** : Trimestrielle pour paramètres, annuelle pour structure
- **Piste audit** : Documenter hypothèses, enregistrer décisions politiques pour révision future

---

## Résumé : L'Avantage de la Théorie des Jeux

**Approche traditionnelle** : "Quelle est la VAN de la souveraineté ?"
- Chiffre de coût unique
- Suppose probabilités connues
- Pas de règle de décision, juste arbitrage statique

**Approche théorie des jeux** : "Quelle est la politique de migration optimale sous risque politique adversarial ?"
- Stratégie conditionnelle à l'état (règles si-alors)
- Robuste aux déplacements distributionnels (ambiguïté Wasserstein)
- Quantifie valeur de flexibilité (prime souveraineté)

**Point clé** : La théorie des jeux transforme la souveraineté d'un **problème de coût** en **problème stratégique**. Vous obtenez :
1. **Politique optimale** $\pi^*(t, s)$ - quoi faire dans chaque situation
2. **Coût pire cas** $V_0$ - budgétiser le risque baissier
3. **Prime souveraineté** - étiquette de prix sur incertitude politique
4. **Robustesse** - protection contre erreurs prévision dans boule-$\varepsilon$

C'est une **stratégie actionnable**, pas juste évaluation de risque.

---

## Lectures Complémentaires

**Fondations Théorie des Jeux** :
- von Neumann, J., & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton.
- Nash, J. (1950). "Equilibrium points in n-person games." *PNAS*, 36(1), 48-49.
- Fudenberg, D., & Tirole, J. (1991). *Game Theory*. MIT Press.

**Programmation Dynamique et Jeux Stochastiques** :
- Puterman, M. L. (2014). *Markov Decision Processes*. Wiley.
- Shapley, L. S. (1953). "Stochastic games." *PNAS*, 39(10), 1095-1100.

**Optimisation Robuste** :
- Ben-Tal, A., El Ghaoui, L., & Nemirovski, A. (2009). *Robust Optimization*. Princeton.
- Kuhn, D., et al. (2019). "Wasserstein distributionally robust optimization." *Operations Research*, 67(6), 1373-1416.

**Applications au Risque Politique/Réglementaire** :
- Baker, S. R., Bloom, N., & Davis, S. J. (2016). "Measuring economic policy uncertainty." *QJE*, 131(4), 1593-1636.
- Handley, K., & Limão, N. (2015). "Trade and investment under policy uncertainty." *AEJ: Economic Policy*, 7(4), 189-222.

---

**Auteur du Tutoriel** : Jean-Baptiste Dézard, Deal ex Machina SAS  
**Licence** : CC BY 4.0  
**Dernière Mise à Jour** : 2026

Pour questions ou feedback sur ce tutoriel, veuillez ouvrir une issue sur le dépôt GitHub.
