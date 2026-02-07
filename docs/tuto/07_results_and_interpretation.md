# Step 7 -- Results and Interpretation

## Learning Objectives

By the end of this step, you will:

- Understand the four scenarios the model runs and what they represent
- Be able to read a policy table and explain what each entry means
- Know why "wait" is the optimal initial action under baseline parameters
- Compute and interpret the sovereignty premium
- Understand the sensitivity analysis and what drives action changes
- Translate model outputs into CFO-friendly language

---

## The Four Scenarios

The notebook runs the DP solver four times, each with a different ambiguity schedule:

| Scenario | Epsilon Schedule | What It Tests |
|----------|-----------------|---------------|
| **Baseline** | $\varepsilon(t) = 0$ for all $t$ | No ambiguity. Pure CVaR under nominal model. Reference point. |
| **Standard** | $\varepsilon(t) \in [0.02, 0.30]$, cyclical | Time-varying ambiguity following a risk indicator cycle |
| **Volatile** | $\varepsilon(t) \in [0.02, 0.40]$, cyclical | Same cycle but stronger ambiguity (worst-case more adversarial) |
| **Macro** | $\varepsilon(t) = 0.30$ at $t=1,3$; lower otherwise | Ambiguity spikes at specific years (elections, negotiations) |

Each scenario produces:
- A **value function** $V_t(s)$ for all states and times
- A **policy** $\pi^*(t, s)$ for all states and times
- A **V0 value**: the worst-case cost-to-go from the initial state at $t=0$

---

## Reading the Policy

The policy $\pi^*(t, s)$ is a matrix with $T$ rows (time periods) and 64 columns (states). Each entry is an action index:

| Index | Action Name |
|:-----:|------------|
| 0 | wait (do nothing) |
| 1 | invest |
| 2 | hedge_only |
| 3 | accelerate_migration |
| 4 | invest+hedge/exercise |

### Example Policy Reading

Suppose the policy says $\pi^*(3, s) = 4$ where $s = (\tau=1, m=2, i=1, h=1, e=0)$.

Translation: "At year 3, if tariffs are active, migration is at year 2, and you have already started investing and hedging, then take action 4 (invest+hedge/exercise). Since $m=2$ and the action advances $m$ by 1 to reach $m=3 = M$, this triggers the exit."

In business terms: "You are 2/3 through migration with tariffs persisting. The model recommends completing migration and exercising the exit clause this year."

### Policy Patterns

Typical patterns you will observe in the model's output:

**When tariff is OFF ($\tau = 0$):**
- At early times ($t$ small): mostly "wait" -- no urgency when tariff is not active
- At later times ($t$ large, close to horizon): "wait" -- not enough time remaining to justify costly migration

**When tariff is ON ($\tau = 1$):**
- At early times with $m = 0$: "invest" or "hedge" -- start preparing
- At mid-horizon with $m > 0$: "accelerate" or "invest+hedge" -- finish the job
- At $m = M - 1$: "invest+hedge/exercise" -- trigger exit
- Near horizon end: "wait" -- not enough time to complete migration; endure the tariff

---

## Why "Wait" Is Optimal at $t = 0$

The central result: **under the baseline parameters, the optimal initial action is always "wait" across all four scenarios.**

This may seem surprising. Why not immediately start investing in migration? Three factors explain this:

### 1. Option Value of Waiting

The tariff is not currently active (initial state has $\tau = 0$). There is only a 15% chance it appears next year. By waiting, the firm preserves the option to invest *later*, after observing whether the tariff actually materializes. Investing now would spend 8.0 units of CAPEX against a threat that has an 85% chance of not materializing in year 1.

**Analogy:** You do not buy fire insurance the moment you hear about a wildfire 100 miles away. You monitor the situation and act when the risk becomes concrete.

### 2. Discount Effect

With a 10% WACC, costs far in the future are heavily discounted. A tariff cost of 10.0 in year 5 is worth only $10 / (1.10)^5 = 6.21$ today. The urgency to act early is reduced because future costs "weigh less."

### 3. Exit Cost vs. Exposure

The total exit cost is 19.0 units (termination fee + cutover + recertification), and migration takes 3 years of OPEX at 1.5/year = 4.5 units, plus the initial CAPEX of 8.0. Total migration cost: approximately 31.5 units.

Meanwhile, the expected tariff cost under the stationary distribution (60% tariff probability) over 10 years is roughly $10 \times 0.60 \times \sum_{t=0}^{9} \gamma_t \approx 37$ units.

