#!/usr/bin/env python
# coding: utf-8

# # Robust Sovereignty Strategy (Ultra-CFO)
# ## Dynamic Programming + CVaR + Wasserstein (DRO) + time-varying ε(t)
# 
# This notebook provides a **board/CFO-ready toy model** for supplier dependency risk under:
# - **Tariff shock** (e.g., +100% cost) and unilateral pricing power
# - **Exit constraint**: needs **3 years** of progress (lock-in / migration)
# - **CAPEX (one-off)** vs **OPEX (recurring)**
# - **Exercise cost** (termination fee + cutover + recert/audit)
# - **Ambiguity** on transition probabilities via **Wasserstein ball ε(t)**
# - Objective: **worst-case CVaR** of **NPV cash** (or EBITDA)
# 
# Outputs:
# - Baseline vs ε(t) scenario
# - **Sovereignty premium** = V₀(ε(t)) − V₀(ε=0)
# - Slide-like plots

# In[ ]:


import numpy as np
import pandas as pd
import cvxpy as cp
import matplotlib.pyplot as plt
from itertools import product
from pydantic import BaseModel, Field, field_validator

np.set_printoptions(precision=3, suppress=True)


# ## 1) Model spec (Pydantic)
# 
# We model the firm as a **single strategic decision-maker** against **Nature** (political/regulatory environment).
# State includes:
# - tariff regime (0/1)
# - migration progress m ∈ {0..3}
# - flags for CAPEX already paid (invest, hedge setup)
# - exit exercised or not
# 
# This keeps the model Markovian and DP-solvable.

# In[ ]:


PlayerId = int
Action = int
State = int

class CFOConfig(BaseModel):
    wacc: float = Field(default=0.10, ge=0.0, le=0.5)          # discount rate
    amort_years: int = Field(default=5, ge=1, le=15)           # for reporting (toy)
    tax_rate: float = Field(default=0.25, ge=0.0, le=0.6)      # optional
    objective: str = Field(default="cash_npv", pattern="^(cash_npv|ebitda_npv)$")

class GameSpec(BaseModel):
    # horizon / actions
    horizon: int = 6
    exit_years: int = 3
    actions_per_player: int = 3  # 0=wait, 1=invest, 2=invest+hedge/exercise-if-ready

    # risk
    alpha_cvar: float = 0.9

    # tariff / dependency
    tariff_cost: float = 10.0
    hedged_tariff_cost: float = 6.0
    post_exit_cost: float = 1.0

    # CAPEX cash one-off
    capex_invest: float = 8.0
    capex_hedge_setup: float = 2.0

    # OPEX cash recurring
    opex_migration: float = 1.5
    opex_dual_run: float = 0.7

    # exercise costs (cash one-off)
    termination_fee: float = 12.0
    cutover_cost: float = 5.0
    recert_audit_cost: float = 2.0

    cfo: CFOConfig = CFOConfig()

class JointAction(BaseModel):
    actions: tuple[Action, ...]

    @field_validator("actions")
    @classmethod
    def non_empty(cls, v):
        if len(v) == 0:
            raise ValueError("Empty joint action")
        return v


# ## 2) State encoding
# 
# State dimensions:
# - tariff ∈ {0,1}
# - m ∈ {0..3}
# - inv ∈ {0,1}   (invest CAPEX already paid?)
# - hed ∈ {0,1}   (hedge setup CAPEX paid?)
# - ex  ∈ {0,1}   (exit exercised?)
# 
# Total: 2×4×2×2×2 = 64 states.

# In[ ]:


def encode_state(tariff: int, m: int, inv: int, hed: int, ex: int) -> int:
    return (((tariff * 4 + m) * 2 + inv) * 2 + hed) * 2 + ex

def decode_state(s: int):
    ex = s % 2; s //= 2
    hed = s % 2; s //= 2
    inv = s % 2; s //= 2
    m = s % 4;   s //= 4
    tariff = s
    return tariff, m, inv, hed, ex

N_STATES = 2 * 4 * 2 * 2 * 2  # 64


# ## 3) Wasserstein transport cost
# 
# We want ambiguity mainly on **tariff dynamics** (political).  
# We penalize moving probability mass across internal flags (m, inv, hed, ex) heavily.

