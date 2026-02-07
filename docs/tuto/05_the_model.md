# Step 5 -- The Bellman-Wasserstein Sovereignty Model

## Learning Objectives

By the end of this step, you will:

- Understand the full state space of the model and how states are encoded
- Know what each action does concretely (wait, invest, hedge, accelerate, exit)
- Understand how transition dynamics work (tariff Markov chain, migration, flags)
- Be able to compute a stage loss for a given state-action pair
- Understand progressive hedge effectiveness and why it matters
- Read and interpret the complete Bellman-Wasserstein equation
- Trace one step of backward induction for this specific model

---

## The State Space

The model tracks the firm's situation using a state vector $s = (\tau, m, \mathbf{f})$.

### State Variables

| Variable | Symbol | Values | Meaning |
|----------|:------:|--------|---------|
| Tariff regime | $\tau$ | $\{0, 1\}$ | 0 = no tariff, 1 = tariff active |
| Migration progress | $m$ | $\{0, 1, 2, 3\}$ | Years of migration completed (exit requires $m = 3$) |
| Investment started | $i$ | $\{0, 1\}$ | Has the firm launched the migration program? |
| Hedge active | $h$ | $\{0, 1\}$ | Is a hedge (dual-source, contract protection) in place? |
| Exit exercised | $e$ | $\{0, 1\}$ | Has the firm fully exited the supplier? |

### Total Number of States

$$|\mathcal{S}| = 2 \times 4 \times 2 \times 2 \times 2 = 64 \text{ states}$$

However, not all 64 combinations are reachable. For example, $e = 1$ (exit exercised) requires $m = 3$ (migration complete) and $i = 1$ (investment started). The model handles this through the transition logic -- unreachable states simply have zero probability.

### State Encoding

States are encoded as a single integer for computational efficiency:

$$\text{index}(s) = \tau \times 32 + m \times 8 + i \times 4 + h \times 2 + e$$

This maps each state tuple $(\tau, m, i, h, e)$ to a unique integer in $\{0, 1, \ldots, 63\}$.

**Example:** State $(\tau=1, m=2, i=1, h=1, e=0)$ -- tariff is on, 2 years migrated, investment started, hedge active, not yet exited:

$$\text{index} = 1 \times 32 + 2 \times 8 + 1 \times 4 + 1 \times 2 + 0 = 32 + 16 + 4 + 2 = 54$$

In the notebook, this is implemented by `encode_state()` and reversed by `decode_state()`.

### Reading a State

Practice reading states in business language:

| State | $\tau$ | $m$ | $i$ | $h$ | $e$ | Business Meaning |
|:-----:|:------:|:---:|:---:|:---:|:---:|:-----------------|
| A | 0 | 0 | 0 | 0 | 0 | No tariff, no migration, no programs -- business as usual |
| B | 1 | 0 | 0 | 0 | 0 | Tariff hit, no preparation -- fully exposed |
| C | 1 | 1 | 1 | 1 | 0 | Tariff on, 1 year migrated, investing and hedging -- in transition |
| D | 0 | 3 | 1 | 0 | 1 | No tariff, fully migrated, exited -- sovereign |

State A is where every firm starts. State D is the goal (if sovereignty is pursued). The model finds the optimal path between them.

---

## The Action Space

The firm chooses from 5 actions each period:

| Index | Action | What It Does | Immediate Cost |
|:-----:|--------|-------------|----------------|
| 0 | **Wait** | Do nothing. No progress. | 0 (but exposed to tariff) |
| 1 | **Invest** | Start/continue migration program. Sets $i=1$, advances $m$ by 1. | CAPEX (if first time) + OPEX |
| 2 | **Hedge only** | Set up hedge without investing in migration. Sets $h=1$. | CAPEX (hedge setup) |
| 3 | **Accelerate migration** | Fast-track migration (requires $i=1$). Advances $m$ by 1 with higher OPEX. | Higher OPEX |
| 4 | **Invest + Hedge / Exercise** | Combined action. If ready ($m=3$), exercises exit. Otherwise, invests and hedges. | Varies |

### Action Constraints

Not all actions are available in all states. The logic handles this through the transition function:

- You cannot **exit** ($e \to 1$) unless $m = 3$ (migration complete)
- You cannot **accelerate** unless $i = 1$ (investment already started)
- You can always **wait** (but you may pay tariff costs)
- **Investing** when $i = 1$ simply continues migration ($m$ advances)
- **Hedging** when $h = 1$ already has no additional CAPEX