The numbers are close, which means the option to wait and learn has significant value. The model does not recommend immediate migration because the **expected benefit is marginal** and waiting preserves flexibility.

### What Would Change the Answer?

The optimal initial action shifts from "wait" to "invest" or "hedge" when:

- **$p_{01}$ increases** (tariff more likely): at around $p_{01} > 0.25$, the model recommends hedging at $t=0$
- **$\varepsilon$ increases significantly**: very high ambiguity makes the worst case more severe
- **Tariff is already ON** ($\tau_0 = 1$): if the initial state has an active tariff, the model immediately recommends action
- **Migration cost decreases**: cheaper CAPEX or shorter exit timeline makes early action more attractive
- **Horizon lengthens**: more time to amortize migration costs

---

## The Sovereignty Premium

The sovereignty premium quantifies **the cost of ambiguity**:

$$\text{Sovereignty Premium} = V_0^{\text{robust}} - V_0^{\text{baseline}}$$

Where:
- $V_0^{\text{baseline}}$ = worst-case cost under the baseline (no ambiguity, $\varepsilon = 0$)
- $V_0^{\text{robust}}$ = worst-case cost with Wasserstein ambiguity ($\varepsilon(t) > 0$)

### Example Computation

Suppose the notebook outputs:

| Scenario | $V_0$ | Optimal $a_0$ |
|----------|:-----:|:--------------:|
| Baseline | -42.3 | wait |
| Standard | -45.1 | wait |
| Volatile | -47.7 | wait |
| Macro | -46.0 | wait |

The sovereignty premiums are:

| Scenario | Premium | Interpretation |
|----------|:-------:|---------------|
| Standard | $-45.1 - (-42.3) = -2.8$ | Ambiguity costs 2.8 units in worst-case terms |
| Volatile | $-47.7 - (-42.3) = -5.4$ | Stronger ambiguity costs 5.4 units |
| Macro | $-46.0 - (-42.3) = -3.7$ | Macro shocks cost 3.7 units |

**Reading these numbers:** The premium is negative because costs are negative (losses). A premium of -5.4 means the robust worst-case is 5.4 units worse than the baseline. In business terms: "Accounting for political forecast uncertainty costs us 5.4 additional units in worst-case NPV."

### What the Premium Tells the CFO

1. **Contingency sizing:** Budget at least [premium] as a contingency reserve for political uncertainty
2. **Sensitivity signal:** If the volatile premium is much larger than the standard, the firm is sensitive to ambiguity levels -- invest in better political risk intelligence
3. **Communication:** "Our sovereignty exposure has a worst-case premium of X, driven by political forecast uncertainty"
4. **Threshold monitoring:** If the premium crosses a pre-defined threshold, escalate to the Strategy Committee

---

## Sensitivity Analysis

The notebook runs sensitivity analysis on two key parameters:

### Horizon Length

As the planning horizon increases from 5 to 15 years:

- **Baseline cost increases** (more periods of potential tariff exposure)
- **Sovereignty premium increases** (more periods where ambiguity matters)
- **Optimal policy may change** (longer horizon justifies larger upfront investments)

**Key insight:** Firms with longer planning horizons (infrastructure, defense, energy) face larger sovereignty premiums and should invest earlier in migration.

### Tariff Persistence ($p_{10}$)

As $p_{10}$ decreases (tariff becomes stickier):

- **Worst-case cost increases sharply** (once tariff appears, it stays longer)
- **Optimal action shifts earlier** from "wait" toward "invest" or "hedge"
- **Sovereignty premium increases** (more uncertainty about long-lasting regimes)

**Key insight:** The stickiness of political regimes matters more than the probability of initial onset. A tariff with $p_{01} = 0.10$ and $p_{10} = 0.03$ (rare but very persistent) is more dangerous than one with $p_{01} = 0.30$ and $p_{10} = 0.25$ (frequent but quickly reversed).

### Ambiguity Radius

As $\varepsilon$ increases:

- **Value function worsens** (Nature is more adversarial)
- **Policy becomes more conservative** (earlier hedging, earlier investment)
- **Convergence:** Beyond some $\varepsilon_{\max}$, the policy stabilizes (pure worst-case reached)

The **break-even $\varepsilon$** is the ambiguity level at which the optimal action switches from "wait" to "invest." This is a critical threshold for the CFO: "If our forecast uncertainty exceeds $\varepsilon^*$, we should act."

---

## CFO Interpretation Framework

When presenting results to a CFO or board, translate the technical outputs:

### From Model Output to Business Language

