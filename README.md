# Sovereignty as Strategic Games: A Distributionally Robust Approach

## Overview

This repository implements a game-theoretic framework for supplier dependency and sovereignty decisions under political risk. The core thesis: **sovereignty is not a static cost-benefit problem but a dynamic sequential game between the firm and Nature**, where Nature represents adversarial political/regulatory dynamics.

## Documentation

### Core Materials
- **Main Notebook**: [`sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb`](sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb) - CFO-friendly walkthrough with executive summary
- **Game Theory Tutorial (EN)**: [`docs/game_theory_tutorial.md`](docs/game_theory_tutorial.md) - Comprehensive guide on game theory, minimax, Bellman equations, and n-player extensions
- **Tutoriel Theorie des Jeux (FR)**: [`docs/game_theory_tutorial_fr.md`](docs/game_theory_tutorial_fr.md) - Version francaise complete

### Strategic Framework (v2.0)
- **Unified Framework**: [`docs/bellman_wasserstein_mean_field_framework.md`](docs/bellman_wasserstein_mean_field_framework.md) - Comprehensive presentation of the Bellman-Wasserstein Mean-Field framework for strategic autonomy, including multi-criterion analysis, hierarchical game structure, and governance integration
- **Implementation Roadmap**: [`docs/implementation_roadmap.md`](docs/implementation_roadmap.md) - Phased roadmap (18-24 months) to transform the toy model into a production-grade Strategic Autonomy Operating System

## Why Games?

Traditional real options frameworks (Dixit & Pindyck, 1994) treat uncertainty as exogenous random shocks. This misses the strategic dimension: political actors respond to firm actions, regulatory regimes exhibit persistence and switching dynamics, and forecast errors are not random but potentially adversarial.

We model sovereignty as a finite-horizon Markov game:
- **Player 1 (Firm)**: Chooses actions {wait, invest, hedge, accelerate, exit} to minimize cost
- **Player 2 (Nature)**: Controls tariff regime transitions and, under ambiguity, selects adversarial next-state distributions within a Wasserstein ball

This framing captures:
1. **Strategic optionality**: The firm's decision is a policy (state-contingent action rule), not a one-time choice
2. **Ambiguity aversion**: Nature can shift transition probabilities within an uncertainty set, forcing robust policies
3. **Path dependence**: Migration progress, investment sunk costs, and hedge effectiveness evolve endogenously

## Mathematical Formulation

### State Space
State $s = (\tau, m, \mathbf{f})$ where:
- $\tau \in \{0,1\}$: tariff regime (off/on)
- $m \in \{0, \ldots, M\}$: migration progress (years to exit)
- $\mathbf{f} = (i, h, e)$: binary flags for investment started, hedge active, exit exercised

### Action Space
Firm chooses $a_t \in \mathcal{A} = \{\text{wait}, \text{invest}, \text{hedge}, \text{accelerate}, \text{exit}\}$

### Nominal Dynamics
Tariff transitions follow a parameterized Markov chain:
$$P(\tau_{t+1} = 1 | \tau_t = 0) = p_{01}, \quad P(\tau_{t+1} = 0 | \tau_t = 1) = p_{10}$$

Migration progress evolves deterministically: $m_{t+1} = \min(M, m_t + \Delta_m(a_t))$

Flags update based on actions and progress (see notebook for full transition kernel).

