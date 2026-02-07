# Step 6 -- Code Walkthrough: Reading the Notebook

## Learning Objectives

By the end of this step, you will:

- Know the structure of the Jupyter notebook and how its sections map to concepts
- Understand the key classes (`CFOConfig`, `GameSpec`, `RiskConfig`, `TransportCost`, `RobustCVaRWasserstein`)
- Be able to read and explain the key functions (`encode_state`, `build_p0_over_full_state`, `stage_losses_cfo`, `dp_solve_cfo`)
- Understand how the Wasserstein DRO inner problem is solved using CVXPY
- Know the dependencies and how to run the notebook

---

## Notebook Structure

The entire implementation lives in a single Jupyter notebook: `sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb`. It is organized in numbered sections:

| Section | Title | What It Contains |
|:-------:|-------|-----------------|
| Intro | Header + Glossary | Context, reading guide, glossary of key terms |
| 1 | Model spec | `CFOConfig` and `GameSpec` class definitions |
| 2 | State encoding | `encode_state()`, `decode_state()`, `N_STATES = 64` |
| 3 | Wasserstein transport cost | `transport_cost_matrix()` function |
| 4 | Nominal transition | `nominal_tariff_transition()`, `build_p0_over_full_state()` |
| 5 | Cash vs EBITDA mapping | `stage_losses_cfo()`, `hedge_effectiveness_factor()` |
| 6 | Robust CVaR (LP) | `RiskConfig`, `TransportCost`, `RobustCVaRWasserstein` class |
| 7 | DP solver | `cvar_discrete_worst_tail()`, `dp_solve_cfo()` |
| 8 | Epsilon schedule | `risk_indicator()`, `eps_from_risk()`, `eps_schedule_*()` |
| 9 | Main results | Runs the four scenarios, prints comparison table |
| 10 | Sensitivity analysis | Horizon and tariff persistence sweeps |
| 11 | CFO interpretation | Business language summary of results |
| 12 | Visualizations | Policy maps, value function heatmaps, charts |

**Reading strategy:** If you are a quant, read sections 1-8 in order. If you are a business user, skip to sections 9, 11, and 12.

---

## Key Classes

### `CFOConfig` -- Financial Parameters

```python
class CFOConfig(BaseModel):
    wacc: float = 0.10           # Weighted Average Cost of Capital (discount rate)
    amort_years: int = 5         # Amortization period for reporting
    tax_rate: float = 0.25       # Corporate tax rate
    objective: str = "cash_npv"  # "cash_npv" or "ebitda_npv"
```

This class captures the financial lens. The `objective` field determines whether the model minimizes cash NPV (treasury perspective) or EBITDA NPV (P&L perspective). In practice, a CFO might run both and compare.

### `GameSpec` -- Game Parameters

```python
class GameSpec(BaseModel):
    horizon: int = 10                 # Planning horizon (years)
    exit_years: int = 3               # Years to complete migration
    actions_per_player: int = 5       # Number of actions
    alpha_cvar: float = 0.9           # CVaR level (0.9 = worst 10%)

    # Tariff Markov chain
    tariff_p01: float = 0.15          # P(tariff turns on)
    tariff_p10: float = 0.10          # P(tariff turns off)

    # Costs (abstract units)
    tariff_cost: float = 10.0         # Full tariff exposure per period
    hedged_tariff_cost: float = 6.0   # Reduced exposure with hedge
    post_exit_cost: float = 0.0       # Residual cost post-exit
    capex_invest: float = 8.0         # One-time migration CAPEX
    capex_hedge_setup: float = 2.0    # One-time hedge setup
    opex_migration: float = 1.5       # Recurring migration OPEX
    opex_dual_run: float = 0.7        # Extra OPEX when dual-running under tariff
    termination_fee: float = 12.0     # Exit termination fee
    cutover_cost: float = 5.0         # Exit cutover cost
    recert_audit_cost: float = 2.0    # Exit recertification cost

    cfo: CFOConfig = CFOConfig()
```

This is the central configuration object. Every cost parameter, transition probability, and structural choice is defined here. To run a different scenario, you create a new `GameSpec` with different values.

### `RiskConfig` and `TransportCost` -- Risk Parameters