### Business Interpretation

Think of these actions as the decisions a CFO faces each year:

- **Wait:** "The political situation is unclear. Let's hold and see how tariffs evolve before committing resources."
- **Invest:** "We're launching the supplier diversification program. Budget EUR 8M CAPEX and EUR 1.5M/year OPEX."
- **Hedge:** "We're not ready to migrate, but let's set up contract protections and a dual-source agreement. Budget EUR 2M."
- **Accelerate:** "The situation is deteriorating. Let's fast-track migration. Increase OPEX spending."
- **Exit:** "Migration is complete. Exercise the exit clause. Pay termination fees and cut over."

---

## Transition Dynamics

The state evolves according to three components:

### 1. Tariff Regime (Stochastic)

The tariff follows a two-state Markov chain:

$$P(\tau_{t+1} = 1 | \tau_t = 0) = p_{01} \quad \text{(tariff turns on)}$$
$$P(\tau_{t+1} = 0 | \tau_t = 1) = p_{10} \quad \text{(tariff turns off)}$$

Default values: $p_{01} = 0.15$ (15% chance tariff appears), $p_{10} = 0.10$ (10% chance tariff disappears).

**Interpretation:** Tariffs are "sticky" -- once imposed, they tend to persist ($p_{10}$ is low). This captures the political reality that tariffs are easier to impose than to remove.

The **stationary probability** of tariff being on is:

$$\pi_1 = \frac{p_{01}}{p_{01} + p_{10}} = \frac{0.15}{0.15 + 0.10} = 0.60$$

In the long run, tariffs are on 60% of the time under these parameters. This is a high-risk environment.

### 2. Migration Progress (Deterministic)

Migration progress advances based on the action taken:

| Action | Effect on $m$ |
|--------|:-------------:|
| Wait | $m$ stays the same |
| Invest | $m \to \min(m + 1, M)$ if $i = 1$ |
| Hedge only | $m$ stays the same |
| Accelerate | $m \to \min(m + 1, M)$ if $i = 1$ |
| Invest+Hedge/Exit | $m \to \min(m + 1, M)$, or exit if $m = M$ |

Migration takes `exit_years = 3` years from investment start to exit readiness. Each investment or acceleration action advances $m$ by 1 year.

### 3. Flag Updates (Deterministic)

Flags update based on actions:

| Flag | Sets to 1 When |
|------|---------------|
| $i$ (investment) | Action = Invest, Accelerate, or Invest+Hedge |
| $h$ (hedge) | Action = Hedge only, or Invest+Hedge |
| $e$ (exit) | Action = Invest+Hedge/Exit **and** $m = M = 3$ |

Once a flag is set to 1, it stays at 1 (irreversible). You cannot "un-invest" or "un-hedge."

### The Full Transition Kernel

The overall transition probability from state $s$ to state $s'$ given action $a$ is:

