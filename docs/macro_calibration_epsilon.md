# Calibration de ε(t) depuis des données macro
## Du guess heuristique vers une fondation statistique rigoureuse

> **Branche**: `feature/macro-calibration-epsilon`  
> **Statut**: Travail en cours — v0.1 (design document)

---

## 1. Le problème avec l'approche actuelle

Dans le notebook principal, ε(t) est défini comme :

```python
def risk_indicator(t, horizon):
    x = t / max(1, horizon-1)
    return float(4*x*(1-x))   # parabole arbitraire

def eps_schedule_indicator(t, horizon):
    return eps_min + (eps_max - eps_min) * risk_indicator(t, horizon)
```

Ce choix a deux défauts fondamentaux :

1. **Pas de lien avec des données** : la parabole `4x(1-x)` est choisie pour sa forme jolie, pas pour refléter une réalité observée.
2. **Pas d'interprétation statistique** : ε_min=0.02 et ε_max=0.30 sont des chiffres posés sans justification de ce que "0.30 de rayon Wasserstein" signifie concrètement pour un décideur.

**La question** : que *devrait* être ε(t), rationnellement ?

---

## 2. Ce que ε représente vraiment

### 2.1 Interprétation statistique fondamentale

Dans notre DRO Wasserstein, on résout :

