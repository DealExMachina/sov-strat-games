# Game Theory for Strategic Decision-Making Under Uncertainty: A Practical Guide

## Introduction

This tutorial explains why and how game theory provides a superior framework for modeling strategic dependencies, particularly when facing adversarial or semi-random actors like "Nature" (political risk, regulatory changes, market conditions). We focus on the sovereignty model as a concrete example.

---

## 1. A Short History of Game Theory

### The Foundations (1920s-1950s)

**John von Neumann** laid the mathematical foundations in the 1920s, proving the **minimax theorem** (1928): in zero-sum two-player games, there exists an optimal mixed strategy for each player. This was revolutionary because it showed that rational behavior under conflict has a mathematical structure.

**Theory of Games and Economic Behavior** (1944, von Neumann & Morgenstern) formalized game theory as a field, introducing:
- Normal form games (payoff matrices)
- Extensive form games (game trees)
- Coalition behavior in n-player games

### The Nash Revolution (1950s)

**John Nash** generalized von Neumann's results to non-zero-sum games, proving that every finite game has at least one **Nash equilibrium** (1950). This was profound: even when players' interests aren't perfectly opposed, there exist stable strategy profiles where no player can unilaterally improve their outcome.

Nash equilibrium became the central solution concept in economics, showing that rational agents can reach predictable outcomes even without coordination.

### Applications Explosion (1960s-present)

- **Economics**: Auction theory, contract theory, industrial organization (Harsanyi, Selten, Myerson)
- **Political science**: Voting theory, international relations, conflict resolution
- **Biology**: Evolutionary game theory (Maynard Smith) - stable strategies in populations
- **Computer science**: Algorithmic game theory, mechanism design, online markets

**Dynamic games** (1970s+): Shapley, Aumann, and others extended to repeated games and stochastic games, enabling analysis of long-term strategic interactions with uncertainty.

### Modern Developments

- **Behavioral game theory** (1990s+): Incorporating bounded rationality, social preferences
- **Algorithmic game theory** (2000s+): Computational complexity, learning in games
- **Robust game theory** (2010s+): Games under ambiguity about opponent types or payoffs

---

## 2. Why Game Theory for Dependencies and Adversarial Actors?

### The Nature of Strategic Dependencies

Traditional decision theory assumes **passive environment**: you make choices, nature generates random outcomes from a known distribution. This fails when:

1. **Adversarial actors exist**: Regulators respond to your strategies, competitors react to your moves, suppliers may exploit dependencies
2. **Nature is semi-adversarial**: Political risk isn't purely random - bad outcomes cluster, policies persist, worst cases happen when you're vulnerable
3. **Feedback loops matter**: Your action (e.g., starting migration) changes the environment (supplier may raise prices, regulator may notice)

### Why Not Just Use Probabilities?

**Problem**: Assigning a single probability $p$ to "tariff happens" assumes:
- You know $p$ precisely (often false - political forecasting is hard)
- The tariff probability is independent of your actions (false - visible migration may trigger political response)
- Worst-case scenarios are just "tail events" (false - adversarial Nature can shift probabilities against you)

**Game theory solution**: Model Nature as a **player** that:
- Chooses from a set of strategies (tariff regimes, timing)
- Has an objective (in zero-sum: hurt you; in robust optimization: shift probabilities adversarially)
- Reacts to your choices (at minimum, within structural constraints)

### The Three Layers of Uncertainty

1. **Risk** (Level 0): Known probability distribution
   - Example: Fair coin flip, well-calibrated historical data
   - Tool: Expected value, variance

2. **Strategic risk** (Level 1): Opponent's strategy unknown but rational
   - Example: Competitor pricing, supplier negotiation
   - Tool: Nash equilibrium, minimax

3. **Ambiguity** (Level 2): Probability distribution itself uncertain
   - Example: Political risk in new regime, unprecedented crisis
   - Tool: Robust optimization, Wasserstein DRO, maxmin expected utility

**This model addresses all three**: We use CVaR for risk aversion, game framing for strategic interactions, and Wasserstein balls for ambiguity.