| Technical Output | CFO Translation |
|-----------------|-----------------|
| $V_0 = -47.7$ | "Under worst-case conditions with political uncertainty, our 10-year sovereign exposure costs us 47.7 units in NPV terms" |
| $\pi^*(0, s_0) = \text{wait}$ | "The model recommends holding current position. No immediate investment in migration is warranted under current parameters" |
| Sovereignty premium = 5.4 | "Political forecast uncertainty costs us 5.4 units in additional worst-case NPV. Budget this as a contingency reserve" |
| Policy switches at $p_{01} > 0.25$ | "If the probability of tariff imposition exceeds 25%, we should start hedging. Monitor political risk indicators" |

### The Four Key Questions for the Board

1. **What should we do now?** Look at $\pi^*(0, s_0)$. The model recommends an immediate action (or "wait").

2. **What triggers a change?** Look at the sensitivity analysis. Identify which parameter changes cause the optimal action to shift. These become monitoring triggers.

3. **How much is uncertainty costing us?** Look at the sovereignty premium. This is the "cost of ambiguity" that the firm faces simply because political risk is hard to forecast.

4. **How robust is this recommendation?** Look at whether the optimal action changes across scenarios. If "wait" is optimal in all four scenarios, the recommendation is robust. If it changes in the volatile scenario, the recommendation is sensitive to uncertainty levels.

### Executive Summary Template

The notebook and `LLM_context_prompt.md` provide a template for generating executive summaries:

> **Bottom line:** The optimal initial action is [wait/invest/hedge]. This is robust across [all/most] scenarios tested.
>
> **Sovereignty premium:** [X] units, representing the cost of political forecast uncertainty.
>
> **Key triggers:** Switch to [invest/hedge] if [tariff probability exceeds Y% / ambiguity exceeds Z / tariff persists for N periods].
>
> **Recommendation:** [Continue monitoring / Allocate budget for hedging / Begin migration planning].

---

## Common Misinterpretations

Be aware of these when discussing results:

**"V0 = -47.7 means we will lose 47.7 units."**
No. V0 is the worst-case cost *under the optimal policy*. It is the cost if everything that can go wrong does go wrong (within the Wasserstein ball), and the firm responds optimally. Actual costs will likely be lower.

**"Wait means do nothing forever."**
No. "Wait" is the optimal action *at $t=0$ in the initial state*. The policy is state-contingent: if the tariff turns on at $t=1$, the model may recommend "invest" or "hedge" in that new state. "Wait" means "no action is needed *right now*."

**"The model says we should not hedge."**
Not necessarily. The model may say "don't hedge at $t=0$ in the current state." But it might recommend hedging at $t=2$ if the tariff has appeared. Read the full policy matrix, not just the initial action.

**"These numbers are precise predictions."**
No. The model is a toy prototype with abstract cost units. The value is in the *structure* of the policy (trigger conditions, timing, sequencing) and the *relative comparisons* (which scenario is worse), not in the precise numbers.

---

## Connection to the Repository

- **Scenario runs:** Notebook Section 9 -- the four calls to `dp_solve_cfo()`
- **Comparison table:** Notebook Section 9 -- prints V0, optimal action, sovereignty premium for each scenario
- **Policy matrices:** Notebook Sections 9-10 -- printed and visualized
- **Sensitivity analysis:** Notebook Section 10 -- horizon and tariff persistence sweeps
- **CFO interpretation:** Notebook Section 11 -- business language summary
- **Visualizations:** Notebook Section 12 -- heatmaps, policy maps, plots
- **Executive summary template:** `LLM_context_prompt.md`

---

## Validation Quiz

### Questions

**Q1.** The model outputs the following results:

| Scenario | $V_0$ | Optimal $a_0$ |
|----------|:-----:|:--------------:|
| Baseline | -38.0 | wait |
| Standard | -41.5 | wait |
| Volatile | -44.2 | invest |

(a) Compute the sovereignty premium for the Standard and Volatile scenarios.
(b) What changed in the Volatile scenario that caused the optimal action to switch from "wait" to "invest"?

**Q2.** A board member says: "The model recommends waiting. That means we have no political risk exposure." Is this correct? Explain.

**Q3.** The policy matrix shows $\pi^*(2, s) = 3$ where $s = (\tau=1, m=1, i=1, h=0, e=0)$. Translate this into a business recommendation.

**Q4.** Explain why higher tariff persistence (lower $p_{10}$) increases the sovereignty premium.

**Q5.** Name two parameters that, if changed, could cause the optimal initial action to switch from "wait" to "invest."