$$p_0(s' | s, a) = P(\tau' | \tau) \cdot \mathbf{1}[m' = f_m(m, a)] \cdot \mathbf{1}[\mathbf{f}' = f_\mathbf{f}(\mathbf{f}, a, m')]$$

The tariff transition is stochastic. Everything else is deterministic given the action. This means for each state-action pair, only 2 next states have nonzero probability (corresponding to tariff turning on or off).

---

## The Loss Function

The stage loss $\ell(s, a)$ represents the total cost incurred in one period:

$$\ell(s, a) = \ell_{\text{tariff}}(s, a) + \ell_{\text{CAPEX}}(s, a) + \ell_{\text{OPEX}}(s, a) + \ell_{\text{exit}}(s, a)$$

### Tariff Cost

| Situation | Cost |
|-----------|:----:|
| No tariff ($\tau = 0$) | 0 |
| Tariff on, no hedge | `tariff_cost` = 10.0 |
| Tariff on, hedge active | `hedged_tariff_cost` = 6.0 (reduced by hedge) |
| Post-exit ($e = 1$) | `post_exit_cost` = 1.0 (residual) |

The hedge reduces tariff exposure but does not eliminate it entirely. The reduction depends on the **progressive hedge effectiveness** (see below).

### CAPEX (One-Time Costs)

| Situation | Cost |
|-----------|:----:|
| First investment ($i: 0 \to 1$) | `capex_invest` = 8.0 |
| Hedge setup ($h: 0 \to 1$) | `capex_hedge_setup` = 2.0 |

These are paid once, when the program is initiated.

### OPEX (Recurring Costs)

| Situation | Cost |
|-----------|:----:|
| Migration in progress ($i=1$, $e=0$) | `opex_migration` = 1.5 per year |
| Dual-running under tariff ($\tau=1$, $i=1$) | `opex_dual_run` = 0.7 per year (additional) |

### Exit Costs

When the firm exercises exit ($e: 0 \to 1$):

| Component | Cost |
|-----------|:----:|
| Termination fee | 12.0 |
| Cutover cost | 5.0 |
| Recertification/audit | 2.0 |
| **Total exit cost** | **19.0** |

### Worked Example

**State:** $(\tau=1, m=1, i=1, h=0, e=0)$ -- tariff on, 1 year migrated, investing, no hedge, not exited.

**Action:** Invest (continue migration).

Costs:
- Tariff: 10.0 (tariff on, no hedge)
- CAPEX: 0 (investment already started, $i$ was already 1)
- OPEX: 1.5 (migration in progress) + 0.7 (dual-run under tariff) = 2.2
- Exit: 0 (not exiting)

**Total stage loss:** $10.0 + 0 + 2.2 + 0 = 12.2$ units

---

## Progressive Hedge Effectiveness

This is one of the key innovations of the model. In many models, a hedge is binary: either fully effective or not at all. Here, hedge effectiveness **scales with migration progress**:

$$\eta(m) = \frac{m}{M}$$

Where $M = 3$ (exit years).

| Migration Progress $m$ | Hedge Effectiveness $\eta(m)$ |
|:-:|:-:|
| 0 | 0% |
| 1 | 33% |
| 2 | 67% |
| 3 | 100% |

**Business intuition:** A hedge (e.g., dual-sourcing agreement) becomes more effective as you build the alternative supplier relationship. At $m = 0$, you have no alternative -- the hedge is just a contract, with limited practical effect. At $m = 2$, you have a working alternative for 2/3 of your needs. At $m = 3$, you are fully migrated and the hedge is moot (you can exit).

**Impact on tariff cost:**

$$\ell_{\text{tariff}}(s, a) = \begin{cases}
\text{tariff\_cost} \times (1 - \eta(m)) + \text{hedged\_tariff\_cost} \times \eta(m) & \text{if } \tau=1, h=1 \\
\text{tariff\_cost} & \text{if } \tau=1, h=0 \\
0 & \text{if } \tau=0
\end{cases}$$

For $m=2$, $h=1$, $\tau=1$: tariff cost = $10 \times (1/3) + 6 \times (2/3) = 3.33 + 4.0 = 7.33$ instead of 10.0.

---

## The Complete Bellman-Wasserstein Equation

Now we can write the full equation that the model solves. All the pieces from Steps 03 and 04 come together:

$$\boxed{V_t(s) = \min_{a \in \mathcal{A}} \sup_{p \in \mathcal{P}_{\varepsilon(t)}(p_0(\cdot | s, a))} \text{CVaR}_\alpha^p\left[\gamma_t \cdot \ell(s, a) + V_{t+1}(S')\right]}$$

Let us read this term by term, one final time with full understanding:

| Component | What It Is | Where We Learned It |
|-----------|-----------|---------------------|
| $V_t(s)$ | Cost-to-go from state $s$ at time $t$ under optimal policy | Step 03 |
| $\min_{a \in \mathcal{A}}$ | Firm chooses the best action (5 options) | Step 02 (game), this step (actions) |
| $\sup_{p \in \mathcal{P}_{\varepsilon(t)}}$ | Nature chooses worst distribution in Wasserstein ball | Step 04 (DRO) |
| $\text{CVaR}_\alpha^p$ | Average of worst $(1-\alpha)$ outcomes under distribution $p$ | Step 04 (CVaR) |
| $\gamma_t \cdot \ell(s, a)$ | Discounted immediate cost | Step 03 (discount), this step (losses) |
| $V_{t+1}(S')$ | Future cost from next state (already computed) | Step 03 (backward induction) |
| $p_0(\cdot \mid s, a)$ | Nominal transition (tariff Markov chain + deterministic updates) | This step (transitions) |
| $\mathcal{P}_{\varepsilon(t)}(p_0)$ | Wasserstein ball around nominal transition | Step 04 (Wasserstein ball) |

### Terminal Condition

$$V_T(s) = 0 \quad \forall s \in \mathcal{S}$$

### The Optimal Policy

$$\pi^*(t, s) = \arg\min_{a \in \mathcal{A}} \left\{ \sup_{p \in \mathcal{P}_{\varepsilon(t)}} \text{CVaR}_\alpha^p\left[\gamma_t \cdot \ell(s, a) + V_{t+1}(S')\right] \right\}$$

---

## Tracing One Step of Backward Induction

Let us trace how the solver handles one specific state at one specific time.

**Setup:** $t = 8$ (two periods from end, $T = 10$). State $s = (\tau=1, m=0, i=0, h=0, e=0)$ -- tariff is on, no migration, no programs.

**Step 1: For each action, compute the argument of the min.**

**Action 0 (Wait):**
- Stage loss: $\ell = 10.0$ (full tariff exposure)
- Next states: $(\tau'=0, m=0, i=0, h=0, e=0)$ with prob $p_{10} = 0.10$ and $(\tau'=1, m=0, i=0, h=0, e=0)$ with prob $0.90$
- Look up $V_9$ for those two states (already computed)
- Compute nominal cost vector: $\gamma_8 \times 10.0 + [V_9(\text{state with } \tau'=0), V_9(\text{state with } \tau'=1)]$
- If $\varepsilon_8 > 0$: solve Wasserstein LP to find worst-case CVaR
- Result: robust CVaR value for Wait

**Action 1 (Invest):**
- Stage loss: $\ell = 10.0 + 8.0 + 1.5 + 0.7 = 20.2$ (tariff + CAPEX + OPEX + dual-run)
- Next states: $(\tau'=0, m=1, i=1, h=0, e=0)$ with prob 0.10, $(\tau'=1, m=1, i=1, h=0, e=0)$ with prob 0.90
- Look up $V_9$ for those states
- Compute robust CVaR
- Result: robust CVaR value for Invest

**(Repeat for actions 2, 3, 4.)**

**Step 2: Choose the action with minimum robust CVaR.**

$$\pi^*(8, s) = \arg\min\{V_{\text{wait}}, V_{\text{invest}}, V_{\text{hedge}}, V_{\text{accelerate}}, V_{\text{exit}}\}$$

**Step 3: Record the optimal value.**

$$V_8(s) = \min\{V_{\text{wait}}, V_{\text{invest}}, V_{\text{hedge}}, V_{\text{accelerate}}, V_{\text{exit}}\}$$

This process repeats for all 64 states at $t = 8$, then for $t = 7$, and so on down to $t = 0$.

---

## Connection to the Repository

- **State encoding/decoding:** `encode_state()` and `decode_state()` functions in the notebook
- **Action definitions:** Constants `WAIT`, `INVEST`, `HEDGE_ONLY`, `ACCELERATE_MIGRATION`, `INVEST_HEDGE_EXERCISE` in the notebook
- **Transition dynamics:** `nominal_tariff_transition()` and `build_p0_over_full_state()` functions
- **Loss function:** `stage_losses_cfo()` function
- **Hedge effectiveness:** `hedge_effectiveness_factor()` function
- **Full solver:** `dp_solve_cfo()` function
- **Mathematical formulation:** `README.md` Sections "State Space" through "Objective: Robust CVaR"
- **Detailed framework:** `docs/bellman_wasserstein_mean_field_framework.md`, Section 2

---

## Validation Quiz

### Questions

**Q1.** Encode the following state as an integer index: tariff OFF ($\tau=0$), migration at 2 years ($m=2$), investment started ($i=1$), hedge active ($h=1$), not exited ($e=0$).

Use the formula: $\text{index} = \tau \times 32 + m \times 8 + i \times 4 + h \times 2 + e$

**Q2.** Decode state index 37 back to its components $(\tau, m, i, h, e)$. What does this state mean in business language?

**Q3.** A firm is in state $(\tau=1, m=2, i=1, h=1, e=0)$. It takes action "Accelerate migration." Compute the stage loss using these parameters:
- tariff_cost = 10.0, hedged_tariff_cost = 6.0
- No new CAPEX (investment and hedge already started)
- opex_migration = 1.5, opex_dual_run = 0.7
- Hedge effectiveness $\eta(m=2) = 2/3$

**Q4.** In the tariff Markov chain with $p_{01} = 0.15$ and $p_{10} = 0.10$, what is the probability that the tariff is still OFF after 2 consecutive periods, starting from OFF?

**Q5.** Why does hedge effectiveness increase with migration progress? Give a business-world explanation.

**Q6.** The model has 64 states, 5 actions, and 10 time periods. How many subproblems does backward induction solve? How does this compare to brute-force enumeration?

**Q7.** True or False: In the transition dynamics, the migration progress $m$ evolves stochastically (randomly) based on the tariff regime.

**Q8.** What are the two next states (and their probabilities) if the current state is $(\tau=0, m=1, i=1, h=0, e=0)$ and the action is "Invest"?

---

### Answers

**A1.** $\text{index} = 0 \times 32 + 2 \times 8 + 1 \times 4 + 1 \times 2 + 0 = 0 + 16 + 4 + 2 + 0 = 22$

**A2.** To decode 37:
- $\tau = \lfloor 37 / 32 \rfloor = 1$, remainder $= 37 - 32 = 5$
- $m = \lfloor 5 / 8 \rfloor = 0$, remainder $= 5$
- $i = \lfloor 5 / 4 \rfloor = 1$, remainder $= 5 - 4 = 1$
- $h = \lfloor 1 / 2 \rfloor = 0$, remainder $= 1$
- $e = 1$

State: $(\tau=1, m=0, i=1, h=0, e=1)$. Business meaning: tariff is ON, migration progress is 0, investment was started, no hedge, exit was exercised. This state is **logically inconsistent** -- you cannot exit ($e=1$) with $m=0$ (no migration progress) since exit requires $m=3$. This is one of the unreachable states in the 64-state space; it would have zero probability in practice.

**A3.**
- Tariff cost with hedge: $10.0 \times (1 - 2/3) + 6.0 \times (2/3) = 10.0 \times 1/3 + 6.0 \times 2/3 = 3.33 + 4.00 = 7.33$
- CAPEX: 0 (both investment and hedge already started)
- OPEX: 1.5 (migration) + 0.7 (dual-run under tariff) = 2.2
- Exit: 0

Total stage loss: $7.33 + 0 + 2.2 + 0 = 9.53$ units.

Compare to the same state without hedge: $10.0 + 0 + 2.2 + 0 = 12.2$. The hedge saves about 2.67 units per period at this migration stage.

**A4.** Starting from OFF, the tariff stays OFF after period 1 with probability $1 - p_{01} = 0.85$. Given it is still OFF, it stays OFF after period 2 with probability $0.85$ again. So:

$$P(\text{OFF after 2 periods} | \text{start OFF}) = 0.85 \times 0.85 = 0.7225$$

There is a 72.25% chance the tariff remains off for two consecutive years. Conversely, there is a 27.75% chance the tariff will appear at least once in two years.

**A5.** Hedge effectiveness increases with migration progress because the alternative supplier relationship becomes more developed over time:
- At $m=0$: The hedge is just a contract on paper. You have no operational alternative, so the hedge has limited practical impact.
- At $m=1$: You have started building the alternative. Some capacity is available, so the hedge covers part of your exposure.
- At $m=2$: The alternative is largely operational. Most of your volume can be shifted if needed.
- At $m=3$: You are fully ready to switch. The hedge is maximally effective (or you can simply exit).

This captures the business reality that "dual-sourcing" is not instant -- it requires years of relationship building, qualification, and operational readiness.

**A6.** Backward induction solves $64 \times 10 \times 5 = 3{,}200$ subproblems. Brute force would require enumerating $5^{10} \approx 10$ million action sequences, each evaluated against $2^{10} = 1{,}024$ tariff paths, for about $10^{10}$ evaluations. Dynamic programming is roughly **3 million times** more efficient.

**A7.** **False.** Migration progress $m$ evolves **deterministically** based on the firm's action. If the firm invests or accelerates, $m$ increases by 1. If the firm waits or hedges only, $m$ stays the same. The only stochastic component in the transitions is the tariff regime $\tau$, which follows a Markov chain.

**A8.** Starting from $(\tau=0, m=1, i=1, h=0, e=0)$ with action "Invest":
- Migration advances: $m' = \min(1 + 1, 3) = 2$
- Investment flag stays: $i' = 1$
- Hedge flag stays: $h' = 0$
- Exit flag stays: $e' = 0$
- Tariff evolves stochastically from $\tau = 0$:

**Next state 1:** $(\tau'=0, m=2, i=1, h=0, e=0)$ with probability $1 - p_{01} = 0.85$

**Next state 2:** $(\tau'=1, m=2, i=1, h=0, e=0)$ with probability $p_{01} = 0.15$

---

**Previous step:** [04 -- Risk and Ambiguity](04_risk_and_ambiguity.md)
**Next step:** [06 -- Code Walkthrough](06_code_walkthrough.md)