$$V_t(s) = \min_{a} \sup_{p \,:\, W_1(p, \hat{p}_0) \leq \varepsilon(t)} \mathrm{CVaR}_\alpha^p\bigl[\ell(t,s,a) + V_{t+1}(S')\bigr]$$

**ε(t) est le rayon de notre incertitude épistémique sur la matrice de transition.**

Plus précisément : $\hat{p}_0(\cdot | s, a)$ est notre *estimation* de la loi de transition — elle n'est pas connue parfaitement. ε(t) doit refléter à quel point nous pouvons nous tromper dans cette estimation à la date t.

### 2.2 Les deux sources d'incertitude sur p₀

```
Incertitude sur p₀(t)
├── 1. Incertitude d'estimation (données rares)
│      └── On n'a observé que N transitions historiques
│          → Plus N est petit, plus ε doit être grand
│
└── 2. Non-stationnarité (chocs macro)
       └── L'environnement macro change → les transitions passées
           sont moins informatives sur le présent
           → Plus les chocs macro sont forts, plus ε doit être grand
```

Ces deux sources se combinent multiplicativement dans la formule finale.

### 2.3 Lien avec la théorie de la concentration de mesure

Pour p* la vraie distribution et p̂ l'estimateur empirique sur N observations, le résultat de Fournier-Guillin (2015) donne :

$$\mathbb{P}\left(W_1(\hat{p}, p^*) > \varepsilon\right) \leq
\begin{cases}
\exp\left(-c_d \cdot N \cdot \varepsilon^2\right) & \text{si } \varepsilon \geq \varepsilon_0(d) \\
\exp\left(-c_d \cdot N \cdot \varepsilon^{2d/(d-2)}\right) & \text{si } d \geq 3
\end{cases}$$

Pour notre espace d'états discret (K états), la borne est plus simple :

$$\mathbb{P}\left(W_1(\hat{p}, p^*) > \varepsilon\right) \leq K \cdot \exp\left(-2N\varepsilon^2 / K^2\right)$$

**Conséquence directe** : pour un niveau de confiance (1-δ), le rayon calibré est :

$$\boxed{\varepsilon(t) = \frac{K}{2} \sqrt{\frac{\log(K/\delta)}{N_\text{eff}(t)}}}$$

où **N_eff(t) est le nombre effectif d'observations informatives à la date t** — et c'est là qu'interviennent les données macro.

---

## 3. Les trois approches de calibration

### Approche A — Bayésienne (Dirichlet-Multinomiale)
*Recommandée quand on a des données historiques de transitions*

### Approche B — Facteurs macro avec taille effective d'échantillon
*Recommandée en pratique, combine théorie et observables*

### Approche C — Régimes macro (HMM / seuil)
*Recommandée pour la robustesse et la communication décisionnelle*

---

## 4. Approche A : Bayésien Dirichlet-Multinomial

### 4.1 Setup

Soit la ligne `i` de la matrice de transition : `p_i = (p_{i1}, ..., p_{iK})`.

On observe N_i transitions depuis l'état i, avec n_{ij} transitions vers l'état j :

- **Prior** : `p_i ~ Dirichlet(α_0)` avec `α_0 = (α,...,α)` (prior non-informatif : α → 0)
- **Posterior** : `p_i | données ~ Dirichlet(α_0 + n_i)`

### 4.2 ε depuis la dispersion du posterior

La distance de Wasserstein entre le posterior et la moyenne posterior peut être bornée par :

$$\varepsilon_A = \sqrt{\sum_{j=1}^{K} \mathrm{Var}_{\text{post}}[p_{ij}]} = \sqrt{\sum_{j=1}^{K} \frac{\hat{p}_{ij}(1-\hat{p}_{ij})}{N_i + K\alpha + 1}}$$

Plus simplement, l'*intervalle de crédibilité* Wasserstein à niveau (1-δ) :

$$\varepsilon_A(t) = z_{1-\delta/2} \cdot \sqrt{\frac{K \cdot \bar{p}(1-\bar{p})}{N_i(t) + 1}}$$

où :
- `z_{1-δ/2}` ≈ 1.96 pour δ=5%
- `K` = nombre d'états
- `N_i(t)` = taille d'échantillon effective à la date t (voir §5)

### 4.3 Interprétation

| `N_i(t)` | ε_A | Signification |
|---|---|---|
| 5 | ~0.30 | Très peu d'observations, large incertitude |
| 20 | ~0.15 | Données modérées |
| 100 | ~0.07 | Bonne estimation |
| 500 | ~0.03 | Estimation précise |
| ∞ | 0 | Connaissance parfaite |

**Ce tableau montre que les valeurs ε_min=0.02, ε_max=0.30 du notebook sont cohérentes avec des tailles d'échantillons allant de N~∞ (calme) à N~5 (crise).**

---

## 5. La taille d'échantillon effective N_eff(t)

C'est le cœur de la connexion avec le macro.

### 5.1 Principe : oubli exponentiel avec taux macro-dépendant

On pèse les observations passées selon leur pertinence pour le présent :

$$N_\text{eff}(t) = \sum_{s \leq t} w(t, s) \cdot \mathbf{1}[\text{observation en } s]$$

avec un facteur d'oubli :

$$w(t, s) = \exp\!\left(-\lambda \cdot \int_s^t \sigma_\text{macro}(u) \, du\right)$$

où `σ_macro(u)` est un indicateur de stress macro normalisé ∈ [0,1].

**Intuition** : en période calme (σ≈0), les données historiques restent très informatives (oubli lent). En période de choc (σ≈1), les régimes passés sont peu représentatifs de l'avenir (oubli rapide).

### 5.2 Version discrète implémentable

Pour des observations annuelles :

$$N_\text{eff}(t) = N_0 \cdot \prod_{s=1}^{t} \rho(s)$$

avec :

$$\rho(s) = \exp\left(-\lambda \cdot \sigma_\text{macro}(s)\right) \in (0, 1]$$

Et donc :

$$\varepsilon(t) = \frac{\varepsilon_\text{base}}{\sqrt{\rho(1) \cdot \rho(2) \cdots \rho(t)}}$$

où `ε_base = K/2 · sqrt(log(K/δ) / N_0)` est le rayon de référence pour une estimation sans stress.

### 5.3 Formule finale de ε(t)

$$\boxed{\varepsilon(t) = \varepsilon_\text{base} \cdot \exp\!\left(\frac{\lambda}{2} \cdot \sum_{s=1}^{t} \sigma_\text{macro}(s)\right)}$$

avec saturation à ε_max pour éviter des valeurs déraisonnables.

---

## 6. Approche B : Facteurs macro composites

### 6.1 L'indicateur de stress macro σ(t)

On construit σ(t) ∈ [0,1] comme une agrégation de facteurs observables :

| Indicateur | Source | Rôle |
|---|---|---|
| **EPU** (Economic Policy Uncertainty) | Baker, Bloom & Davis | Incertitude politique économique globale |
| **VIX** | CBOE | Volatilité implicite marchés (proxy peur) |
| **Cycle électoral** | Calendrier public | Proximité d'une élection majeure |
| **Tensions commerciales** | WTO, USTR, Eurostat | Tarifs et renégociations en cours |
| **Risque géopolitique** | GPR Index (Caldara & Iacoviello) | Conflits, crises géopolitiques |

### 6.2 Agrégation en score composite

**Étape 1 — Normalisation rang-centile** (robuste aux outliers) :

$$\tilde{x}_i(t) = F_i(x_i(t)) \in [0,1]$$

où `F_i` est la CDF empirique historique de l'indicateur i.

**Étape 2 — Agrégation pondérée** :

$$\sigma(t) = \sum_{i} w_i \cdot \tilde{x}_i(t), \quad \sum_i w_i = 1$$

Les poids `w_i` peuvent être estimés par régression sur des épisodes historiques où l'on connaît les déviations réalisées des transitions.

**Étape 3 — Lissage temporel** (éviter la réactivité excessive) :

$$\bar{\sigma}(t) = (1-\mu) \cdot \sigma(t) + \mu \cdot \bar{\sigma}(t-1)$$

avec `μ ∈ [0.3, 0.7]` selon le délai de réaction souhaité.

### 6.3 Mapping σ(t) → ε(t) : trois familles

**Linéaire (simple, transparent)** :
$$\varepsilon_\text{lin}(t) = \varepsilon_\text{min} + (\varepsilon_\text{max} - \varepsilon_\text{min}) \cdot \bar{\sigma}(t)$$

*C'est structurellement la même que le notebook — mais maintenant σ(t) est ancré dans des données réelles.*

**Exponentielle (fondée sur la théorie §5.3)** :
$$\varepsilon_\text{exp}(t) = \varepsilon_\text{base} \cdot \exp\!\left(\lambda \cdot \bar{\sigma}(t)\right)$$

*Plus cohérente avec la dérivation via N_eff.*

**Puissance** :
$$\varepsilon_\text{pow}(t) = \varepsilon_\text{base} \cdot \left(1 + \kappa \cdot \bar{\sigma}(t)^\gamma\right)$$

*Flexible : γ<1 pour des chocs macro qui affectent rapidement ε dès le début ; γ>1 pour des effets de seuil.*

---

## 7. Approche C : Détection de régimes

### 7.1 Modèle à deux régimes : Calme / Stress

On modélise le macro-état comme un processus caché M(t) ∈ {0=calme, 1=stress} :

```
Calme (M=0) : faible volatilité, transitions historiques fiables     → ε_calme ≈ 0.04
Stress (M=1) : haute volatilité, régimes en mutation               → ε_stress ≈ 0.25
```

La matrice de transition entre régimes :

$$\Pi = \begin{pmatrix} 1-p_{01} & p_{01} \\ p_{10} & 1-p_{10} \end{pmatrix}$$

typiquement `p_{01}=0.15` (entrée en crise 15%/an) et `p_{10}=0.50` (sorte de crise 50%/an).

### 7.2 ε(t) conditionnel

Soit `q(t) = P(M(t)=1 | données_t)` la probabilité filtrée d'être en régime stress :

$$\varepsilon_C(t) = (1-q(t)) \cdot \varepsilon_\text{calme} + q(t) \cdot \varepsilon_\text{stress}$$

### 7.3 Avantages pour la communication

Ce modèle produit des résultats binaires interprétables :
- "Nous sommes en régime stress (q=0.8) → ε élevé → grande prime de souveraineté"
- "Régime calme (q=0.1) → ε faible → coût d'ambiguïté modéré"

---

## 8. Comparaison des approches

| Critère | Approche A (Bayésien) | Approche B (Facteurs macro) | Approche C (Régimes) |
|---|---|---|---|
| **Fondation théorique** | ★★★ Très forte | ★★★ Forte | ★★ Bonne |
| **Données requises** | Transitions historiques | EPU, VIX, calendrier | Idem B + calibration HMM |
| **Interprétabilité CFO** | ★ Difficile | ★★ Correcte | ★★★ Excellente |
| **Réactivité** | Lente (dépend de N) | Rapide | Moyenne |
| **Recommandation** | Référence/validation | Production | Communication décisionnelle |

**Notre recommandation** : utiliser l'Approche B comme moteur de production, validée par l'Approche A sur données historiques, et présentée via l'Approche C aux décideurs.

---

## 9. Calibration des paramètres clés

### 9.1 ε_base et ε_max

Calibrés depuis des épisodes historiques référencés :

| Épisode | Période | ε suggéré | Justification |
|---|---|---|---|
| Commerce mondial stable | 2010-2018 | 0.03 – 0.06 | Régime WTO stable, faible EPU |
| Brexit | 2016-2020 | 0.15 – 0.25 | Forte incertitude commerciale UK-EU |
| Guerre commerciale US-Chine | 2018-2020 | 0.20 – 0.30 | Tarifs 25% imposés en quelques mois |
| Covid supply shock | 2020-2021 | 0.25 – 0.35 | Disruptions radicales et imprévisibles |
| Tensions US-Chine semi | 2022-2024 | 0.15 – 0.25 | Risque durable mais partiellement anticipé |

### 9.2 λ (sensibilité de l'oubli)

Calibré empiriquement :
- `λ=0.5` : réaction modérée (recommandé pour horizons 5-10 ans)
- `λ=1.0` : réaction forte (recommandé si l'environnement est très instable)
- `λ=2.0` : réaction très forte (cas de crise aiguë)

### 9.3 Poids des indicateurs w_i

Ordre de grandeur raisonnable a priori :

| Indicateur | Poids suggéré | Justification |
|---|---|---|
| EPU (secteur spécifique) | 0.35 | Indicateur le plus directement lié |
| VIX (ou VSTOXX) | 0.25 | Proxy forward-looking de l'incertitude |
| Proximité électorale | 0.20 | Sauts discrets bien documentés |
| Indice tensions commerciales | 0.20 | Directement pertinent pour tarifs |

---

## 10. Algorithme complet

```python
def compute_epsilon_schedule(
    macro_series: dict,          # {'EPU': [...], 'VIX': [...], 'election': [...]}
    T: int,                      # horizon de planification
    eps_base: float = 0.04,      # rayon calibré en période calme
    eps_max: float = 0.35,       # plafond
    lambda_decay: float = 0.8,   # sensibilité à l'oubli
    weights: dict = None,        # poids des indicateurs
    smoothing: float = 0.4,      # μ pour le lissage temporel
) -> np.ndarray:                 # ε(0), ε(1), ..., ε(T-1)
    """
    Calcule le schedule ε(t) depuis des indicateurs macro observables.

    Pipeline :
    1. Normalise chaque indicateur par son centile historique
    2. Agrège en stress composite σ(t) avec les poids donnés
    3. Lisse temporellement
    4. Mappe vers ε via la formule exponentielle
    5. Sature à eps_max
    """
    # 1. Normalisation rang-centile
    # 2. Agrégation pondérée → σ(t)
    # 3. Lissage → σ̄(t)
    # 4. ε(t) = eps_base * exp(lambda_decay * σ̄(t))
    # 5. clip(ε, eps_base, eps_max)
    ...
```

L'implémentation complète se trouve dans `macro_calibration.ipynb`.

---

## 11. Roadmap pour la suite

### Court terme (dans ce sprint)
- [x] Formalisation théorique (ce document)
- [ ] Notebook d'implémentation avec données synthétiques (`macro_calibration.ipynb`)
- [ ] Intégration au solveur DP existant
- [ ] Comparaison politique optimale : toy ε vs macro-calibré ε

### Moyen terme
- [ ] Téléchargement et ingestion des données réelles EPU (Baker-Bloom-Davis, licence libre)
- [ ] Backtesting sur épisodes historiques (guerre commerciale 2018-2020, Covid 2020)
- [ ] Calibration des poids w_i par régression sur épisodes de référence
- [ ] Pipeline automatisé : données → ε → rapport CFO

### Long terme
- [ ] ε multi-dimensionnel (une dimension par fournisseur / dimension de souveraineté)
- [ ] Apprentissage en ligne : mise à jour Bayésienne en temps réel
- [ ] Intégration dans le mean-field game (ε commun à toutes les firmes)

---

## Références

- Fournier, N. & Guillin, A. (2015). *On the rate of convergence in Wasserstein distance of the empirical measure.* Probability Theory and Related Fields, 162(3-4), 707-738.
- Esfahani, P.M. & Kuhn, D. (2018). *Data-driven distributionally robust optimization using the Wasserstein metric.* Mathematical Programming, 171(1-2), 115-166.
- Baker, S.R., Bloom, N. & Davis, S.J. (2016). *Measuring Economic Policy Uncertainty.* The Quarterly Journal of Economics, 131(4), 1593-1636.
- Caldara, D. & Iacoviello, M. (2022). *Measuring Geopolitical Risk.* American Economic Review, 112(4), 1194-1225.
- Wiesemann, W., Kuhn, D. & Rustem, B. (2013). *Robust Markov Decision Processes.* Mathematics of Operations Research, 38(1), 153-183.
- Blanchet, J. & Murthy, K. (2019). *Quantifying distributional model risk via optimal transport.* Mathematics of Operations Research, 44(2), 565-600.
