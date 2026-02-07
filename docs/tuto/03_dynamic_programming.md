# Step 3 -- Dynamic Programming and Backward Induction

## Learning Objectives

By the end of this step, you will:

- Understand why brute-force enumeration of strategies is intractable
- Know Bellman's optimality principle and why it works
- Be able to write and interpret the Bellman equation
- Solve a small dynamic programming problem by hand using backward induction
- Understand the difference between a value function and a policy
- Connect the discount factor to WACC (Weighted Average Cost of Capital)

---

## The Curse of Dimensionality

Consider our sovereignty model: 5 possible actions, 10 time periods. If you tried to enumerate every possible sequence of actions, you would have:

$$5^{10} = 9{,}765{,}625 \approx 10 \text{ million action sequences}$$

And for each sequence, you would need to evaluate it against all possible tariff trajectories (Nature's moves). With 2 tariff states per period, that is $2^{10} = 1{,}024$ possible tariff paths. Total combinations: about **10 billion** evaluations.

This is already intractable for a toy model with 64 states. For a realistic model with hundreds of states, it becomes astronomically impossible. This exponential explosion is what Richard Bellman called the **"curse of dimensionality."**

Dynamic programming is the cure.

---

## Bellman's Optimality Principle

**Richard Bellman** (1920-1984) developed dynamic programming in the 1950s. His central insight is captured in the **principle of optimality**:

> *"An optimal policy has the property that whatever the initial state and initial decision are, the remaining decisions must constitute an optimal policy with regard to the state resulting from the first decision."*

In simpler terms: **if you are on the best path overall, then from any point along that path, the remaining path must also be the best.** There is no benefit to "going off-script" halfway through.

**Why this helps computationally:** Instead of evaluating entire sequences of decisions, you can break the problem into stages. At each stage, you only need to find the best action for the current state, assuming you will behave optimally in the future. This turns an exponential problem into a polynomial one.

**Analogy:** Imagine planning a road trip from Paris to Rome. You do not need to evaluate every possible combination of roads for the entire journey. If you know the best route from Lyon to Rome, then the problem from Paris reduces to: "What is the best way to get from Paris to Lyon?" and then use the already-known best route from Lyon onward. Bellman's principle says this decomposition always works for optimal paths.

---

## The Bellman Equation

### Standard Form

For a finite-horizon problem with $T$ periods, the **Bellman equation** is:

$$V_t(s) = \min_{a \in \mathcal{A}} \left[ \ell(s, a) + \gamma \sum_{s'} p(s' | s, a) \cdot V_{t+1}(s') \right]$$

Let us unpack each term:

| Symbol | Meaning |
|--------|---------|
| $V_t(s)$ | **Value function**: the minimum total cost from state $s$ at time $t$ to the end of the horizon, following the optimal policy |
| $\min_{a \in \mathcal{A}}$ | The firm chooses the action $a$ that minimizes cost |
| $\ell(s, a)$ | **Stage cost**: the immediate cost of taking action $a$ in state $s$ |
| $\gamma$ | **Discount factor**: $\gamma = 1/(1 + r)$ where $r$ is the discount rate |
| $p(s' \mid s, a)$ | **Transition probability**: chance of moving to state $s'$ given current state $s$ and action $a$ |
| $V_{t+1}(s')$ | **Future value**: minimum cost-to-go from the next state (already computed) |

### Terminal Condition

At the final period $T$, there are no more decisions to make:

$$V_T(s) = 0 \quad \text{for all states } s$$

(Or a terminal cost function if there is a salvage value or penalty.)

### The Optimal Policy

Once you have $V_t(s)$ for all states and times, the **optimal policy** is:

$$\pi^*(t, s) = \arg\min_{a \in \mathcal{A}} \left[ \ell(s, a) + \gamma \sum_{s'} p(s' | s, a) \cdot V_{t+1}(s') \right]$$

This tells you the best action in every state at every time. It is a **complete contingency plan**.

---

## Worked Example: A Tiny DP Problem

Let us solve a problem small enough to do by hand, using the same logic as the sovereignty model.

### Setup

**A firm faces a 3-year planning horizon.** At each year, it can either **Wait** (cost = 0 if no tariff, cost = 5 if tariff) or **Exit** (one-time cost = 8, then no more tariff costs forever).

**Tariff dynamics:** If tariff is OFF, it turns ON next year with probability 0.3. If tariff is ON, it stays ON with probability 0.7.

**States:** $s \in \{\text{OFF}, \text{ON}, \text{EXITED}\}$

**Discount factor:** $\gamma = 1.0$ (no discounting, to keep the math simple)

### Step 1: Terminal Values ($t = 3$)

$$V_3(\text{OFF}) = 0, \quad V_3(\text{ON}) = 0, \quad V_3(\text{EXITED}) = 0$$

No more costs after the horizon ends.

### Step 2: Solve $t = 2$ (one period remaining)

**State = OFF:**
- Wait: cost = 0 + [0.7 x V_3(OFF) + 0.3 x V_3(ON)] = 0 + 0 = 0
- Exit: cost = 8 + V_3(EXITED) = 8

Best: **Wait**, $V_2(\text{OFF}) = 0$

**State = ON:**
- Wait: cost = 5 + [0.3 x V_3(OFF) + 0.7 x V_3(ON)] = 5 + 0 = 5
- Exit: cost = 8 + V_3(EXITED) = 8

Best: **Wait**, $V_2(\text{ON}) = 5$

**State = EXITED:**
- No choice needed: $V_2(\text{EXITED}) = 0$

### Step 3: Solve $t = 1$ (two periods remaining)

**State = OFF:**
- Wait: cost = 0 + [0.7 x V_2(OFF) + 0.3 x V_2(ON)] = 0 + 0.7(0) + 0.3(5) = 1.5
- Exit: cost = 8 + V_2(EXITED) = 8 + 0 = 8

Best: **Wait**, $V_1(\text{OFF}) = 1.5$

**State = ON:**
- Wait: cost = 5 + [0.3 x V_2(OFF) + 0.7 x V_2(ON)] = 5 + 0.3(0) + 0.7(5) = 5 + 3.5 = 8.5
- Exit: cost = 8 + V_2(EXITED) = 8 + 0 = 8

Best: **Exit**, $V_1(\text{ON}) = 8$

**State = EXITED:** $V_1(\text{EXITED}) = 0$

### Step 4: Solve $t = 0$ (three periods remaining)

**State = OFF:**
- Wait: cost = 0 + [0.7 x V_1(OFF) + 0.3 x V_1(ON)] = 0 + 0.7(1.5) + 0.3(8) = 1.05 + 2.4 = 3.45
- Exit: cost = 8 + V_1(EXITED) = 8

Best: **Wait**, $V_0(\text{OFF}) = 3.45$

**State = ON:**
- Wait: cost = 5 + [0.3 x V_1(OFF) + 0.3 x V_1(ON)] -- wait, let us be careful with the transition.

Actually, let us re-check. If tariff is ON: probability 0.3 it turns OFF, probability 0.7 it stays ON.

- Wait: cost = 5 + [0.3 x V_1(OFF) + 0.7 x V_1(ON)] = 5 + 0.3(1.5) + 0.7(8) = 5 + 0.45 + 5.6 = 11.05
- Exit: cost = 8 + V_1(EXITED) = 8

Best: **Exit**, $V_0(\text{ON}) = 8$

### Summary of Optimal Policy

| Time | State OFF | State ON | State EXITED |
|:----:|:---------:|:--------:|:------------:|
| $t=0$ | Wait (3.45) | Exit (8.00) | -- (0) |
| $t=1$ | Wait (1.50) | Exit (8.00) | -- (0) |
| $t=2$ | Wait (0.00) | Wait (5.00) | -- (0) |

**The policy says:**
- If tariff is OFF: always wait (do not pay the exit cost when you do not need to)
- If tariff is ON at $t=0$ or $t=1$: exit immediately (because the expected future tariff cost exceeds the exit cost)
- If tariff is ON at $t=2$: just wait (only one period left, paying 5 is less than exit cost of 8)

This is a **state-contingent policy** -- different actions for different situations, adapting over time. Exactly what the sovereignty model produces, just on a much larger scale.

### Computational Savings

- Brute force: $2^3 \times 3 = 24$ paths to evaluate for each of $2^3 = 8$ action sequences = 192 evaluations
- Dynamic programming: 3 states x 3 time periods x 2 actions = **18 evaluations**

For the real model (64 states, 10 periods, 5 actions): brute force needs $\sim 10^{10}$ evaluations. DP needs $64 \times 10 \times 5 = 3{,}200$ subproblems. That is a speedup factor of **three million**.

---

## The Discount Factor and WACC

In the sovereignty model, future costs are discounted using the **WACC (Weighted Average Cost of Capital)**:

$$\gamma_t = \frac{1}{(1 + r)^t}$$

Where $r$ is the WACC (default: 10% in the model).

**What this means:** A cost of 10 units incurred 5 years from now is worth $10 / (1.10)^5 = 6.21$ units in today's terms.

**Why discount?** Money has a time value. A euro today can be invested and grow. So a cost far in the future is less burdensome than the same cost today. The WACC reflects the firm's cost of capital -- the minimum return shareholders and creditors expect.

**Impact on the model:** Higher WACC means future costs matter less, which makes waiting more attractive (since the future tariff costs are discounted away). Lower WACC makes future costs more important, which can push toward earlier action.

In the Bellman equation, the discount factor appears as:

$$V_t(s) = \min_{a} \left[ \gamma_t \cdot \ell(s, a) + \sum_{s'} p(s' | s, a) \cdot V_{t+1}(s') \right]$$

Note that $V_{t+1}$ already incorporates future discounting, so the recursion correctly chains the discounts.

---

## From Standard DP to Our Model

The standard Bellman equation is:

$$V_t(s) = \min_{a} \mathbb{E}_{p_0}\left[\gamma_t \ell(s,a) + V_{t+1}(S')\right]$$

Our model adds two layers of sophistication:

**Layer 1 -- CVaR (risk aversion):** Replace the expectation $\mathbb{E}$ with $\text{CVaR}_\alpha$:

$$V_t(s) = \min_{a} \text{CVaR}_\alpha^{p_0}\left[\gamma_t \ell(s,a) + V_{t+1}(S')\right]$$

This focuses on the tail of the distribution (worst outcomes) rather than the average.

**Layer 2 -- Wasserstein DRO (ambiguity aversion):** Allow Nature to choose the worst distribution within a ball:

$$V_t(s) = \min_{a} \sup_{p \in \mathcal{P}_\varepsilon(p_0)} \text{CVaR}_\alpha^p\left[\gamma_t \ell(s,a) + V_{t+1}(S')\right]$$

This protects against the forecast itself being wrong.

We will cover CVaR and Wasserstein in detail in Step 04. The key point for now: **the Bellman structure (backward induction, optimal substructure) is preserved.** The DP machinery works the same way regardless of whether you use expected value, CVaR, or robust CVaR -- only the inner computation at each step changes.

---

## How This Maps to the Code

In the notebook, the function `dp_solve_cfo()` implements backward induction:

```python
# Pseudocode of the solver loop
for t in reversed(range(T)):       # backward in time
    for s in range(N_STATES):      # for each state
        for a in range(N_ACTIONS): # try each action
            p0 = transition_kernel(spec, s, a)
            losses = discount(t) * stage_loss(spec, t, s, a) + V[t+1, :]

            if eps_t > 0:
                val = robust_cvar_wasserstein(p0, losses, eps_t, alpha, C)
            else:
                val = cvar_discrete(p0, losses, alpha)

            values.append(val)

        pi[t, s] = argmin(values)  # optimal action
        V[t, s] = min(values)      # optimal value
```

This is exactly the backward induction we did by hand, just scaled to 64 states, 5 actions, and 10 periods.

---

## Connection to the Repository

- **Bellman's optimality principle** is discussed in `docs/game_theory_tutorial.md`, Section 3
- The **evolution of the Bellman equation** (standard -> CVaR -> robust CVaR) appears in the same section
- The **computational complexity** $O(T \times |S| \times |A| \times n_{LP})$ is discussed in `README.md`
- The **solver implementation** is the `dp_solve_cfo()` function in the notebook
- The **discount factor** is set via `CFOConfig.wacc` in the notebook

---

## Validation Quiz

### Questions

**Q1.** Why can't we just enumerate all possible strategies (brute force) for the sovereignty model with 5 actions and 10 periods?

**Q2.** State Bellman's optimality principle in your own words (one or two sentences).

**Q3.** In the worked example (3-period tariff problem), what is the optimal action at $t = 1$ when the tariff is ON? Why?

**Q4.** What is the terminal condition in our model, and why is it set that way?

**Q5.** The WACC in the model is 10%. Compute the discount factor $\gamma_t$ for $t = 3$. What does this number mean in practical terms?

**Q6.** The model computes 64 states x 10 periods x 5 actions = 3,200 subproblems. Each subproblem involves solving a Wasserstein LP that takes about 30ms. Roughly how long does the full solve take?

**Q7.** True or False: Dynamic programming only works for expected-value objectives. It cannot be used with CVaR or robust optimization.

**Q8.** In backward induction, why do we start at $t = T$ and work backward, rather than starting at $t = 0$ and working forward?

---

### Answers

**A1.** With 5 actions and 10 periods, there are $5^{10} \approx 10$ million possible action sequences. For each sequence, you would need to evaluate against all possible tariff paths ($2^{10} = 1{,}024$ paths), resulting in roughly 10 billion evaluations. This is computationally intractable even for a toy model. Dynamic programming reduces this to about 3,200 subproblems by exploiting the optimal substructure of the problem.

**A2.** If you are following the best overall strategy, then from any point in time and any state you find yourself in, the remaining strategy must also be the best possible for that state going forward. You never "regret" past decisions on the optimal path -- the future is optimized regardless of how you got there.

**A3.** At $t = 1$ with tariff ON, the optimal action is **Exit** with a cost of 8.
- Waiting would cost: 5 (current tariff) + 0.3(0) + 0.7(5) = 8.5
- Exiting costs: 8 + 0 = 8

Since 8 < 8.5, it is cheaper to exit now than to endure the likely continuation of tariffs. Note that at $t = 2$ (one period remaining), the answer flips: waiting costs 5 while exit costs 8, so you wait. The horizon matters -- with more future exposure, exit becomes worthwhile.

**A4.** The terminal condition is $V_T(s) = 0$ for all states $s$. This means there are no costs beyond the planning horizon. It is the starting point for backward induction -- you need to know the "future value" at the last period to compute the value at $T-1$, and the simplest assumption is that the problem ends at $T$ with zero remaining cost. (In practice, a terminal cost function could be added to capture ongoing exposure beyond the horizon.)

**A5.** $\gamma_3 = 1/(1 + 0.10)^3 = 1/1.331 \approx 0.751$. This means a cost of 1 unit incurred 3 years from now is equivalent to 0.751 units in today's terms. Future costs are worth less because the firm's capital has an opportunity cost of 10% per year.

**A6.** $3{,}200 \times 30\text{ms} = 96{,}000\text{ms} = 96$ seconds, roughly **1.5 minutes**. The actual runtime is reported as 30-60 seconds in the README, which is consistent (not all subproblems require the LP solve, and some are faster than 30ms). This is highly tractable for a decision that might be worth millions of euros.

**A7.** **False.** Dynamic programming works for any objective that satisfies the **recursive structure** (optimal substructure). Both CVaR and robust CVaR objectives preserve this structure. The Bellman equation changes from $\min_a \mathbb{E}[\ldots]$ to $\min_a \text{CVaR}[\ldots]$ or $\min_a \sup_p \text{CVaR}^p[\ldots]$, but the backward induction algorithm remains the same. Only the inner computation (how you evaluate the expected/worst-case cost) changes.

**A8.** We start at $t = T$ because we need to know the **future value** $V_{t+1}(s')$ before we can compute $V_t(s)$. The Bellman equation defines $V_t$ in terms of $V_{t+1}$. If we tried to go forward from $t = 0$, we would not know the future values and could not evaluate our decisions. Starting at the end (where $V_T = 0$ is known) and working backward fills in the value function one layer at a time, until we reach $t = 0$ and have the complete optimal policy.

---

**Previous step:** [02 -- Game Theory Primer](02_game_theory_primer.md)
**Next step:** [04 -- Risk and Ambiguity](04_risk_and_ambiguity.md)