# In[ ]:


def transport_cost_matrix():
    C = np.zeros((N_STATES, N_STATES))
    for i in range(N_STATES):
        ti, mi, invi, hedi, exi = decode_state(i)
        for j in range(N_STATES):
            tj, mj, invj, hedj, exj = decode_state(j)

            c_tar = 1.0 * abs(ti - tj)          # cheap to move across tariff
            c_m   = 10.0 * abs(mi - mj)         # expensive to move across progress
            c_inv = 50.0 * abs(invi - invj)     # very expensive across flags
            c_hed = 50.0 * abs(hedi - hedj)
            c_ex  = 50.0 * abs(exi - exj)

            C[i, j] = c_tar + c_m + c_inv + c_hed + c_ex
    return C


# ## 4) Nominal transition and time constraint
# 
# - Tariff follows a nominal 2-state Markov chain.
# - Progress `m` increases by 1 each period if action ∈ {1,2}, capped at `exit_years`.
# - Exit is exercised if action=2 and `m` reaches `exit_years`.

# In[ ]:


def nominal_tariff_transition(tariff: int) -> np.ndarray:
    # Toy nominal dynamics; replace with calibrated scenario / macro inputs
    if tariff == 0:
        return np.array([0.85, 0.15])  # switch into tariff
    return np.array([0.10, 0.90])      # persistence

def next_progress(m: int, action: int, exit_years: int) -> int:
    inc = 1 if action in (1, 2) else 0
    return min(exit_years, m + inc)

def build_p0_over_full_state(spec: GameSpec, s: int, action: int) -> np.ndarray:
    tariff, m, inv, hed, ex = decode_state(s)

    if ex == 1:
        m_next, inv_next, hed_next, ex_next = spec.exit_years, inv, hed, 1
    else:
        m_next = next_progress(m, action, spec.exit_years)
        inv_next = inv or (1 if action in (1,2) else 0)
        hed_next = hed or (1 if action == 2 else 0)
        ex_next = 1 if (action == 2 and m_next == spec.exit_years) else 0

    p_tar = nominal_tariff_transition(tariff)
    p0 = np.zeros(N_STATES)

    for tariff_next in (0, 1):
        s_next = encode_state(tariff_next, m_next, int(inv_next), int(hed_next), int(ex_next))
        p0[s_next] += p_tar[tariff_next]

    return p0


# ## 5) Cash vs EBITDA mapping (CFO)
# 
# We compute:
# - **cash** flow impact (CAPEX cash, OPEX cash, tariff cash, exercise cash)
# - **EBITDA** impact (toy): OPEX + tariff (exercise treated as exceptional by default)
# 
# Objective:
# - `cash_npv` (default): worst-case CVaR of discounted cash impact
# - `ebitda_npv`: same but on EBITDA proxy
# 
# Discounting uses WACC.

# In[ ]:


def discount_factor(spec: GameSpec, t: int) -> float:
    r = spec.cfo.wacc
    return 1.0 / ((1.0 + r) ** t)

def stage_losses_cfo(spec: GameSpec, s: int, action: int):
    tariff, m, inv, hed, ex = decode_state(s)

    # CAPEX cash one-off
    capex_cash = 0.0
    if inv == 0 and action in (1,2):
        capex_cash += spec.capex_invest
    if hed == 0 and action == 2:
        capex_cash += spec.capex_hedge_setup

    # OPEX recurring while migrating and investment started
    invest_started = (inv == 1) or (action in (1,2))
    opex_cash = 0.0
    if ex == 0 and invest_started and m < spec.exit_years:
        opex_cash += spec.opex_migration
        if tariff == 1:
            opex_cash += spec.opex_dual_run

    # Exercise costs
    exercise_cash = 0.0
    m_next = next_progress(m, action, spec.exit_years)
    will_exercise = (ex == 0 and action == 2 and m_next == spec.exit_years)
    if will_exercise:
        exercise_cash += spec.termination_fee + spec.cutover_cost + spec.recert_audit_cost

    # Tariff cash cost
    tariff_cash = 0.0
    if tariff == 1:
        if ex == 1:
            tariff_cash = spec.post_exit_cost
        else:
            if m < spec.exit_years:
                tariff_cash = spec.hedged_tariff_cost if action == 2 else spec.tariff_cost
            else:
                tariff_cash = spec.tariff_cost

    cash = capex_cash + opex_cash + exercise_cash + tariff_cash

    # EBITDA proxy: OPEX + tariff (exercise excluded by default)
    ebitda = opex_cash + tariff_cash
    ebit = ebitda  # keeping it minimal

    return cash, ebitda, ebit


