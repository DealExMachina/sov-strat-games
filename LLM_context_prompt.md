# Context and prompt for LLM (copy-paste below)

---

## CONTEXT: Robust Sovereignty Strategy — CFO Model Results

### What the model does
- **Setting:** Supplier dependency under political/regulatory risk. Tariff shock, exit constraint (3 years lock-in/migration), CAPEX vs OPEX, and one-off exercise costs.
- **Objective:** Worst-case **CVaR 90%** of **NPV cash** over a finite horizon.

### Model parameters (baseline numbers, same units as NPV cash)
| Parameter | Value | Meaning |
|-----------|--------|---------|
| **Running / tariff** | | |
| `tariff_cost` | 10.0 | Running cost per period when tariff is on and not hedged |
| `hedged_tariff_cost` | 6.0 | Running cost per period when tariff is on and hedged (mitigation) |
| `post_exit_cost` | 1.0 | Running cost per period after exit (sovereignty achieved) |
| **Recurring (OPEX)** | | |
| `opex_migration` | 1.5 | Recurring migration cost per period while in progress, before exit |
| `opex_dual_run` | 0.7 | Extra recurring cost per period when tariff=1 and dual-running |
| **One-off (CAPEX / mitigation)** | | |
| `capex_invest` | 8.0 | One-off cost to start investment (migration path) |
| `capex_hedge_setup` | 2.0 | One-off cost to set up hedge (mitigation) |
| **Cost of exit (one-off exercise)** | | |
| `termination_fee` | 12.0 | Contract termination fee at exit |
| `cutover_cost` | 5.0 | Cutover cost at exit |
| `recert_audit_cost` | 2.0 | Recertification/audit cost at exit |
| **Total cost of exit** | **19.0** | termination_fee + cutover_cost + recert_audit_cost |
| **Structure** | | |
| `exit_years` | 3 | Years of progress required before exit can be exercised |
| `horizon` | 6 | Planning horizon (periods) |
| `wacc` (CFO) | 0.10 | Discount rate |
- **Ambiguity:** Transition probabilities are uncertain; we use a Wasserstein ball with radius ε(t) that can vary over time.
- **Sovereignty premium:** V₀(ε(t)) − V₀(ε=0) — the drop in worst-case NPV when we add ambiguity vs. a baseline with no ambiguity.

### Scenarios run
1. **Baseline (no ambiguity)** — reference, no uncertainty penalty.
2. **Standard ε(t)** — time-varying ambiguity.
3. **Volatile (ε_max=0.4)** — stronger ambiguity.
4. **Macro evaluations** — risk and ambiguity peaked in specific years (e.g. 1 and 3).

### Main result
**Optimal initial action at t=0 is always: wait (do nothing)** in all four scenarios. The model compares three actions: wait (do nothing), invest, invest+hedge/exercise.

### Review table (conceptual)
Each scenario has:
- **Optimal a0:** Initial recommended action (always "wait (do nothing)" here).
- **V0:** Worst-case NPV from the optimal policy from today’s state (same units as the objective).
- **Cost vs baseline:** How much worse the worst-case outcome is once we introduce ambiguity. Positive = we lose that much in worst-case terms relative to the baseline.

### CFO interpretation (from the notebook)

**What we did.** We compared four settings: a baseline with no ambiguity on political/regulatory risk, and three cases where we explicitly allow for ambiguity (uncertainty about how bad things can get). In all of them we optimized for **worst-case** value (CVaR 90%) of project NPV over the horizon.

**Bottom line.** The optimal initial decision is always **wait (do nothing)**. That is robust across all scenarios: the model does not recommend investing or hedging at t=0 given current costs, exit constraints, and the way we specified risk.

**What the table means.**
- **V0** = worst-case NPV from the optimal policy, starting from today’s state. It is in the same units as the objective (e.g. NPV cash).
- **Cost vs baseline** = how much worse the worst-case outcome is once we introduce ambiguity, relative to the baseline. A positive number means we "lose" that much in worst-case terms by facing an uncertain rather than a known risk environment.

So the **sovereignty premium** (the drop from baseline V0 when we add ambiguity) is the **cost of uncertainty** in our setup: the amount of worst-case value we give up when we take political/regulatory ambiguity seriously.

**Reading the scenarios.**
- **Baseline (no ambiguity):** Reference. No extra penalty for uncertainty.
- **Standard eps(t):** Time-varying ambiguity. The premium is the cost of that uncertainty in worst-case NPV.
- **Volatile (eps_max=0.4):** Stronger ambiguity. A larger premium means a bigger hit to worst-case value if we assume a more volatile risk environment.
- **Macro evaluations:** Risk and ambiguity peaked in specific years (e.g. year 1 and 3). The premium shows how much worst-case value is affected when we concentrate uncertainty there.

**Implications for the CFO.**
1. **Capital and timing:** Under these assumptions, the model supports delaying investment/hedging. Revisit the decision as new information arrives (e.g. tariff or regulatory clarity).
2. **Budgeting:** Use the **sovereignty premium** (and "Cost vs baseline") as a **reserve or stress buffer**: in worst-case terms, ambiguity "costs" roughly that much NPV. It can inform contingency or scenario planning.
3. **Scenario comparison:** If the premium is much higher in the volatile or macro case, that signals sensitivity to how we model uncertainty. Sensitivity analysis and stress tests around those scenarios are warranted.
4. **Policies, not just numbers:** The same "wait" recommendation with different premiums means the **cost of that stance** varies by scenario. Communicating both the recommended action and the associated worst-case cost helps align board and management on risk tolerance.

---

## PROMPT (choose one or adapt)

- **Option A:** "Using the context above, answer my follow-up questions about the sovereignty model, the results, and the CFO interpretation."
- **Option B:** "Summarize the above in 2–3 short paragraphs for a board memo."
- **Option C:** "Based on the context, suggest 3–5 concrete next steps for the finance team (e.g. sensitivity runs, reporting, triggers to reassess)."

---

*End of context and prompt*
