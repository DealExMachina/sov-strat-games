# Step 1 -- Why Sovereignty Matters

## Learning Objectives

By the end of this step, you will:

- Understand the real-world business problem this model addresses
- Know why traditional NPV analysis is insufficient for sovereignty decisions
- Distinguish the three layers of uncertainty (risk, strategic risk, ambiguity)
- Understand the difference between a "decision" and a "policy"
- Know what the "sovereignty premium" means and why CFOs care about it

---

## The Real-World Problem

Imagine you are the CFO of a large European industrial company. Your firm depends heavily on a US technology supplier -- say a cloud infrastructure provider like AWS, Azure, or GCP. This supplier is critical: your operations, data, and digital infrastructure run on their platform.

Everything works fine until geopolitical tensions escalate. The European Union, in retaliation for US tariffs on European goods, imposes tariffs on US technology services. Your US supplier mechanically passes this cost through to you. Overnight, your cloud bill increases by 25-40%.

**You now face a strategic decision:**

- Do you **wait** and hope the tariff is temporary?
- Do you **invest** in migrating to a European cloud provider (expensive, multi-year project)?
- Do you **hedge** by setting up a dual-source architecture?
- Do you **accelerate** migration if the situation worsens?
- Do you **exit** the US supplier entirely once ready?

This is not a hypothetical. Trade wars, technology export controls, data sovereignty regulations, and sanctions have made supplier dependency a board-level concern for firms worldwide. The 2018-2020 US-China trade war, EU digital sovereignty initiatives, and semiconductor export controls are all real instances of this dynamic.

---

## A Concrete Scenario

Let us make it specific. Here are the parameters from the model (in abstract cost units):

| Cost Component | Value | What It Represents |
|---------------|-------|---------------------|
| Annual tariff exposure | 10.0 | Extra cost per year when tariff is active, unhedged |
| Hedged tariff cost | 6.0 | Reduced exposure with hedge in place |
| Post-exit cost | 1.0 | Residual cost after full migration |
| Migration CAPEX | 8.0 | One-time investment to start migration |
| Hedge setup | 2.0 | One-time cost to set up hedge |
| Total exit cost | 19.0 | Termination fee + cutover + recertification |
| Migration timeline | 3 years | Time from investment start to exit readiness |

To make this concrete: if your annual cloud spend is EUR 15M and tariffs add 40%, the "tariff cost" of 10.0 abstract units might represent EUR 6M/year in real terms. The migration CAPEX of 8.0 might be EUR 8M in engineering and transition costs. The numbers are intentionally abstract so the framework generalizes.

**The key question is not just "how much does sovereignty cost?" but "what should I do, and when, depending on how the world evolves?"**

---

## Why Traditional NPV Analysis Fails

A traditional approach would be:

1. Estimate the probability of a tariff (say, 15%)
2. Compute expected tariff costs over the horizon
3. Compare to migration costs
4. If expected tariff cost > migration cost, migrate. Otherwise, don't.

This produces a single number and a single decision. It fails for three fundamental reasons:

### Problem 1: Static Analysis in a Dynamic World

NPV gives you a **one-time decision** ("migrate" or "don't migrate"). But the real world is sequential. You can:

- Start with waiting, then switch to hedging if tariffs appear
- Begin migration, then accelerate if the political situation worsens
- Hedge first, then invest in full migration later

A static NPV misses the **option value** of waiting and adapting. Real options theory partially addresses this, but standard real options still assume you know the probability distribution.

### Problem 2: Trusting a Single Probability

Where does your "15% tariff probability" come from? Political risk is notoriously hard to forecast. Experts disagree. Elections happen. Leaders make unexpected decisions.

The real question is not "what is the probability?" but "what if my probability estimate is wrong?" If you assume 15% but the true probability is 30%, your NPV-based decision could be catastrophically wrong.

### Problem 3: No Adversarial Thinking

Traditional analysis treats political risk as random weather -- it happens or it doesn't, with no strategic dimension. But political actors **respond** to firm behavior:

- If many firms start migrating, the government may notice and adjust tariff policy
- If you signal dependence, the supplier may raise prices
- If you build alternatives, your negotiating position improves

These feedback loops require **game-theoretic** reasoning, not statistical averaging.

---

## The Three Layers of Uncertainty