**Q6.** The CFO asks: "How should I use the sovereignty premium in my budget?" Give a practical answer in 2-3 sentences.

**Q7.** True or False: If the optimal action is "wait" in all four scenarios, the firm faces no risk.

**Q8.** What is the difference between the "initial action" $\pi^*(0, s_0)$ and the "full policy" $\pi^*(t, s)$? Why is the full policy more valuable?

---

### Answers

**A1.**

(a) Sovereignty premiums:
- Standard: $-41.5 - (-38.0) = -3.5$ units
- Volatile: $-44.2 - (-38.0) = -6.2$ units

(b) In the Volatile scenario, $\varepsilon_{\max}$ is increased to 0.40 (vs. 0.30 in Standard). This gives Nature more room to shift distributions adversarially, making the worst-case significantly worse. The worst case under "wait" becomes so bad that "invest" (which incurs CAPEX but reduces future tariff exposure) becomes the better option. The higher ambiguity tips the balance from "option value of waiting" to "cost of inaction."

**A2.** This is **incorrect**. "Wait" means "no immediate action is optimal *given current conditions*." The firm still faces political risk exposure -- the value function $V_0$ reflects the worst-case cost of that exposure. The recommendation to wait means that the cost of acting now (CAPEX, OPEX) exceeds the expected benefit of acting now. The firm is choosing to *bear* the risk for now, with the intention of acting later if conditions change (tariff appears, ambiguity increases). The policy provides contingency actions for every future state.

**A3.** Action 3 is "accelerate_migration." The state $(\tau=1, m=1, i=1, h=0, e=0)$ means: tariff is active, 1 year of migration completed, investment program underway, no hedge, not yet exited.

Business recommendation: "At year 2, with tariffs persisting and migration only 1/3 complete, the model recommends accelerating migration. Increase OPEX spending to fast-track the supplier transition, aiming to complete migration sooner and exercise the exit clause."

**A4.** Lower $p_{10}$ means tariffs are harder to remove once imposed. This has two effects:
1. **Higher expected tariff exposure:** Once a tariff appears, it lasts longer, increasing cumulative costs.
2. **More uncertainty about duration:** The firm cannot rely on tariffs resolving quickly, so the worst-case scenarios become significantly worse.

Both effects increase the gap between the robust model (where Nature can exploit this persistence) and the baseline, widening the sovereignty premium. The ambiguity about whether the tariff will persist for 2 years or 8 years is more costly when persistence is the norm.

**A5.** Two parameters:
1. **$p_{01}$ (tariff onset probability):** If increased above ~0.25, the tariff is likely enough that the cost of waiting exceeds the cost of investing.
2. **$\varepsilon$ (ambiguity radius):** If increased significantly (e.g., $\varepsilon_{\max} = 0.50$), the worst-case under "wait" becomes so severe that early investment is justified as insurance.

Other valid answers: reducing `capex_invest` (cheaper migration), reducing `exit_years` (faster migration), increasing `tariff_cost` (more painful tariff), or starting with $\tau_0 = 1$ (tariff already active).

**A6.** "The sovereignty premium should be treated as a **contingency reserve** in your budget. If the standard premium is 3.5 units and the volatile premium is 6.2 units, set aside between 3.5 and 6.2 units as a buffer for political risk. Additionally, use the premium as a **monitoring trigger**: if quarterly re-computation shows the premium growing beyond a pre-agreed threshold (e.g., 5.0 units), escalate to the Strategy Committee to reassess the migration timeline."

**A7.** **False.** "Wait" being optimal in all scenarios does not mean the firm faces no risk. It means that the *cost of acting now* exceeds the *benefit of acting now* across all uncertainty assumptions tested. The firm still faces significant worst-case exposure (reflected in the $V_0$ values). The risk is borne, not eliminated. The policy includes contingency actions for future states where the tariff materializes.

**A8.** The **initial action** $\pi^*(0, s_0)$ is just the first move -- what to do right now. The **full policy** $\pi^*(t, s)$ is a complete contingency plan for every possible state at every future time period. The full policy is far more valuable because:
- It tells you what to do *if* the tariff appears in year 2, 3, or 5
- It provides trigger conditions (at which state does action change?)
- It adapts to how the situation evolves
- It can be turned into operational decision rules for the team

A single initial action has no adaptive capacity. A full policy is a **strategic playbook**.

---

**Previous step:** [06 -- Code Walkthrough](06_code_walkthrough.md)
**Next step:** [08 -- Extensions and Future](08_extensions_and_future.md)