### When to Use Game Theory vs. Simple Optimization

**Use game theory when:**
- Outcomes depend on others' choices (competitors, regulators, suppliers)
- The "opponent" has objectives (even if just self-interest)
- First-mover advantage or commitment value matters
- You need to find robust strategies against worst-case responses

**Use simple optimization when:**
- Environment is truly passive (weather, machine failure from wear)
- You have overwhelming information advantage
- Speed matters more than robustness (tactical decisions)

---

## 3. This First Simple Example: The Min-Max Approach

### The Two-Player Game Structure

**Players**:
- **Firm** (minimizing player): Chooses actions $a \in \{\text{wait}, \text{invest}, \text{hedge}, \text{accelerate}, \text{exit}\}$
- **Nature** (maximizing player): Controls tariff regime and (under ambiguity) transition probabilities

**Why "Nature" as Player?**

Nature isn't malicious, but modeling political/regulatory risk as an adversarial player:
1. **Protects against Murphy's Law**: "Whatever can go wrong, will go wrong, at the worst possible time"
2. **Captures clustering**: Bad events correlate - tariffs persist, crises deepen
3. **Conservative but rational**: Better to over-prepare for political risk than be caught flat-footed

### The Value Function: Minimax Bellman Equation

At each time $t$ and state $s$, we solve:

$$V_t(s) = \min_{a \in \mathcal{A}} \max_{p \in \mathcal{P}_\varepsilon(p_0)} \text{CVaR}_\alpha^p\left[\gamma_t \ell(s,a) + V_{t+1}(S')\right]$$

**Translation**:
- **Firm minimizes** by choosing action $a$
- **Nature maximizes** by shifting next-state distribution $p$ within Wasserstein ball $\mathcal{P}_\varepsilon$
- **CVaR** captures tail risk (worst $1-\alpha$ outcomes)
- **$\ell(s,a)$** is stage cost (CAPEX + OPEX + tariff)
- **$V_{t+1}$** is future cost-to-go

### Why Minimax Works Here

**Conservative but not paranoid**: The Wasserstein constraint $\varepsilon$ limits how adversarial Nature can be. Think of it as:
- $\varepsilon = 0$: Trust your forecast completely (standard DP)
- $\varepsilon = 0.1$: Allow Nature to shift probabilities slightly (robust)
- $\varepsilon = \infty$: Pure worst-case (too conservative)

We calibrate $\varepsilon(t)$ to political risk indicators, making ambiguity time-varying and observable.

### The Output: A Policy, Not a Decision

**Key insight**: We don't get "invest now" or "wait forever" - we get a **state-contingent policy** $\pi(t, s)$ that says:
- **If** tariff is off, migration at 0, no hedge → wait
- **If** tariff turns on, migration at 0, no hedge → hedge
- **If** tariff persists, migration at 2, hedge active → accelerate then exit

This is **adaptive strategy**, not a rigid plan. Much more valuable than a single decision.

---

## 4. Why This Is Different from Simulation

### Simulation Approach

**What it does**:
1. Specify a probability model for tariff transitions (e.g., Markov chain)
2. Generate many random sample paths (Monte Carlo)
3. For each path, apply a heuristic policy (e.g., "hedge if tariff is on for 2 years")
4. Average the costs across simulations

**Outputs**: Distribution of outcomes, mean cost, percentiles

**Limitations**:
- **Assumes you know the probability model**: What if your $P(\text{tariff} | \text{pre-election})$ is wrong?
- **Evaluates a given policy**: Doesn't tell you if there's a better policy
- **No adversarial robustness**: If Nature can be slightly more adversarial than your model, simulation gives false confidence

### Game-Theoretic Optimization Approach

**What it does**:
1. Specify a **nominal** probability model $p_0$ and uncertainty set (Wasserstein ball)
2. Solve for **optimal policy** $\pi^*$ that minimizes worst-case cost
3. Nature simultaneously chooses worst-case distribution $p^*$ within uncertainty set
4. Equilibrium: $(\pi^*, p^*)$ is a saddle point

**Outputs**: Optimal policy, worst-case cost, sovereignty premium (value of robustness)

**Advantages**:
- **Optimizes the policy**: Tells you what to do, not just evaluates what you proposed
- **Robust to model error**: Protects against distributional shifts within $\varepsilon$-ball
- **Interpretable**: Policy $\pi^*$ is a decision rule you can implement

### When to Use Each

| Approach | Use When | Example |
|----------|---------|---------|
| **Simulation** | Model is trusted, want to understand variability, communicate risk distribution | Climate risk with good historical data, operational planning |
| **Game theory** | Model is uncertain, need optimal strategy, adversarial environment | Political risk, competitive markets, regulatory uncertainty |
| **Hybrid** | Use game theory to find policy, simulation to stress-test it | Optimize with robust game, then Monte Carlo on extreme scenarios |

### Example: Tariff Risk

**Simulation says**: "15% chance of tariff in year 2, here's the distribution of costs"

**Game theory says**: "If tariff happens in year 2, optimal policy is to hedge immediately, then accelerate migration in year 3. Worst-case cost is 47.7 units if Nature adversarially shifts transition probabilities by $\varepsilon=0.3$."

Which is more useful for a CFO facing real political uncertainty? **The policy** - that is, the actionable decision rule ("what to do in each situation") rather than just a probability or cost distribution. Game theory gives you strategic triggers, not just risk assessment.

---

## 5. Generalization to N-Player Games

### Current Model: Two-Player Game

- **Firm** vs. **Nature**
- Zero-sum (almost): Firm minimizes cost, Nature maximizes within constraint
- Sequential: Firm moves first each period, Nature reveals next state

### Extension 1: Multi-Firm Oligopoly

**Setup**: $n$ firms face the same political risk, must decide migration strategies

**Key question**: Do you migrate early (signal concern, possibly trigger regulation) or late (free-ride on others' migration, but face capacity constraints)?

**Game structure**:
- **Players**: Firms $i = 1, \ldots, n$ + Nature
- **Strategies**: Each firm $i$ chooses policy $\pi_i(t, s_i, s_{-i})$ where $s_{-i}$ includes observed actions of other firms
- **Payoff**: Firm $i$'s cost depends on:
  - Own migration progress
  - Aggregate industry migration (affects supplier pricing, political attention)
  - Nature's response (may depend on visible industry exodus)

**Solution concept**: **Markov Perfect Equilibrium (MPE)**
- Each firm's policy is optimal given other firms' policies
- No credible deviations (subgame perfect)
- Nature plays adversarially within constraints

**New phenomena**:
- **First-mover disadvantage**: Early migrators signal weakness, pay premium
- **Herding**: If others migrate, I should too (equilibrium multiplicity)
- **Coordination failure**: All firms wait, collectively worse off

**Computational challenge**: State space now includes $s = (s_1, \ldots, s_n, \tau)$ - explosion with $n$. Need:
- Mean-field approximation (large $n$): Track distribution of firm states
- Approximate MPE: Best response dynamics, policy iteration
- Dimension reduction: Aggregate statistics (e.g., "fraction of industry migrated")

### Extension 2: Government as Strategic Player

**Setup**: Government chooses tariff policy anticipating firm responses

**Game structure**:
- **Player 1 (Government)**: Chooses tariff path $\{\tau_t\}$ to maximize objective (political support, trade balance, domestic employment)
- **Player 2 (Firm)**: Chooses migration policy $\pi$ to minimize cost given tariff path
- **Nature**: Exogenous shocks (election outcomes, international relations)

**Solution concept**: **Stackelberg equilibrium**
- Government commits to tariff policy (leader)
- Firm best-responds with migration policy (follower)
- Nature plays last (or simultaneously)

**Backward induction**:
1. Solve firm's problem for any tariff path: $\pi^*(\tau)$
2. Government chooses optimal $\tau^*$ anticipating $\pi^*(\tau)$
3. Equilibrium: $(\tau^*, \pi^*(\tau^*))$

**Policy implications**:
- **Credibility matters**: If government can't commit (time inconsistency), firm expects ex-post reneging
- **Partial migration as insurance**: Firm maintains flexibility, government loses leverage
- **Negotiation**: Tariff policy may be outcome of Nash bargaining

### Extension 3: Geopolitical Supra-Game (The Forgotten Context)

**Real scenario of the model**: A European firm suffers tariffs that the EU inflicts on a US tech supplier, in **retaliation** for US tariffs imposed on European firms. The current model treats these tariffs as exogenous (Nature), but they are actually the outcome of a **strategic game between economic powers**.

**Meta-game structure**:
- **Upper level**: EU vs. US (strategic tariff game)
  - **Player A (US)**: Imposes tariffs $\tau_{US}$ to protect domestic industries
  - **Player B (EU)**: Responds with retaliatory tariffs $\tau_{EU}$ to create political pressure
  - **Objective**: Each maximizes national welfare anticipating the other's response
  
- **Lower level**: Firm (our model)
  - Suffers $\tau_{EU}$ as environment
  - Chooses migration policy $\pi$
  - Faces adversarial Nature (uncertainty about retaliation duration/intensity)

**Nested dynamics**:

1. **EU-US tariff game** (Macro level):
   - US imposes tariff → EU calculates optimal retaliation
   - EU anticipates that: tariff too high → European firms migrate → loses credible retaliation capacity
   - Equilibrium: Retaliatory tariffs high enough for political pressure, but not so high they destroy their own industry

2. **European firm** (Micro level - our model):
   - Observes $\tau_{EU}$ imposed on US supplier
   - Decides migration policy under uncertainty: "Will the tariff persist?"
   - This uncertainty reflects uncertainty about the **EU-US game**: negotiation, escalation, resolution?

**Why this layer matters**:

- **Tariff endogeneity**: $\tau_{EU}$ is not purely exogenous - it depends on US response, itself a function of damage to US industries
- **Migration signaling**: Massive European firm migration can signal to EU government that retaliation is unsustainable
- **Political leverage**: EU government can use threat of "letting firms migrate" as negotiation tool with US

**Implications for the model**:

If we modeled the complete game (3 players: US, EU, Firm), we would get:
- **3-player Nash equilibrium** where no party can improve unilaterally
- **Retaliation credibility**: EU only maintains tariff if firm migration remains partial
- **Bargaining range**: Zone where both governments prefer negotiation to escalation

**In practice**: Our 2-player model (Firm vs. Nature) is a **reduced form** of the complete game. The ambiguity $\varepsilon(t)$ on tariff transitions **implicitly captures** uncertainty about the underlying geopolitical game.

For a production model, one could:
- Link $\varepsilon(t)$ to **trade tension indicators** (twitter diplomacy, WTO statements, negotiation cycles)
- Explicitly model $P(\text{resolution})$ as function of aggregate industry migration
- Add "political lobbying" action where firm influences EU government position

### Extension 4: Supply Chain Network

**Setup**: Multi-tier supply chain with dependencies at each level

**Graph structure**:
- **Nodes**: Firms at different tiers (Tier 0 = final assembler, Tier 1 = direct suppliers, Tier 2 = component makers)
- **Edges**: Supply relationships with risk (tariff exposure, single-source dependencies)
- **Nature**: Shocks propagate through network

**Game dynamics**:
- **Simultaneous moves**: All firms choose migration strategies
- **Network externalities**: Your supplier's migration affects your costs
- **Cascade risk**: Tier 1 failure forces Tier 0 emergency migration

**Solution approach**:
- **Network game equilibrium**: Firm $i$'s payoff depends on neighbors' actions
- **Potential games**: If game has potential function, pure strategy Nash exists
- **Contagion analysis**: Stress-test network resilience under adversarial Nature

### Computational Strategies for N-Player Games

1. **Decomposition**: Separate into subgames (by geography, time horizon)
2. **Mean-field approximation**: Replace firm interactions with aggregate statistics
3. **Sampling**: Monte Carlo Tree Search, opponent modeling
4. **Learning**: Multi-agent reinforcement learning (if equilibrium is unknown)

**Practical recommendation**: Start with 2-3 player version to understand mechanisms, then scale with approximations.

---

## 6. Steps to Connect This to Real-World Business

### Step 1: Stakeholder Alignment

**Goal**: Ensure leadership understands the framework and buys into the approach

**Actions**:
1. **Executive briefing**: Present toy model results as "proof of concept"
   - Emphasize policy output (decision rules) not just cost numbers
   - Show sovereignty premium as quantified ambiguity cost
   - Demonstrate sensitivity: how results change with assumptions

2. **Define success criteria**: What decisions will this inform?
   - Supplier diversification budget allocation
   - Trigger points for accelerating migration
   - Hedge contract terms (duration, break clauses)

3. **Identify skeptics and address concerns**:
   - "Why not just use our existing risk model?" → Show game theory handles adversarial Nature
   - "Isn't this too complex?" → Demonstrate that policy is interpretable
   - "Can we trust it?" → Stress-test with historical scenarios

### Step 2: Data Collection and Calibration

**Tariff transition probabilities** $(p_{01}, p_{10})$:
- **Historical data**: Tariff events in relevant sectors over 20 years
- **Expert elicitation**: Survey trade policy analysts, government relations team
- **Leading indicators**: Election cycles, trade balance, geopolitical tensions
- **Bayesian update**: Start with priors, update as regime unfolds

**Cost parameters**:
- **CAPEX (investment, exit costs)**: Engineering estimates, vendor quotes
  - Investment program setup: IT systems, dual-source contracts
  - Termination fees: Contract break clauses, unwinding costs
  - Cutover costs: Logistics, retraining, recertification
- **OPEX (recurring costs)**: Accounting data, projected premium for alternative suppliers
  - Migration period: Dual-run costs, project management, travel
  - Tariff costs: Customs data, policy team estimates
  - Hedged tariff costs: Contract terms (forward purchasing, local content agreements)

**Discount rate (WACC)**: Finance team provides, typically 8-12% for corporate

**Risk aversion ($\alpha$ for CVaR)**: 
- Board/CFO risk appetite survey: "What probability of bad outcome is acceptable?"
- Typical: $\alpha = 0.90$ (protect worst 10%) to $\alpha = 0.95$ (worst 5%)

**Ambiguity radius** $\varepsilon(t)$:
- Link to **Economic Policy Uncertainty (EPU) index** (Baker et al. 2016)
- Map EPU to $\varepsilon \in [0.02, 0.40]$ based on historical forecast error
- Time-varying: Higher $\varepsilon$ around elections, trade negotiations

### Step 3: Model Refinement

**Enrich state space**:
- **Multi-level tariffs**: Not binary, but low/medium/high ($\tau \in \{0, 0.15, 0.25, 0.40\}$)
- **Partial migration**: Migration progress as continuous (% of volume shifted)
- **Supplier capacity**: Limited alternative supplier capacity (scarcity premium)
- **Regional disaggregation**: Europe vs. Asia sourcing as separate migration tracks

**Add realistic actions**:
- **Hybrid sourcing**: Split volume between sources with different risk/cost
- **Contract renegotiation**: Pay premium to add flexibility clauses
- **Political lobbying**: Costly action to influence $p_{10}$ (tariff removal probability)
- **Build own capacity**: CAPEX-heavy option to eliminate supplier dependency entirely

**Multi-period commitment**:
- **Investment irreversibility**: Once migration starts, partial sunk costs
- **Hedge lock-in**: Multi-year hedge contracts limit future flexibility
- **Learning by doing**: Migration gets cheaper/faster as organization gains experience

### Step 4: Validation and Backtesting

**Historical counterfactuals**:
- Apply model to past episodes (2018 trade war, EU regulations)
- Compare recommended policy to actual firm decisions
- Quantify "regret": How much better would game-theoretic policy have performed?

**Stress testing**:
- **Scenario analysis**: "What if tariff=1 persisted for entire horizon?"
- **Adversarial shocks**: Worst-case Nature within $\varepsilon$-ball - does policy survive?
- **Parameter sensitivity**: If CAPEX is 50% higher, does optimal action change?

**External validation**:
- Compare to industry peers: Are our migration costs reasonable?
- Benchmark ambiguity radius: EPU-implied $\varepsilon$ vs. our calibration
- Consult experts: Do policy triggers (e.g., "hedge if tariff persists 2 years") make business sense?

### Step 5: Integration into Decision Processes

**Quarterly updates**:
- Re-solve model with updated state $(t, \tau, m, i, h, e)$ and latest $\varepsilon(t)$ from EPU
- Check if optimal action changed ("hedge" → "accelerate" means threshold crossed)
- Report sovereignty premium trend to CFO

**Trigger monitoring**:
- Implement dashboard tracking policy-relevant indicators:
  - Current tariff regime: Off/On
  - Migration progress: X% complete
  - EPU index: Above/below threshold
- Automated alerts: "Optimal policy changed - review recommended"

**Budgeting and planning**:
- Embed sovereignty premium in budget stress scenarios
- Allocate migration budget based on model recommendations
- Set aside contingency funds for acceleration if triggers hit

### Step 6: Continuous Improvement

**Learning loop**:
1. **Observe outcomes**: Did tariff evolve as expected? Was migration cost accurate?
2. **Update beliefs**: Bayesian update on $(p_{01}, p_{10})$, recalibrate cost functions
3. **Re-optimize**: Solve updated model, compare to previous policy
4. **Iterate**: Feed learnings back to Step 2 (data collection)

**Model extensions as needed**:
- Add new states (regulatory compliance stages, technology lock-in)
- Refine action space (granular migration speeds)
- Multi-player version if competitors' actions become strategic

**Governance**:
- **Model owner**: Assign dedicated team (strategy/FP&A/risk)
- **Review cadence**: Quarterly for parameters, annual for structure
- **Audit trail**: Document assumptions, log policy decisions for future review

---

## Summary: The Game-Theoretic Advantage

**Traditional approach**: "What's the NPV of sovereignty?"
- Single cost number
- Assumes known probabilities
- No decision rule, just a static trade-off

**Game-theoretic approach**: "What's the optimal migration policy under adversarial political risk?"
- State-contingent strategy (if-then rules)
- Robust to distributional shifts (Wasserstein ambiguity)
- Quantifies value of flexibility (sovereignty premium)

**Key takeaway**: Game theory transforms sovereignty from a **cost problem** into a **strategic problem**. You get:
1. **Optimal policy** $\pi^*(t, s)$ - what to do in each situation
2. **Worst-case cost** $V_0$ - budget the downside
3. **Sovereignty premium** - price tag on political uncertainty
4. **Robustness** - protection against forecast errors within $\varepsilon$-ball

This is **actionable strategy**, not just risk assessment.

---

## Further Reading

**Game Theory Foundations**:
- von Neumann, J., & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton.
- Nash, J. (1950). "Equilibrium points in n-person games." *PNAS*, 36(1), 48-49.
- Fudenberg, D., & Tirole, J. (1991). *Game Theory*. MIT Press.

**Dynamic Programming and Stochastic Games**:
- Puterman, M. L. (2014). *Markov Decision Processes*. Wiley.
- Shapley, L. S. (1953). "Stochastic games." *PNAS*, 39(10), 1095-1100.

**Robust Optimization**:
- Ben-Tal, A., El Ghaoui, L., & Nemirovski, A. (2009). *Robust Optimization*. Princeton.
- Kuhn, D., et al. (2019). "Wasserstein distributionally robust optimization." *Operations Research*, 67(6), 1373-1416.

**Applications to Political/Regulatory Risk**:
- Baker, S. R., Bloom, N., & Davis, S. J. (2016). "Measuring economic policy uncertainty." *QJE*, 131(4), 1593-1636.
- Handley, K., & Limão, N. (2015). "Trade and investment under policy uncertainty." *AEJ: Economic Policy*, 7(4), 189-222.

---

**Tutorial Author**: Jean-Baptiste Dézard, Deal ex Machina SAS  
**License**: CC BY 4.0  
**Last Updated**: 2026

For questions or feedback on this tutorial, please open an issue on the GitHub repository.