# ## 6) Robust CVaR under Wasserstein ambiguity (LP)
# 
# We solve:
# 
# sup_{p : W(p,p0) ≤ ε} CVaR_α^p(loss)
# 
# using a discrete optimal transport formulation.

# In[ ]:


class RiskConfig(BaseModel):
    alpha: float = Field(..., gt=0, lt=1)
    wasserstein_eps: float = Field(..., ge=0)

class TransportCost(BaseModel):
    C: np.ndarray

class RobustCVaRWasserstein:
    def __init__(self, cfg: RiskConfig, cost: TransportCost):
        self.cfg = cfg
        self.C = cost.C

    def evaluate(self, p0: np.ndarray, losses: np.ndarray) -> float:
        n = len(losses)
        alpha = self.cfg.alpha
        eps = self.cfg.wasserstein_eps

        p = cp.Variable(n, nonneg=True)
        eta = cp.Variable()
        xi = cp.Variable(n, nonneg=True)
        T = cp.Variable((n, n), nonneg=True)

        constraints = [
            cp.sum(p) == 1,
            cp.sum(T, axis=1) == p0,          # from p0
            cp.sum(T, axis=0) == p,           # to p
            cp.sum(cp.multiply(self.C, T)) <= eps,
            xi >= losses - eta
        ]

        objective = cp.Minimize(
            eta + (1 / (1 - alpha)) * cp.sum(cp.multiply(p, xi))
        )

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)

        if problem.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(f"Robust CVaR failed: {problem.status}")

        return float(problem.value)


# ## 7) DP solver with time-varying ε(t)
# 
# Backward induction:
# - V[t,s] = min_a  sup_{p in Wasserstein ball} CVaR( discounted flow + V[t+1,s'] )
# 
# We compute both **value function** and **policy** (optimal action).

# In[ ]:


def dp_solve_cfo(spec: GameSpec, C: np.ndarray, eps_fn):
    A = spec.actions_per_player
    p = spec.horizon

    V = np.zeros((p + 1, N_STATES))
    pi = np.zeros((p, N_STATES), dtype=int)

    for t in reversed(range(p)):
        eps_t = float(eps_fn(t, p))
        risk_eval = RobustCVaRWasserstein(
            RiskConfig(alpha=spec.alpha_cvar, wasserstein_eps=eps_t),
            TransportCost(C=C)
        )
        disc = discount_factor(spec, t)

        for s in range(N_STATES):
            vals = []
            for a in range(A):
                p0 = build_p0_over_full_state(spec, s, a)

                losses = np.zeros(N_STATES)
                for sp in range(N_STATES):
                    cash, ebitda, _ = stage_losses_cfo(spec, s, a)
                    flow = cash if spec.cfo.objective == "cash_npv" else ebitda
                    losses[sp] = disc * flow + V[t+1, sp]

                vals.append(risk_eval.evaluate(p0, losses))

            vals = np.array(vals)
            best = int(vals.argmin())
            pi[t, s] = best
            V[t, s] = vals[best]

    return V, pi


# ## 8) ε(t) from a risk indicator
# 
# We use a CFO-friendly approach:
# - Define an indicator R(t) ∈ [0,1]
# - Map it to ε(t) in [ε_min, ε_max]

# In[ ]:


def risk_indicator(t, horizon):
    # toy: cycle (0 -> 1 -> 0)
    x = t / max(1, horizon-1)
    return float(4*x*(1-x))

def eps_from_risk(R, eps_min=0.02, eps_max=0.30):
    return eps_min + (eps_max - eps_min) * R