This model distinguishes three progressively deeper layers of uncertainty. Understanding them is essential:

### Level 0: Risk (Known Distribution)

You know the probability distribution exactly. A fair coin has P(heads) = 0.5. Historical data gives you reliable frequencies.

**Tool:** Expected value, variance, standard risk measures.

**Example:** Machine failure rates based on 20 years of maintenance data.

### Level 1: Strategic Risk (Unknown but Rational Opponent)

You don't know what the other player will do, but you know they are rational (self-interested). A competitor might undercut your price, but not at a loss to themselves.

**Tool:** Nash equilibrium, minimax strategies.

**Example:** Competitor pricing in an oligopoly.

### Level 2: Ambiguity (Unknown Distribution)

You don't even know the probability distribution. Your best estimate could be wrong. The forecast itself is uncertain.

**Tool:** Robust optimization, Wasserstein DRO, maxmin expected utility.

**Example:** Political risk in a new regulatory regime, unprecedented trade war dynamics.

**This model addresses all three layers simultaneously:**

- **CVaR** handles Level 0 (focusing on the tail of the distribution -- the worst outcomes)
- **Game framing** handles Level 1 (Nature as adversarial player)
- **Wasserstein DRO** handles Level 2 (allowing the distribution to shift within a ball of uncertainty)

---

## Policy vs. Decision

This distinction is crucial and often misunderstood.

### A Decision

A decision is a single choice: "Invest now" or "Wait." It is what traditional analysis produces.

The problem: a decision made today might be wrong tomorrow if circumstances change. "Wait" might be right today but terrible if a tariff hits next year and you have no plan.

### A Policy

A policy is a **complete contingency plan**: "If the world is in state X at time t, take action Y."

For example, the model might produce:

| Current Tariff | Migration Progress | Hedge Active | Recommended Action |
|:-:|:-:|:-:|:--|
| Off | 0 years | No | Wait |
| On | 0 years | No | Hedge |
| On | 1 year | Yes | Accelerate migration |
| On | 3 years | Yes | Exercise exit |
| Off | 2 years | Yes | Continue investment |

This is **adaptive strategy**. You don't commit to one path. You have a decision rule for every possible situation. Much more valuable than a single number.

**Analogy:** A GPS doesn't give you one instruction ("drive north"). It gives you a **policy**: "If you are at intersection A, turn left. If you are at intersection B, go straight. If you miss the turn, recalculate." That is what this model produces for sovereignty decisions.

---

## The Sovereignty Premium

The **sovereignty premium** is one of the key outputs of the model. It answers the question: **"How much does uncertainty about political risk cost us?"**

Formally:

$$\text{Sovereignty Premium} = V_0(\varepsilon(t)) - V_0(\varepsilon = 0)$$

Where:

- $V_0(\varepsilon = 0)$ is the worst-case cost assuming you trust your forecast perfectly (no ambiguity)
- $V_0(\varepsilon(t))$ is the worst-case cost when you account for forecast errors (ambiguity radius $\varepsilon(t) > 0$)

The difference is the **price of uncertainty** -- how much extra worst-case cost you face because your political risk forecast might be wrong.

**Why CFOs care:**

1. **Budgeting:** The sovereignty premium tells you how much contingency to set aside
2. **Communication:** You can tell the board: "Political uncertainty costs us X in worst-case terms"
3. **Trigger definition:** When the premium exceeds a threshold, it is time to act
4. **Scenario comparison:** Compare premiums across different assumptions to identify sensitivity

---

## When to Use Game Theory vs. Simple Optimization

Not every problem needs game theory. Here is a practical guide:

| Situation | Approach | Why |
|-----------|----------|-----|
| Machine maintenance scheduling | Simple optimization | Environment is passive, good historical data |
| Supplier pricing under trade war | Game theory | Adversarial actors, feedback loops, ambiguity |
| Portfolio allocation with known returns | Simple optimization | Passive market (for a small investor) |
| Supplier diversification under political risk | Game theory | Sequential decisions, unknown distributions, strategic interactions |
| Weather-dependent logistics | Simulation / stochastic optimization | Weather is non-adversarial, decent forecasts exist |
| Regulatory compliance timing | Game theory | Regulator responds to firm behavior, timing is strategic |

