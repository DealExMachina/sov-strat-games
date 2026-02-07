# Step 4 -- Risk and Ambiguity: CVaR, Wasserstein, and DRO

## Learning Objectives

By the end of this step, you will:

- Understand the difference between expected value, VaR, and CVaR
- Know why CVaR is a "coherent" risk measure and why that matters
- Have an intuitive grasp of Wasserstein distance as optimal transport
- Understand what a Wasserstein ball is and how it defines an ambiguity set
- Know the role of the transport cost matrix $C$
- Understand Distributionally Robust Optimization (DRO) at a conceptual level
- See how time-varying $\varepsilon(t)$ connects the model to real-world indicators

---

## Level 0: Expected Value (Risk-Neutral)

The simplest approach to uncertainty is to take the **expected value** (average):

$$\mathbb{E}[L] = \sum_i p_i \cdot L_i$$

**Example:** You face two scenarios for your annual tariff cost:
- 70% chance: no tariff, cost = 0
- 30% chance: tariff hits, cost = 10

Expected cost: $0.70 \times 0 + 0.30 \times 10 = 3.0$

**The problem:** Expected value treats all outcomes equally. A CFO who faces a 30% chance of losing 10 units is not the same as a CFO who always loses 3 units. The **variability** and the **worst case** matter, especially for large firms where a single bad year can trigger covenant breaches, credit downgrades, or management crises.

---

## Level 1: VaR and CVaR

### Value-at-Risk (VaR)

**VaR at level $\alpha$** answers: "What is the loss that we will *not* exceed with probability $\alpha$?"

$$\text{VaR}_\alpha(L) = \inf\{x : P(L \leq x) \geq \alpha\}$$

**Example with a 6-sided die:**

You roll a die. The loss associated with each face is:

| Roll | 1 | 2 | 3 | 4 | 5 | 6 |
|------|---|---|---|---|---|---|
| Loss | 1 | 2 | 3 | 4 | 8 | 15 |

Each roll has probability 1/6. The cumulative probabilities are:

| Loss $\leq x$ | 1 | 2 | 3 | 4 | 8 | 15 |
|---|---|---|---|---|---|---|
| $P(L \leq x)$ | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 |

$\text{VaR}_{0.90}$ is the smallest $x$ such that $P(L \leq x) \geq 0.90$. Since $P(L \leq 8) = 5/6 \approx 0.833 < 0.90$ and $P(L \leq 15) = 1.0 \geq 0.90$, we get:

$$\text{VaR}_{0.90} = 15$$

**Problem with VaR:** It tells you the threshold, but says nothing about how bad things get *beyond* that threshold. Two portfolios can have the same VaR but very different tail losses.

### Conditional Value-at-Risk (CVaR)

**CVaR at level $\alpha$** (also called Expected Shortfall) answers: "Given that we are in the worst $(1-\alpha)$ fraction of scenarios, what is the average loss?"

$$\text{CVaR}_\alpha(L) = \frac{1}{1-\alpha} \int_\alpha^1 \text{VaR}_u(L) \, du$$

For discrete distributions, this simplifies to: **the average of the worst $(1-\alpha)$ fraction of outcomes.**

**Continuing the die example:**

At $\alpha = 0.90$, we look at the worst 10% of outcomes. With 6 equally likely outcomes, the worst 10% corresponds to the worst $6 \times 0.10 = 0.6$ outcomes. Since we cannot take 0.6 of an outcome, the worst 10% is effectively the single worst outcome (with appropriate weighting).

A cleaner calculation: sort the losses in decreasing order: 15, 8, 4, 3, 2, 1. The worst $1 - 0.90 = 10\%$ tail. Since each outcome has probability 1/6, the worst outcome (loss = 15) alone covers probability 1/6 = 16.7% > 10%.

$$\text{CVaR}_{0.90} = \frac{1}{1 - 0.90} \left(\frac{0.10}{1/6} \times 15 \times \frac{1}{6}\right)$$

More intuitively: for $\alpha = 2/3$ (worst 1/3), CVaR is the average of the two worst outcomes:

$$\text{CVaR}_{2/3} = \frac{8 + 15}{2} = 11.5$$