```python
class RiskConfig(BaseModel):
    alpha: float       # CVaR level (e.g. 0.9)
    wasserstein_eps: float  # Wasserstein ball radius

class TransportCost(BaseModel):
    C: np.ndarray      # 64x64 transport cost matrix
```

These are passed to the `RobustCVaRWasserstein` class. They are separate from `GameSpec` because they change at each time step ($\varepsilon(t)$ varies).

### `RobustCVaRWasserstein` -- The Core Optimization Engine

```python
class RobustCVaRWasserstein:
    def __init__(self, cfg: RiskConfig, cost: TransportCost):
        self.cfg = cfg
        self.C = cost.C

    def evaluate(self, p0: np.ndarray, losses: np.ndarray) -> float:
        """Solve: sup_{p: W_C(p,p0) <= eps} CVaR_alpha^p(losses)"""
        # ... sets up and solves a CVXPY linear program ...
```

This class encapsulates the Wasserstein DRO inner problem. Given a nominal distribution `p0` and a loss vector `losses`, it finds the worst-case CVaR by solving a convex program.

---

## Key Functions

### State Encoding

```python
def encode_state(tariff: int, m: int, inv: int, hed: int, ex: int) -> int:
    return (((tariff * 4 + m) * 2 + inv) * 2 + hed) * 2 + ex

def decode_state(s: int):
    ex = s % 2;  s //= 2
    hed = s % 2; s //= 2
    inv = s % 2; s //= 2
    m = s % 4;   s //= 4
    tariff = s
    return tariff, m, inv, hed, ex
```

These convert between the tuple representation $(\tau, m, i, h, e)$ and a single integer index $\{0, \ldots, 63\}$. The encoding uses mixed-radix arithmetic:

- `tariff` occupies the highest bits (x32)
- `m` occupies the next 2 bits (x8, values 0-3)
- `inv`, `hed`, `ex` each occupy 1 bit (x4, x2, x1)

### Transition Kernel

```python
def build_p0_over_full_state(spec, s, action):
    tariff, m, inv, hed, ex = decode_state(s)

    # Compute next state for flags and progress (deterministic)
    m_next = next_progress(spec, m, action)
    inv_next = inv or (action in {INVEST, ACCELERATE, INVEST_HEDGE_EXERCISE})
    hed_next = hed or (action in {HEDGE_ONLY, INVEST_HEDGE_EXERCISE})
    ex_next = 1 if (action == INVEST_HEDGE_EXERCISE and m_next == exit_years) else 0

    # Stochastic: tariff transition
    p_tar = nominal_tariff_transition(spec, tariff)  # [P(tar=0), P(tar=1)]

    p0 = np.zeros(N_STATES)  # 64-dimensional probability vector
    for tariff_next in (0, 1):
        s_next = encode_state(tariff_next, m_next, inv_next, hed_next, ex_next)
        p0[s_next] = p_tar[tariff_next]

    return p0
```

This function builds the full 64-dimensional transition probability vector. Note that only **2 entries** are nonzero (corresponding to tariff on/off in the next period), because all other state updates are deterministic.

**Key insight:** The sparse structure (only 2 nonzero entries) means that for most state-action pairs, the "distribution" that Nature can distort is very simple. The Wasserstein ball allows Nature to shift probability between these two outcomes (and potentially to other states, depending on the transport cost).

### Loss Function

```python
def stage_losses_cfo(spec, t, s, action):
    tariff, m, inv, hed, ex = decode_state(s)

    # CAPEX: one-time costs when starting programs
    capex_cash = 0.0
    if inv == 0 and action in {INVEST, ACCELERATE, INVEST_HEDGE_EXERCISE}:
        capex_cash += spec.capex_invest       # 8.0
    if hed == 0 and action in {HEDGE_ONLY, INVEST_HEDGE_EXERCISE}:
        capex_cash += spec.capex_hedge_setup  # 2.0

    # OPEX: recurring costs during migration
    opex_cash = 0.0
    if ex == 0 and invest_started and m < exit_years:
        opex_cash += spec.opex_migration      # 1.5
        if tariff == 1:
            opex_cash += spec.opex_dual_run   # 0.7

    # Exit costs: one-time when exercising
    exercise_cash = 0.0
    if will_exercise:
        exercise_cash = exit_cost_at_t(spec, t)  # ~19.0

    # Tariff cost: with progressive hedge effectiveness
    hedge_factor = hedge_effectiveness_factor(spec, m, hed, action)
    tariff_cash = (1 - hedge_factor) * tariff_cost + hedge_factor * hedged_tariff_cost

    return cash, ebitda, ebit
```