**Rule of thumb:** If the environment could "respond" to your actions (even indirectly, through political dynamics), and if you are uncertain about the probability model, game theory is the right framework.

---

## Connection to the Repository

The business context described here maps directly to the repository:

- The **scenario** (European firm, US supplier, tariff risk) is described in `README.md` and the notebook introduction
- The **cost parameters** come from `GameSpec` and `CFOConfig` classes in the notebook
- The **three layers of uncertainty** correspond to the "complexity ladder" in the notebook's first cell
- The **sovereignty premium** is computed in the notebook's results sections
- The **CFO interpretation** is detailed in `LLM_context_prompt.md`

---

## Validation Quiz

### Questions

**Q1.** A European firm faces a 20% tariff on its US cloud supplier. The firm's annual cloud spend is EUR 15M. In simple terms, what is the annual tariff cost?

**Q2.** Name two reasons why a standard NPV analysis fails for sovereignty decisions.

**Q3.** At which "level of uncertainty" does Wasserstein DRO operate?
- (a) Level 0 -- known distribution
- (b) Level 1 -- unknown but rational opponent
- (c) Level 2 -- unknown distribution

**Q4.** What is the difference between a "decision" and a "policy" in the context of this model? Give a one-sentence definition of each.

**Q5.** The sovereignty premium is defined as $V_0(\varepsilon(t)) - V_0(\varepsilon = 0)$. If the baseline worst-case cost is -45 units and the robust worst-case cost is -49 units, what is the sovereignty premium? Is this a good or bad thing?

**Q6.** A colleague says: "We estimated a 10% probability of tariffs. Let's just use expected value to decide." Give two specific objections to this approach, using concepts from this step.

**Q7.** True or False: In this model, the supplier is modeled as a separate strategic player with its own objectives.

---

### Answers

**A1.** EUR 15M x 20% = **EUR 3M per year**. This is the direct tariff cost if fully passed through by the supplier. In the model's abstract units, this would be mapped to the `tariff_cost` parameter.

**A2.** Any two of:
- **Static vs. dynamic:** NPV gives a one-time decision but the real problem is sequential -- you can adapt over time (option value of waiting).
- **Single probability:** NPV assumes you know the tariff probability precisely, but political risk forecasts are unreliable.
- **No adversarial thinking:** NPV treats uncertainty as passive randomness, but political actors can respond to firm actions.

**A3.** **(c) Level 2 -- unknown distribution.** Wasserstein DRO protects against the case where the probability distribution itself is wrong. CVaR handles Level 0 (tail risk under a known distribution), and game framing handles Level 1 (rational opponent).

**A4.**
- A **decision** is a single choice made at one point in time (e.g., "invest now").
- A **policy** is a complete contingency plan that specifies an action for every possible state at every time period (e.g., "if tariff is on and migration is at year 1, then accelerate").

**A5.** The sovereignty premium is $-49 - (-45) = -4$ units. Since worst-case costs are negative (they represent losses), the premium means the robust scenario is **4 units worse** than the baseline. This is the **cost of uncertainty** -- the extra worst-case loss you face when accounting for forecast errors. It is not "good" or "bad" in itself; it quantifies the price of ambiguity, which helps the CFO budget contingency reserves.

**A6.** Two objections:
1. **The 10% might be wrong** (ambiguity). Political risk is hard to forecast. If the true probability is 25%, the expected-value decision could be dangerously wrong. Wasserstein DRO explicitly protects against this by considering a range of plausible distributions around your 10% estimate.
2. **Expected value ignores tail risk.** Even if 10% is correct, the *average* outcome is not what matters for a risk-averse CFO. What matters is the downside -- the worst 10% of scenarios. CVaR captures this by focusing on the tail of the distribution, not the mean.

**A7.** **False.** In the current model, the supplier is **not** a separate strategic player. It is assimilated into Nature: the supplier mechanically passes tariff costs through to the firm (100% pass-through) without any strategic behavior. The two players are the Firm (minimizer) and Nature (maximizer), where Nature encompasses both the political decision (tariff on/off) and the supplier as a passive cost vector. Modeling the supplier as a strategic player is discussed as a future extension (see Step 08).

---

**Previous step:** [00 -- Welcome and Roadmap](00_welcome.md)
**Next step:** [02 -- Game Theory Primer](02_game_theory_primer.md)