### Objective: Robust CVaR
We solve for the policy $\pi^*$ that minimizes worst-case tail risk:
$$V_t(s) = \min_{a \in \mathcal{A}} \sup_{p \in \mathcal{P}_{\varepsilon(t)}(p_0)} \text{CVaR}_\alpha^p \left[ \gamma_t \ell(t, s, a) + V_{t+1}(S') \right]$$

where:
- $\text{CVaR}_\alpha$: Conditional Value-at-Risk at level $\alpha$ (tail-risk measure)
- $\mathcal{P}_{\varepsilon}(p_0)$: Wasserstein ball of radius $\varepsilon$ around nominal distribution $p_0$
- $\ell(t,s,a)$: stage cost (CAPEX + OPEX + tariff exposure + exit costs)
- $\gamma_t = (1+r)^{-t}$: discount factor (WACC-based)

The Wasserstein distance constraint ensures robustness to forecast errors while avoiding worst-case conservatism of full minimax approaches.

## Key Innovations

### 1. Progressive Hedge Effectiveness
Unlike binary hedge models, we implement $\eta(m) = m/M$ effectiveness scaling: hedge value increases with migration progress, capturing the business reality that alternative suppliers become more viable as you build relationships and dual-source.

### 2. Time-Varying Ambiguity
The ambiguity radius $\varepsilon(t)$ is linked to observable political risk indicators:
$$\varepsilon(t) = \varepsilon_{\min} + (\varepsilon_{\max} - \varepsilon_{\min}) \cdot R(t)$$
where $R(t) \in [0,1]$ could be calibrated to policy uncertainty indices (Baker et al., 2016), election cycles, or trade negotiation windows.

### 3. Separation of Risk and Ambiguity
The model distinguishes:
- **Risk** (Level 1): Tail events under known distribution → CVaR optimization
- **Ambiguity** (Level 2): Unknown distribution within Wasserstein set → DRO

This separation is critical for correct pricing of uncertainty (Gilboa & Schmeidler, 1989; Hansen & Sargent, 2008).

## Extensions Beyond Toy Model

The current implementation simplifies:
1. **Binary tariff regime**: Real tariffs have magnitude, gradual phase-in, and sectoral heterogeneity
2. **Single supplier**: Multi-supplier portfolios require network flow formulation
3. **Deterministic migration**: Add learning-by-doing (Arrow, 1962) and implementation risk
4. **Exogenous transitions**: Endogenize political response to firm actions (leader-follower structure)
5. **Perfect state observability**: Add partial observability (POMDP formulation)

Production extensions should:
- Calibrate transition probabilities to historical trade policy data
- Link $\varepsilon(t)$ to market-implied ambiguity (option skew, credit spreads)
- Add capacity constraints and organizational friction
- Model competitive dynamics (oligopoly migration game)
- Incorporate learning: Bayesian update of $p_{01}, p_{10}$ as tariff regime unfolds

## Related Literature

### Game Theory Foundations
- von Neumann, J., & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton University Press.
- Nash, J. F. (1950). Equilibrium points in n-person games. *Proceedings of the National Academy of Sciences*, 36(1), 48-49. DOI: [10.1073/pnas.36.1.48](https://doi.org/10.1073/pnas.36.1.48)
- Fudenberg, D., & Tirole, J. (1991). *Game Theory*. MIT Press.

### Dynamic Programming and Bellman Equations
- Bellman, R. (1957). *Dynamic Programming*. Princeton University Press.
- Puterman, M. L. (2014). *Markov Decision Processes: Discrete Stochastic Dynamic Programming*. John Wiley & Sons.
- Shapley, L. S. (1953). Stochastic games. *Proceedings of the National Academy of Sciences*, 39(10), 1095-1100. DOI: [10.1073/pnas.39.10.1095](https://doi.org/10.1073/pnas.39.10.1095)

### Real Options and Investment Under Uncertainty
- Dixit, A. K., & Pindyck, R. S. (1994). *Investment under Uncertainty*. Princeton University Press.
- Trigeorgis, L. (1996). *Real Options: Managerial Flexibility and Strategy in Resource Allocation*. MIT Press.

### Robust Optimization and Distributional Robustness
- Ben-Tal, A., El Ghaoui, L., & Nemirovski, A. (2009). *Robust Optimization*. Princeton University Press.
- Kuhn, D., Mohajerin Esfahani, P., Nguyen, V. A., & Shafieezadeh-Abadeh, S. (2019). Wasserstein distributionally robust optimization: Theory and applications in machine learning. *Operations Research*, 67(6), 1373-1416. DOI: [10.1287/opre.2019.1902](https://doi.org/10.1287/opre.2019.1902)
- Blanchet, J., & Murthy, K. (2019). Quantifying distributional model risk via optimal transport. *Mathematics of Operations Research*, 44(2), 565-600. DOI: [10.1287/moor.2018.0936](https://doi.org/10.1287/moor.2018.0936)

### Risk Measures and CVaR
- Rockafellar, R. T., & Uryasev, S. (2002). Conditional value-at-risk for general loss distributions. *Journal of Banking & Finance*, 26(7), 1443-1471. DOI: [10.1016/S0378-4266(02)00271-6](https://doi.org/10.1016/S0378-4266(02)00271-6)
- Acerbi, C., & Tasche, D. (2002). On the coherence of expected shortfall. *Journal of Banking & Finance*, 26(7), 1487-1503. DOI: [10.1016/S0378-4266(02)00269-8](https://doi.org/10.1016/S0378-4266(02)00269-8)

### Decision Theory Under Ambiguity
- Gilboa, I., & Schmeidler, D. (1989). Maxmin expected utility with non-unique prior. *Journal of Mathematical Economics*, 18(2), 141-153. DOI: [10.1016/0304-4068(89)90018-9](https://doi.org/10.1016/0304-4068(89)90018-9)
- Hansen, L. P., & Sargent, T. J. (2008). *Robustness*. Princeton University Press.
- Maccheroni, F., Marinacci, M., & Rustichini, A. (2006). Ambiguity aversion, robustness, and the variational representation of preferences. *Econometrica*, 74(6), 1447-1498. DOI: [10.1111/j.1468-0262.2006.00716.x](https://doi.org/10.1111/j.1468-0262.2006.00716.x)

### Policy Uncertainty and Economic Impact
- Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. *Quarterly Journal of Economics*, 131(4), 1593-1636. DOI: [10.1093/qje/qjw024](https://doi.org/10.1093/qje/qjw024)
- Handley, K., & Limão, N. (2015). Trade and investment under policy uncertainty: Theory and firm evidence. *American Economic Journal: Economic Policy*, 7(4), 189-222. DOI: [10.1257/pol.20140068](https://doi.org/10.1257/pol.20140068)

### Learning in Dynamic Environments
- Arrow, K. J. (1962). The economic implications of learning by doing. *Review of Economic Studies*, 29(3), 155-173. DOI: [10.2307/2295952](https://doi.org/10.2307/2295952)

## Implementation Details

**Language**: Python 3.11+  
**Key Dependencies**:
- `cvxpy`: Convex optimization for Wasserstein DRO inner problem
- `numpy`: Numerical linear algebra
- `pydantic`: Type-safe parameter specification

**Solver**: CLARABEL (primary) with SCS fallback for conic programs (Wasserstein optimal transport)
- CLARABEL: Modern Rust-based conic solver with excellent numerical stability
- SCS: Splitting Conic Solver as fallback for robustness

**Computational Complexity**: $O(T \cdot |S| \cdot |A| \cdot n_{\text{LP}})$ where:
- $T$: horizon length (10 years)
- $|S|$: state space size (64 states)
- $|A|$: action space size (5 actions)
- $n_{\text{LP}}$: LP solve time for Wasserstein ball projection (~10-50ms)

For horizons $T > 20$ or state spaces $|S| > 1000$, consider approximate DP methods (fitted value iteration, deep RL).

## Usage

**For CFOs and Business Leaders**:
- Start with the main notebook [`sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb`](sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb)
- Jump to Section 9 for results and Section 11 for interpretation
- Review Executive Summary at the end for AI-generated synthesis

**For Quant Teams**:
- Read [`docs/game_theory_tutorial.md`](docs/game_theory_tutorial.md) for theoretical foundations
- Focus on notebook Sections 2-8 for methodology
- Review Section 10 for sensitivity analysis

**For French Speakers**:
- Voir [`docs/game_theory_tutorial_fr.md`](docs/game_theory_tutorial_fr.md) pour guide complet 🇫🇷

**Parameter Calibration**:
1. Estimate $(p_{01}, p_{10})$ from historical tariff transition data or political risk scores
2. Set $\varepsilon(t)$ based on option-implied volatility skew or analyst forecast dispersion
3. Calibrate costs to actual supplier contracts and migration cost estimates
4. Validate CVaR level $\alpha$ against firm's risk appetite (typically 0.90-0.95)

## Citation

If you use this framework in research or production models, please cite:

```
@misc{sovereignty-games-2026,
  title={Sovereignty as Strategic Games: A Distributionally Robust Approach to Supplier Dependency},
  author={Jean-Baptiste Dézard},
  organization={Deal ex Machina SAS},
  year={2026},
  howpublished={\url{https://github.com/jeanbaptdzd/DP-CVaR-Wasserstein}},
  note={First draft toy model for strategic decision analysis under political risk}
}
```

## Author

**Jean-Baptiste Dézard**  
Deal ex Machina SAS

## License

This work is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/

You are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made

## Contact

For technical questions regarding this framework, please open an issue on the GitHub repository.

---

**Disclaimer**: This is a first-draft toy model for research and education purposes. Not intended for direct production use without extensive validation, calibration, and risk management review.

**Important**: This is vibe research - it may contain slop. Use at your own risk :)