(Simplified for readability -- the actual code has more detail.)

The function returns three values: cash cost, EBITDA impact, and EBIT. The solver uses whichever the `CFOConfig.objective` specifies.

### The DP Solver

```python
def dp_solve_cfo(spec, C, eps_fn, log_lp_timing=True):
    V = np.zeros((horizon + 1, N_STATES))    # Value function: (T+1) x 64
    pi = np.zeros((horizon, N_STATES), int)   # Policy: T x 64

    for t in reversed(range(horizon)):        # Backward in time
        eps_t = eps_fn(t, horizon)            # Time-varying ambiguity
        disc = discount_factor(spec, t)       # WACC discounting

        # Set up Wasserstein solver for this period
        if eps_t > 0:
            risk_eval = RobustCVaRWasserstein(
                RiskConfig(alpha=alpha_cvar, wasserstein_eps=eps_t),
                TransportCost(C=C)
            )

        for s in range(N_STATES):             # For each state
            vals = []
            for a in range(5):                # Try each action
                p0 = build_p0_over_full_state(spec, s, a)
                flow = stage_losses_cfo(spec, t, s, a)[0]  # cash
                losses = disc * flow + V[t + 1, :]  # immediate + future

                if eps_t <= 0:
                    val = cvar_discrete_worst_tail(p0, losses, alpha)
                else:
                    val = risk_eval.evaluate(p0, losses)

                vals.append(val)

            pi[t, s] = argmin(vals)           # Optimal action
            V[t, s] = min(vals)               # Optimal value

    return V, pi
```

This is the heart of the model. Let us trace the logic:

1. **Outer loop** (`t` from $T-1$ to $0$): backward induction over time
2. **Middle loop** (`s` from $0$ to $63$): iterate over all states
3. **Inner loop** (`a` from $0$ to $4$): try each of the 5 actions
4. For each (t, s, a):
   - Build the nominal transition vector `p0` (64-dimensional, only 2 nonzero entries)
   - Compute the loss vector: discounted immediate cost plus future value function
   - If $\varepsilon_t > 0$: solve the Wasserstein DRO problem (LP via CVXPY)
   - If $\varepsilon_t = 0$: compute standard CVaR (fast, no LP needed)
5. Pick the action with the smallest robust CVaR value

**Output:** Two matrices:
- `V[t, s]`: the robust worst-case cost-to-go from state $s$ at time $t$
- `pi[t, s]`: the optimal action index at state $s$ at time $t$

### The Wasserstein LP Inner Problem

When `eps_t > 0`, the `RobustCVaRWasserstein.evaluate()` method solves:

$$\inf_{\eta, \lambda \geq 0, u} \left\{ \eta + \lambda \varepsilon + p_0^\top u \right\}$$

Subject to:

$$u_i + \lambda C_{ij} \geq \frac{1}{1-\alpha}(L_j - \eta)^+ \quad \forall i, j$$

Where:
- $\eta$ is the VaR threshold
- $\lambda$ is the Wasserstein dual multiplier (price of transport)
- $u$ is the vector of dual potentials
- $C_{ij}$ is the transport cost between states $i$ and $j$
- $L_j$ is the loss at state $j$

This is formulated as a CVXPY problem and solved with **CLARABEL** (a modern Rust-based conic solver) with SCS as fallback. Each solve takes about 10-50ms.

**Why LP duality?** The original problem is a semi-infinite optimization (Nature chooses from infinitely many distributions). The LP dual reformulation turns it into a finite-dimensional problem with $O(n^2)$ constraints (where $n = 64$ states). This is tractable on a laptop.

---

## Epsilon Schedules

The time-varying ambiguity is defined by schedule functions:

```python
def risk_indicator(t, horizon):
    """Toy cyclical risk indicator: peaks at mid-horizon."""
    x = t / max(1, horizon - 1)
    return float(4 * x * (1 - x))   # parabola: 0 -> 1 -> 0

def eps_from_risk(R, eps_min=0.02, eps_max=0.30):
    """Map risk indicator [0,1] to epsilon [eps_min, eps_max]."""
    return eps_min + (eps_max - eps_min) * R
```

Three schedules are provided:

| Schedule | Description | Use Case |
|----------|-------------|----------|
| `eps_schedule_indicator` | Standard cyclical, $\varepsilon \in [0.02, 0.30]$ | Baseline with uncertainty |
| `eps_schedule_volatile` | Same cycle but $\varepsilon_{\max} = 0.40$ | High-uncertainty environment |
| `eps_schedule_macro` | Spikes at $t=1$ and $t=3$ | Specific macro events (elections, negotiations) |

The baseline scenario uses `eps_fn = lambda t, h: 0.0` (no ambiguity, pure CVaR).

---

## Dependencies

The notebook requires these Python packages:

| Package | Purpose | Version |
|---------|---------|---------|
| `numpy` | Numerical arrays and linear algebra | Any recent |
| `pandas` | Data tables for results display | Any recent |
| `cvxpy` | Convex optimization (Wasserstein LP) | >= 1.3 |
| `matplotlib` | Plotting and visualization | Any recent |
| `pydantic` | Type-safe model configuration | v2.x |
| `tqdm` | Progress bars for the solver | Any recent |

**Solvers (installed with CVXPY):**
- **CLARABEL**: Primary solver. Modern, Rust-based, numerically stable.
- **SCS**: Fallback solver. Splitting Conic Solver, used if CLARABEL fails.

### Running the Notebook

```bash
# Install dependencies
pip install numpy pandas cvxpy matplotlib pydantic tqdm

# Launch Jupyter
jupyter notebook sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb
```

Run all cells in order. The main computation (four DP solves) takes 2-5 minutes depending on your hardware. Progress bars show the status.

---

## How the Outputs Look

After running the solver, the notebook produces:

1. **Comparison table**: V0 (worst-case cost) for each scenario, with sovereignty premium
2. **Policy matrices**: For each scenario, a table showing $\pi^*(t, s)$ -- what action to take in each state at each time
3. **Value function heatmaps**: Visualizing $V_t(s)$ across states and time
4. **Sensitivity plots**: How results change with horizon and tariff persistence
5. **Epsilon schedule plots**: Visualizing $R(t)$ and $\varepsilon(t)$ over time

The CFO interpretation section (Section 11) translates these technical outputs into business language.

---

## Connection to the Repository

Everything described in this step lives in the single notebook file:

- **Classes**: Cells under Sections 1 and 6
- **State encoding**: Section 2
- **Transport cost**: Section 3
- **Transitions**: Section 4
- **Losses**: Section 5
- **Solver**: Section 7
- **Schedules**: Section 8
- **Results**: Sections 9-12

The file `LLM_context_prompt.md` provides a structured context for generating executive summaries of the results using an LLM.

---

## Validation Quiz

### Questions

**Q1.** Match each class to its purpose:

| Class | Purpose |
|-------|---------|
| A. `CFOConfig` | 1. Defines the transport cost for Wasserstein distance |
| B. `GameSpec` | 2. Holds financial parameters (WACC, tax rate, objective) |
| C. `RiskConfig` | 3. Solves the robust CVaR under Wasserstein ambiguity |
| D. `TransportCost` | 4. Defines all game parameters (horizon, costs, transitions) |
| E. `RobustCVaRWasserstein` | 5. Holds CVaR level and Wasserstein radius |

**Q2.** In the `dp_solve_cfo()` function, what are the three nested loops (from outer to inner), and what does each iterate over?

**Q3.** The `build_p0_over_full_state()` function returns a 64-dimensional probability vector, but only 2 entries are nonzero. Why?

**Q4.** What happens in `dp_solve_cfo()` when `eps_t = 0`? How does this differ from when `eps_t > 0`?

**Q5.** The `transport_cost_matrix()` function assigns cost 1.0 for moving across tariff states but cost 50.0 for moving across flag states ($i$, $h$, $e$). Explain why this asymmetry is intentional.