Compare to the expected value: $(1+2+3+4+8+15)/6 = 5.5$. CVaR at 2/3 is **more than double** the expected value, because it focuses on the tail.

### Why CVaR Is Better Than VaR

CVaR is a **coherent risk measure**, satisfying four mathematical properties:

1. **Monotonicity:** If portfolio A always loses more than B, then $\text{CVaR}(A) \geq \text{CVaR}(B)$
2. **Translation invariance:** Adding a constant to all losses shifts CVaR by the same amount
3. **Positive homogeneity:** Scaling losses scales CVaR proportionally
4. **Subadditivity:** $\text{CVaR}(A + B) \leq \text{CVaR}(A) + \text{CVaR}(B)$

The last property (**subadditivity**) is the critical one. It means that **diversification never increases risk** under CVaR. VaR fails this property -- you can construct examples where combining two portfolios *increases* VaR, which is nonsensical from a risk management perspective.

**In our model**, CVaR at $\alpha = 0.90$ means: "The average cost in the worst 10% of scenarios." This is what the firm should budget for if it wants to protect against tail events, not just average outcomes.

---

## Level 2: Ambiguity and Wasserstein Distance

### The Problem of Model Uncertainty

CVaR protects against bad outcomes *within a known distribution*. But what if the distribution itself is wrong?

Consider: you estimated $P(\text{tariff}) = 0.15$ based on expert opinion. But what if the true probability is 0.30? Or 0.05? Your CVaR calculation would be off, and your policy might be suboptimal.

This is **ambiguity** (also called Knightian uncertainty, after Frank Knight who distinguished it from risk in 1921): uncertainty about the probability model itself.

### Wasserstein Distance: Intuition

The **Wasserstein distance** measures how "far apart" two probability distributions are. It comes from **optimal transport theory** -- originally developed by Gaspard Monge in 1781 for moving piles of dirt efficiently.

**The dirt-moving analogy:**

Imagine you have a pile of sand distributed across a field (your nominal distribution $p_0$), and you want to reshape it into a different configuration (an alternative distribution $p$). Moving sand costs money: moving 1 kg of sand by 1 meter costs 1 unit.

The **Wasserstein distance** $W_C(p, p_0)$ is the **minimum total transport cost** to reshape $p_0$ into $p$.

$$W_C(p, q) = \min_{\pi \in \Pi(p,q)} \sum_{i,j} \pi_{ij} \cdot C_{ij}$$

Where:
- $\pi_{ij}$ is the amount of probability mass moved from state $i$ to state $j$
- $C_{ij}$ is the **transport cost** for moving mass from $i$ to $j$
- $\Pi(p,q)$ is the set of valid transport plans (total mass out of $i$ equals $p_i$, total mass into $j$ equals $q_j$)

### A Concrete Example

Suppose you have 3 states with nominal distribution $p_0 = (0.5, 0.3, 0.2)$.

State 1 is "good" (low cost), State 2 is "medium," State 3 is "bad" (high cost).

Transport costs:

| From \ To | State 1 | State 2 | State 3 |
|-----------|:-------:|:-------:|:-------:|
| State 1 | 0 | 1 | 3 |
| State 2 | 1 | 0 | 1 |
| State 3 | 3 | 1 | 0 |

Moving probability from good to bad states is expensive (cost = 3). Moving between adjacent states is cheaper (cost = 1).

If Nature wants to make the distribution worse (more weight on State 3), it would prefer to move mass from State 2 to State 3 (cost = 1 per unit) rather than from State 1 to State 3 (cost = 3 per unit).

With a Wasserstein budget of $\varepsilon = 0.1$, Nature could move 0.1 units of mass from State 2 to State 3, creating $p = (0.5, 0.2, 0.3)$ at a transport cost of $0.1 \times 1 = 0.1 \leq \varepsilon$.

### The Wasserstein Ball

The **Wasserstein ball** of radius $\varepsilon$ around $p_0$ is:

$$\mathcal{P}_\varepsilon(p_0) = \{p \in \mathcal{P}(\mathcal{S}) : W_C(p, p_0) \leq \varepsilon\}$$

This is the set of all distributions that are "close enough" to $p_0$ according to the Wasserstein distance. It represents the range of plausible distributions given your uncertainty about the true model.