def eps_schedule_indicator(t, horizon):
    return eps_from_risk(risk_indicator(t, horizon))


# ## 9) Run: baseline vs ε(t) scenario + sovereignty premium

# In[ ]:


spec = GameSpec(horizon=6, cfo=CFOConfig(wacc=0.10, amort_years=5, objective="cash_npv"))

C = transport_cost_matrix()
s0 = encode_state(tariff=0, m=0, inv=0, hed=0, ex=0)

V_base, pi_base = dp_solve_cfo(spec, C, eps_fn=lambda t,h: 0.0)
V_scn,  pi_scn  = dp_solve_cfo(spec, C, eps_fn=eps_schedule_indicator)

V0_base = V_base[0, s0]
V0_scn  = V_scn[0, s0]
premium = V0_scn - V0_base

summary = pd.DataFrame([{
    "objective": spec.cfo.objective,
    "WACC": spec.cfo.wacc,
    "V0_baseline_eps0": V0_base,
    "V0_eps(t)": V0_scn,
    "sovereignty_premium": premium,
    "a0_baseline": int(pi_base[0, s0]),
    "a0_eps(t)": int(pi_scn[0, s0]),
}])

summary


# ## 10) Slide-like outputs
# ### Slide A — Risk environment (R(t), ε(t))

# In[ ]:


eps_vals = [eps_schedule_indicator(t, spec.horizon) for t in range(spec.horizon)]
R_vals = [risk_indicator(t, spec.horizon) for t in range(spec.horizon)]

plt.figure(figsize=(8,4))
plt.plot(range(spec.horizon), R_vals, marker="o", label="Risk indicator R(t)")
plt.plot(range(spec.horizon), eps_vals, marker="o", label="Ambiguity ε(t)")
plt.title("Political / Regulatory Risk Environment")
plt.xlabel("Time")
plt.ylabel("Level")
plt.grid(True)
plt.legend()
plt.show()


# ### Slide B — Robust NPV impact (baseline vs ε(t))

# In[ ]:


plt.figure(figsize=(8,4))
plt.plot(range(spec.horizon), V_base[:-1, s0], marker="o", label="Baseline (ε=0)")
plt.plot(range(spec.horizon), V_scn[:-1, s0], marker="o", label="Scenario ε(t)")
plt.title("Worst-case NPV (CVaR 90%) — From Initial Position")
plt.xlabel("Time")
plt.ylabel("NPV cash impact")
plt.grid(True)
plt.legend()
plt.show()


# ### Slide C — Sovereignty premium

# In[ ]:


plt.figure(figsize=(6,4))
plt.bar(["Sovereignty premium"], [premium])
plt.title("Sovereignty Premium (Worst-case NPV)")
plt.ylabel("€ impact (NPV cash)")
plt.grid(True, axis="y")
plt.show()


# ### Slide D — Rollout (mode nominal) to explain the policy
# 
# We follow the most likely next state under the nominal transition (for illustration).

# In[ ]:


def rollout_policy_mode(spec: GameSpec, pi, start_state: int):
    s = start_state
    out = []
    for t in range(spec.horizon):
        a = int(pi[t, s])
        cash, ebitda, ebit = stage_losses_cfo(spec, s, a)
        p0 = build_p0_over_full_state(spec, s, a)
        sp = int(np.argmax(p0))  # nominal mode
        out.append((t, s, a, cash, ebitda, ebit, sp))
        s = sp
    return out

roll = rollout_policy_mode(spec, pi_scn, s0)

rows = []
for t, s, a, cash, ebitda, ebit, sp in roll:
    tariff, m, inv, hed, ex = decode_state(s)
    tariff2, m2, inv2, hed2, ex2 = decode_state(sp)
    rows.append({
        "t": t,
        "state": f"tariff={tariff}, m={m}, inv={inv}, hed={hed}, ex={ex}",
        "action": ["wait","invest","invest+hedge/exercise"][a],
        "cash": cash,
        "disc": discount_factor(spec, t),
        "next_state(mode)": f"tariff={tariff2}, m={m2}, inv={inv2}, hed={hed2}, ex={ex2}",
    })

pd.DataFrame(rows)