**Q6.** Which solver does the `RobustCVaRWasserstein` class try first? What happens if it fails?

**Q7.** How would you modify the notebook to run a scenario with a 15-year horizon and tariff persistence of $p_{10} = 0.05$ (very sticky tariffs)?

**Q8.** True or False: The notebook requires a GPU to run in reasonable time.

---

### Answers

**A1.**
- A-2: `CFOConfig` holds financial parameters (WACC, tax rate, objective)
- B-4: `GameSpec` defines all game parameters (horizon, costs, transitions)
- C-5: `RiskConfig` holds CVaR level alpha and Wasserstein radius epsilon
- D-1: `TransportCost` defines the transport cost matrix for Wasserstein distance
- E-3: `RobustCVaRWasserstein` solves the robust CVaR under Wasserstein ambiguity

**A2.** The three loops are:
1. **Outer: time** (`for t in reversed(range(horizon))`) -- iterates backward from $T-1$ to $0$
2. **Middle: states** (`for s in range(N_STATES)`) -- iterates over all 64 states
3. **Inner: actions** (`for a in range(5)`) -- tries each of the 5 possible actions

For each (t, s, a) combination, the function computes the robust CVaR value, then picks the best action for that state at that time.

**A3.** Because the transition dynamics have only one stochastic component: the tariff regime. Given a state and action, the migration progress, investment flag, hedge flag, and exit flag all update **deterministically**. Only the tariff can be 0 or 1 in the next period (with probabilities from the Markov chain). So only 2 next states have nonzero probability.

**A4.**
- **When `eps_t = 0`:** No Wasserstein ambiguity. The function calls `cvar_discrete_worst_tail(p0, losses, alpha)`, which computes standard CVaR under the nominal distribution `p0`. This is fast (no LP solve needed, just sorting and weighted averaging).
- **When `eps_t > 0`:** Wasserstein ambiguity is active. The function calls `risk_eval.evaluate(p0, losses)`, which solves a convex LP via CVXPY to find the worst-case CVaR within the Wasserstein ball. This is slower (~10-50ms per solve) but provides robustness against distributional shifts.

The baseline scenario uses `eps_t = 0` throughout, giving standard CVaR results. The other scenarios use time-varying `eps_t > 0`.

**A5.** The asymmetry reflects which dimensions are **genuinely uncertain**:
- **Tariff regime** (cost = 1.0): Controlled by governments, inherently uncertain. The firm cannot predict political decisions, so Nature should be able to shift tariff probabilities easily. Low transport cost gives Nature freedom here.
- **Flags** (cost = 50.0): Controlled by the firm itself. Whether the firm has invested, hedged, or exited is a known fact, not subject to uncertainty. High transport cost prevents Nature from "pretending" the firm has not invested when it has, which would be unrealistic.

This ensures the Wasserstein adversary perturbs the **right** dimensions -- political risk, not the firm's own decisions.

**A6.** The class tries **CLARABEL** first (a modern, Rust-based conic solver with excellent numerical stability). If CLARABEL raises a `SolverError`, it falls back to **SCS** (Splitting Conic Solver) with increased precision (`eps=1e-8`) and iteration limit (`max_iters=25000`). This two-tier approach provides both speed (CLARABEL is fast) and robustness (SCS handles edge cases).

**A7.** Create a modified `GameSpec`:

```python
spec_custom = GameSpec(
    horizon=15,          # Changed from 10 to 15
    tariff_p10=0.05,     # Changed from 0.10 to 0.05 (stickier tariffs)
    # ... all other parameters inherit defaults
)
```

Then run `dp_solve_cfo(spec_custom, C, eps_fn=your_schedule)`. The solver will compute over $15 \times 64 \times 5 = 4{,}800$ subproblems instead of 3,200. Runtime will increase proportionally (roughly 50% longer).

**A8.** **False.** The notebook runs entirely on CPU. The computations are linear programs (CVXPY + CLARABEL/SCS), which are CPU-based. The entire solve (four scenarios) takes 2-5 minutes on a standard laptop. No GPU is needed.

---

**Previous step:** [05 -- The Model](05_the_model.md)
**Next step:** [07 -- Results and Interpretation](07_results_and_interpretation.md)