**Key insight:** The Wasserstein ball is not just any set of distributions. It has *structure* determined by the transport cost $C$:

- If moving probability across tariff regimes is cheap (low $C$), Nature has more freedom to shift tariff probabilities
- If moving probability across migration states is expensive (high $C$), Nature cannot easily change how migration evolves (because that is under the firm's control)

This asymmetry is realistic: political risk is uncertain (easy for Nature to distort), but your own migration progress is well-known (hard for Nature to distort).

---

## The Transport Cost Matrix in Our Model

In the sovereignty model, the transport cost matrix $C$ is designed to reflect which state transitions are uncertain:

**Cheap transport (low cost):**
- Moving probability across **tariff regimes** (tariff on vs. off): political uncertainty is high, so Nature can easily shift this
- Cost: typically small values (1-2 units)

**Expensive transport (high cost):**
- Moving probability across **migration progress** states: the firm controls its own migration, so this should not be uncertain
- Moving probability across **flag** states (investment started, hedge active): these are binary decisions under the firm's control
- Cost: typically large values (5-10 units)

This design ensures that when Nature "pushes" the distribution adversarially, it pushes on the dimensions that are genuinely uncertain (political risk), not on dimensions the firm controls (its own decisions).

---

## Distributionally Robust Optimization (DRO)

Putting it all together, **DRO** solves:

$$\min_{a} \sup_{p \in \mathcal{P}_\varepsilon(p_0)} \text{CVaR}_\alpha^p\left[ \text{cost}(a, p) \right]$$

In words: **Choose the action that minimizes the worst-case CVaR, where "worst case" is over all distributions in the Wasserstein ball.**

The key insight: we do not need to know the exact distribution. We only need a **nominal estimate** $p_0$ and a **radius** $\varepsilon$ that captures how uncertain we are about that estimate. The optimization automatically finds the worst plausible distribution and protects against it.

### How DRO Is Solved Computationally

The inner problem (finding the worst distribution in the Wasserstein ball) can be reformulated as a **linear program** via LP duality:

$$\sup_{p : W_C(p, p_0) \leq \varepsilon} \text{CVaR}_\alpha^p(L) = \min_{\eta, \lambda \geq 0, u} \left\{ \eta + \lambda\varepsilon + p_0^\top u \right\}$$

Subject to constraints involving $\eta$, $\lambda$, $u$, the transport cost $C$, and the loss vector $L$.

This LP is solved using convex optimization software (CVXPY with CLARABEL or SCS solvers in our notebook). Each solve takes about 10-50 milliseconds, making the overall DP tractable.

You do not need to understand the LP duality in detail at this stage. The key takeaway: **the robust CVaR under Wasserstein ambiguity can be computed exactly and efficiently.**

---

## Time-Varying Ambiguity: $\varepsilon(t)$

A distinctive feature of this model is that the ambiguity radius changes over time:

$$\varepsilon(t) = \varepsilon_{\min} + (\varepsilon_{\max} - \varepsilon_{\min}) \cdot R(t)$$

Where $R(t) \in [0, 1]$ is a political risk indicator.

**Why time-varying?**

- **Election years** have higher political uncertainty ($R(t)$ increases, so $\varepsilon(t)$ increases)
- **Post-election periods** may have lower uncertainty as policies become clearer
- **Trade negotiation windows** increase uncertainty about tariff regimes
- **Crisis periods** (pandemics, wars) spike uncertainty across the board

**Calibration options:**

- **Economic Policy Uncertainty (EPU) index** (Baker, Bloom, Davis 2016): a well-known index tracking policy-related uncertainty in newspapers, tax code provisions, and forecast disagreement
- **VIX** (CBOE Volatility Index): implied volatility from options markets
- **Election cycle dummies:** binary indicators for election years
- **Trade negotiation calendars:** planned summits, WTO hearings

The formula maps observable indicators to model parameters, making the ambiguity radius data-driven rather than arbitrary.

**Default schedule in the notebook:** The model implements several schedules for $\varepsilon(t)$:
- Constant: $\varepsilon(t) = \varepsilon_0$ for all $t$
- Linear decay: ambiguity decreases over time (you learn about the political situation)
- Hump-shaped: ambiguity peaks at mid-horizon (election cycle)
- Custom: user-defined schedule

---

## Putting the Three Layers Together

Here is how the three layers of the model interact:

| Layer | What It Handles | Mathematical Tool | Parameter |
|-------|----------------|-------------------|-----------|
| **Expected value** | Average outcome under nominal model | $\mathbb{E}_{p_0}[\cdot]$ | -- |
| **CVaR** | Worst $(1-\alpha)$ fraction of outcomes under nominal model | $\text{CVaR}_\alpha^{p_0}[\cdot]$ | $\alpha$ (default: 0.90) |
| **Wasserstein DRO** | Worst distribution in uncertainty ball, then CVaR | $\sup_{p \in \mathcal{P}_\varepsilon} \text{CVaR}_\alpha^p[\cdot]$ | $\varepsilon(t)$ |

The model can be run at each layer independently:

- **Level 0 (EV):** $\varepsilon = 0$, $\alpha = 0$ (or use expectation instead of CVaR) -- optimistic, trusts the model
- **Level 1 (CVaR):** $\varepsilon = 0$, $\alpha = 0.90$ -- pessimistic about outcomes, trusts the model
- **Level 2 (Robust CVaR):** $\varepsilon > 0$, $\alpha = 0.90$ -- pessimistic about outcomes AND about the model

Comparing the value functions across levels reveals the **cost of risk aversion** (Level 1 vs. Level 0) and the **cost of ambiguity** (Level 2 vs. Level 1). The sovereignty premium is specifically the cost of ambiguity.

---

## Connection to the Repository

- The **CVaR computation** is implemented in `cvar_discrete_worst_tail()` in the notebook
- The **Wasserstein DRO inner problem** is solved by the `RobustCVaRWasserstein` class using CVXPY
- The **transport cost matrix** is defined in the `TransportCost` class and constructed by `transport_cost_matrix()`
- The **time-varying $\varepsilon(t)$** schedules are implemented as `eps_schedule_*()` functions
- The **three-level comparison** (EV vs. CVaR vs. Robust CVaR) is the main output of the notebook
- The **EPU index** connection is discussed in `docs/bellman_wasserstein_mean_field_framework.md`, Section 6

---

## Validation Quiz

### Questions

**Q1.** A random variable $L$ has the following distribution:

| Outcome | Probability |
|:-------:|:-----------:|
| 2 | 0.40 |
| 5 | 0.30 |
| 12 | 0.20 |
| 25 | 0.10 |

Compute:
- (a) The expected value $\mathbb{E}[L]$
- (b) $\text{CVaR}_{0.70}(L)$ (the average of the worst 30% of outcomes)

**Q2.** Explain the "dirt-moving" analogy for Wasserstein distance in 2-3 sentences.

**Q3.** In our model, moving probability across tariff regimes has low transport cost, while moving probability across migration progress states has high transport cost. Why does this make sense?

**Q4.** What happens to the model when $\varepsilon = 0$? What about when $\varepsilon$ is very large?

**Q5.** The sovereignty premium is defined as the difference in value between the robust model ($\varepsilon > 0$) and the baseline ($\varepsilon = 0$). If the baseline worst-case cost is -42 units and the robust worst-case cost is -47 units, what is the sovereignty premium? What does it represent?

**Q6.** Why is CVaR considered a better risk measure than VaR for risk management? Name the specific mathematical property that VaR lacks.

**Q7.** If the Economic Policy Uncertainty index doubles during an election year, what happens to $\varepsilon(t)$ in the model? What is the practical consequence for the firm's optimal policy?

**Q8.** True or False: Wasserstein DRO assumes the worst possible distribution in the entire probability space, with no constraints.

---

### Answers

**A1.**

(a) Expected value:
$$\mathbb{E}[L] = 0.40 \times 2 + 0.30 \times 5 + 0.20 \times 12 + 0.10 \times 25 = 0.8 + 1.5 + 2.4 + 2.5 = 7.2$$

(b) CVaR at $\alpha = 0.70$ (worst 30%):

The worst 30% of outcomes includes:
- Outcome 25 (probability 0.10)
- Outcome 12 (probability 0.20)

Total probability in the tail: 0.10 + 0.20 = 0.30 (exactly 30%).

$$\text{CVaR}_{0.70} = \frac{1}{0.30}(0.10 \times 25 + 0.20 \times 12) = \frac{1}{0.30}(2.5 + 2.4) = \frac{4.9}{0.30} \approx 16.33$$

The average loss in the worst 30% of scenarios is about 16.33, compared to the overall expected loss of 7.2. The tail is more than twice as costly as the average.

**A2.** Imagine two piles of sand on a landscape, each representing a probability distribution. The Wasserstein distance is the minimum total cost of shoveling sand from one pile's shape to the other's shape, where the cost depends on how far you move each grain. Nearby distributions require little shoveling (low Wasserstein distance), while very different distributions require moving a lot of sand over long distances (high Wasserstein distance). In our model, "sand" is probability mass and "distance" is determined by the transport cost matrix $C$.

**A3.** The transport cost reflects **who controls what**:
- **Tariff regimes** are controlled by governments and are inherently uncertain for the firm. The firm cannot predict or control political decisions, so it makes sense that Nature can easily shift probability across tariff states (low transport cost). This gives Nature room to be adversarial where uncertainty is genuine.
- **Migration progress** is controlled by the firm itself. The firm knows how far along its migration is -- this is not uncertain. Making this transport cost high prevents Nature from "cheating" by claiming the firm might magically jump forward or backward in migration, which would be unrealistic.

**A4.**
- **$\varepsilon = 0$:** The Wasserstein ball collapses to a single point -- the nominal distribution $p_0$. Nature has no freedom to deviate. The model reduces to standard DP with CVaR (Level 1). You are trusting your forecast completely.
- **Very large $\varepsilon$:** The Wasserstein ball becomes very large, allowing Nature to choose almost any distribution. The model approaches a pure worst-case (maximin) solution that is typically too conservative. Every action looks equally bad because Nature can always find a catastrophic scenario. Practical models use moderate $\varepsilon$ values calibrated to real-world forecast error.

**A5.** The sovereignty premium is $-47 - (-42) = -5$ units. Since costs are negative (losses), the robust scenario is 5 units worse. This premium represents the **cost of ambiguity** -- how much additional worst-case loss the firm faces because its political risk forecast might be wrong. The CFO can interpret this as: "We need to budget 5 additional units of contingency to cover the possibility that our tariff probability estimates are off."

**A6.** CVaR is preferred because it satisfies **subadditivity**: $\text{CVaR}(A + B) \leq \text{CVaR}(A) + \text{CVaR}(B)$. This means diversification (combining risks) never increases the risk measure, which aligns with financial intuition. VaR violates subadditivity -- there exist cases where combining two portfolios produces a higher VaR than the sum of individual VaRs, which would absurdly penalize diversification. CVaR is a "coherent" risk measure (satisfying monotonicity, translation invariance, positive homogeneity, and subadditivity); VaR is not.

**A7.** If the EPU index doubles, $R(t)$ increases (it is proportional to EPU), which increases $\varepsilon(t)$ via the formula $\varepsilon(t) = \varepsilon_{\min} + (\varepsilon_{\max} - \varepsilon_{\min}) \cdot R(t)$. A larger $\varepsilon(t)$ means Nature has more freedom to shift distributions adversarially. Practically, this makes the worst-case cost higher and may push the optimal policy toward more **protective actions** (hedging, investing in migration) earlier. The model becomes more conservative during high-uncertainty periods, which is the intended behavior -- you should act earlier when political risk is elevated.

**A8.** **False.** Wasserstein DRO does not assume the worst distribution in the *entire* probability space. It assumes the worst distribution **within the Wasserstein ball** of radius $\varepsilon$ around the nominal distribution $p_0$. The constraint $W_C(p, p_0) \leq \varepsilon$ limits how far Nature can deviate from the nominal model. This is what makes Wasserstein DRO practical: it is robust to forecast errors of magnitude $\varepsilon$, not to arbitrary distributions.

---

**Previous step:** [03 -- Dynamic Programming](03_dynamic_programming.md)
**Next step:** [05 -- The Model](05_the_model.md)
