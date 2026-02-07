# Step 2 -- Game Theory Primer

## Learning Objectives

By the end of this step, you will:

- Know the key milestones in the history of game theory
- Understand the concepts of players, strategies, payoffs, and equilibrium
- Be able to find Nash equilibria in simple 2x2 games
- Understand the minimax theorem and its connection to zero-sum games
- Know what sequential (extensive form) games are
- Understand why we model "Nature" as an adversarial player in this project

---

## A Brief History

Game theory is the mathematical study of strategic interactions -- situations where the outcome for each participant depends on the choices of all participants.

### The Foundations (1920s-1940s)

**John von Neumann** proved the **minimax theorem** in 1928: in any finite two-player zero-sum game, there exists an optimal strategy for each player. This was the mathematical birth of game theory.

In 1944, von Neumann and Oskar Morgenstern published *Theory of Games and Economic Behavior*, which formalized:

- **Normal form games** (payoff matrices)
- **Extensive form games** (game trees with sequential moves)
- **Utility theory** (how to represent preferences mathematically)

### The Nash Revolution (1950s)

**John Nash** generalized von Neumann's results to **non-zero-sum games** (where players' interests are not perfectly opposed). His key result: every finite game has at least one **Nash equilibrium** -- a set of strategies where no player can improve their outcome by unilaterally changing their strategy.

Nash equilibrium became the central solution concept in economics and earned Nash the Nobel Prize in 1994.

### Dynamic Games (1950s-1970s)

**Lloyd Shapley** extended game theory to **stochastic games** (1953) -- games that evolve over time with probabilistic transitions. This is directly relevant to our model, where the tariff regime evolves stochastically.

**Richard Bellman** developed **dynamic programming** (1957), providing the computational machinery to solve sequential decision problems. We will cover this in detail in Step 03.

### Modern Developments

- **Robust game theory** (2010s+): Games where players face ambiguity about opponents' types or payoff structures -- directly connected to our Wasserstein DRO approach.
- **Mean-field game theory** (2000s+): Tractable approximations for games with many players -- relevant to the extensions in Step 08.

---

## Key Concepts

### Players

A **player** is a decision-maker in the game. In our model:

- **Player 1: The Firm** -- chooses actions to minimize its costs
- **Player 2: Nature** -- controls the environment (tariff regime) and, under ambiguity, can adversarially shift probability distributions

### Strategies

A **strategy** is a complete plan of action. It specifies what a player will do in every possible situation.

- **Pure strategy:** A deterministic choice. "Always invest at $t=0$."
- **Mixed strategy:** A probability distribution over pure strategies. "Invest with 60% probability, wait with 40%."
- **Policy (in dynamic games):** A function mapping states to actions. "If tariff is on and migration progress is 2, then accelerate."

In our model, the firm's strategy is a **policy** $\pi(t, s)$ -- a function that tells the firm what to do in every state at every time period.

### Payoffs

A **payoff** (or utility) is the outcome each player receives for a given combination of strategies. In our model:

- The Firm's payoff is the **negative of discounted cost** (the firm wants to minimize cost, which is the same as maximizing negative cost)
- Nature's payoff is the **firm's cost** (Nature wants to make things as expensive as possible for the firm)

### Zero-Sum Games

A game is **zero-sum** if one player's gain equals the other's loss. Our model is approximately zero-sum: the firm minimizes cost while Nature maximizes it within constraints.

In a zero-sum game, the minimax theorem guarantees that both players have optimal strategies, and the game has a well-defined **value** (the outcome when both play optimally).

---

## The Minimax Theorem: A Worked Example

Let us work through a simple 2x2 zero-sum game to build intuition.

### Setup

Two players: **Row** (minimizer) and **Column** (maximizer). Row chooses a row, Column chooses a column. The number in the cell is the payoff (cost to Row, gain to Column):

|  | Column: Left | Column: Right |
|--|:---:|:---:|
| **Row: Up** | 3 | 7 |
| **Row: Down** | 5 | 2 |

### Row's Reasoning (Minimizer)

Row thinks: "If I play Up, Column will play Right (giving me 7 -- bad). If I play Down, Column will play Left (giving me 5). So my worst-case is min(max(3,7), max(5,2)) = min(7, 5) = **5** with Down."

This is the **maximin** value: the best worst-case for Row.

### Column's Reasoning (Maximizer)

Column thinks: "If I play Left, Row will play Up (giving me 3). If I play Right, Row will play Down (giving me 2). So my worst-case is max(min(3,5), min(7,2)) = max(3, 2) = **3** with Left."

This is the **minimax** value: the best worst-case for Column.

### The Gap

Maximin (5) is not equal to minimax (3). There is no pure-strategy equilibrium where both are satisfied. This happens when there is no "saddle point" in the matrix.

### Mixed Strategy Equilibrium

The minimax theorem guarantees a solution in **mixed strategies** (randomization):

Let Row play Up with probability $p$ and Down with probability $1-p$.

Column's expected payoff from Left: $3p + 5(1-p) = 5 - 2p$

Column's expected payoff from Right: $7p + 2(1-p) = 2 + 5p$

At equilibrium, Column is indifferent: $5 - 2p = 2 + 5p$, so $p = 3/7$.

The **game value** is $5 - 2(3/7) = 5 - 6/7 = 29/7 \approx 4.14$.

**Key insight:** By randomizing, Row can guarantee a worst-case of 4.14, which is better than the pure-strategy worst-case of 5. Randomization is a form of protection against an adversary.

### Connection to Our Model

In our sovereignty model, the "minimax" structure appears in the Bellman equation:

$$V_t(s) = \min_{a} \max_{p \in \mathcal{P}_\varepsilon} \text{CVaR}_\alpha^p[\ldots]$$

- The Firm (Row) **minimizes** over actions $a$
- Nature (Column) **maximizes** over distributions $p$ in the Wasserstein ball

The Wasserstein constraint ($p \in \mathcal{P}_\varepsilon$) is like limiting Column's strategy set -- Nature cannot be arbitrarily adversarial, only within a ball of radius $\varepsilon$ around the nominal distribution.

---

## Sequential Games and Game Trees

The example above is a **simultaneous** game (both players choose at the same time). Our sovereignty model is a **sequential** game: decisions unfold over time.

### Extensive Form

A sequential game is represented as a **game tree**:

```
Time 0: Firm chooses action
    |
    |---> wait
    |       |
    |       Time 1: Nature reveals tariff (on/off)
    |               |
    |               |---> tariff OFF: Firm chooses again...
    |               |---> tariff ON:  Firm chooses again...
    |
    |---> invest
    |       |
    |       Time 1: Nature reveals tariff
    |               |
    |               |---> tariff OFF: Firm chooses again...
    |               |---> tariff ON:  Firm chooses again...
    |
    ... (and so on for hedge, accelerate, exit)
```

At each node, one player moves. The game unfolds over 10 periods (years), creating a tree with many branches.

### Why This Matters

In a sequential game, **backward induction** (solving from the end to the beginning) finds the optimal strategy. This is exactly what Bellman's dynamic programming does -- and what our model implements. We will dive deep into this in Step 03.

### Information Structure

In our model, the firm **observes** the full state (tariff regime, migration progress, flags) before making each decision. This is called **perfect state observability**. The firm does not know the future, but it knows where it stands right now.

This is a simplification. In reality, you might not know the exact "tariff probability" (partial observability). Extensions to handle this exist (POMDPs) but are beyond the current model.

---

## Why Model Nature as a Player?

This is a conceptual choice that deserves careful explanation.

### Nature Is Not Malicious

Nature (political risk, regulatory dynamics) does not literally "want" to hurt your firm. But modeling it as an adversarial player is a **conservative design choice** that provides several benefits:

**1. Protection against Murphy's Law.** "Whatever can go wrong, will go wrong, at the worst possible time." By assuming Nature plays against you, you prepare for bad outcomes clustering when you are most vulnerable.

**2. Captures persistence and correlation.** Political regimes are sticky -- bad periods tend to persist (tariffs rarely disappear after one year). An adversarial Nature captures this better than independent random draws.

**3. Protects against overconfidence.** If your political risk forecast is wrong (and it probably is), an adversarial Nature tests your strategy against the worst plausible scenario, not just the expected one.

**4. Produces robust strategies.** A strategy that works against an adversarial Nature will certainly work if Nature is merely random. The reverse is not true.

### The Constraint on Nature

Crucially, Nature is not *infinitely* adversarial. The Wasserstein ball radius $\varepsilon$ limits how much Nature can deviate from the nominal distribution:

- $\varepsilon = 0$: Nature follows the nominal model exactly (no adversary)
- $\varepsilon = 0.1$: Nature can shift probabilities slightly (mild adversary)
- $\varepsilon = 0.4$: Nature has significant freedom (strong adversary)
- $\varepsilon = \infty$: Pure worst-case (usually too conservative)

The calibration of $\varepsilon$ is critical. In the model, $\varepsilon(t)$ is **time-varying** and linked to observable political risk indicators (like the Economic Policy Uncertainty index), making the adversary's strength data-driven rather than arbitrary.

### Where Is the Supplier?

An important clarification: the **supplier is not a separate player** in this model. The supplier is assumed to mechanically pass tariff costs through to the firm (100% pass-through). It is absorbed into Nature.

Why? Because if the supplier has no strategic maneuvering room (it simply adds the tariff to its price), modeling it explicitly adds no information. The two effective players are:

1. The **EU government** (decides to impose tariffs -- a political decision)
2. The **supplier** (passes costs through -- a mechanical action)

Both are wrapped into "Nature." Making the supplier a strategic player (with partial absorption, strategic pricing, etc.) is discussed as a future extension in Step 08.

---

## Nash Equilibrium: Formal Definition

For reference, here is the formal definition you will encounter in the literature:

A **Nash Equilibrium** is a strategy profile $(s_1^*, s_2^*, \ldots, s_n^*)$ such that for every player $i$:

$$u_i(s_i^*, s_{-i}^*) \geq u_i(s_i, s_{-i}^*) \quad \forall s_i \in S_i$$

In words: no player can improve their payoff by unilaterally changing their strategy, holding everyone else's strategy fixed.

In our two-player zero-sum game, the Nash equilibrium coincides with the **minimax solution**: the firm's optimal policy and Nature's worst-case distribution form a saddle point where neither can improve.

---

## Connection to the Repository

The game-theoretic concepts from this step appear throughout the repository:

- The **two-player game structure** is defined in the notebook's Section 1 ("Model spec -- a strategic game")
- **Player definitions** (Firm as minimizer, Nature as maximizer) appear in `README.md` under "Why Games?"
- The **minimax structure** appears in the Bellman-Wasserstein equation (notebook Section 7)
- The **comprehensive game theory tutorial** is in `docs/game_theory_tutorial.md`, which covers history, minimax, Bellman evolution, N-player extensions, and business applications in much greater detail
- The **N-player extensions** (oligopoly, supplier as strategic player, government game) are covered in Section 5 of that tutorial

---

## Validation Quiz

### Questions

**Q1.** In a zero-sum game, what is the relationship between Player 1's payoff and Player 2's payoff?

**Q2.** Consider this 2x2 zero-sum game (payoff to Row, who minimizes):

|  | Column: A | Column: B |
|--|:-:|:-:|
| **Row: X** | 4 | 6 |
| **Row: Y** | 8 | 2 |

What is Row's maximin value (best worst-case under pure strategies)? What pure strategy achieves it?

**Q3.** What is the difference between a "strategy" and a "policy" in a dynamic (sequential) game?

**Q4.** In our model, the Wasserstein ball radius $\varepsilon$ controls how adversarial Nature can be. What happens at the two extremes?
- (a) When $\varepsilon = 0$
- (b) When $\varepsilon \to \infty$

**Q5.** A colleague argues: "Modeling Nature as adversarial is too pessimistic. Political risk is random, not malicious." Give two reasons why the adversarial framing is still useful.

**Q6.** Why is the supplier not modeled as a separate strategic player in the current model?

**Q7.** John Nash's key contribution was extending game theory from zero-sum games to what type of games?

**Q8.** In the game tree for our sequential sovereignty game, who moves first at each time period -- the Firm or Nature? What does the other player do after?

---

### Answers

**A1.** In a zero-sum game, Player 1's payoff plus Player 2's payoff equals zero (or a constant). One player's gain is exactly the other's loss. In our model, the Firm's cost is Nature's "gain" -- the firm minimizes what Nature maximizes.

**A2.** Row's worst cases:
- If Row plays X: worst case is max(4, 6) = 6
- If Row plays Y: worst case is max(8, 2) = 8

Maximin = min(6, 8) = **6**, achieved by playing **X**. Row guarantees a cost of at most 6 by choosing X.

(Note: this game also has no pure-strategy saddle point, since Column's minimax is max(min(4,8), min(6,2)) = max(4, 2) = 4, which differs from 6. A mixed-strategy equilibrium exists between 4 and 6.)

**A3.** A **strategy** is a general term for any plan of action. A **policy** is specifically a function $\pi(t, s)$ that maps each time period $t$ and state $s$ to an action $a$. In a dynamic game, the policy is the natural form of a strategy because the player needs to specify what to do in every possible future situation, not just at the start.

**A4.**
- **(a) $\varepsilon = 0$:** Nature must follow the nominal distribution exactly. There is no adversarial ambiguity. The model reduces to standard dynamic programming with CVaR risk measure. You are trusting your forecast completely.
- **(b) $\varepsilon \to \infty$:** Nature can choose any distribution at all. This is pure worst-case (maximin) with no constraint. Typically far too conservative -- it assumes the worst possible scenario regardless of plausibility. All actions would appear equally catastrophic.

**A5.** Two reasons:
1. **Robustness guarantee:** A strategy that works against an adversarial Nature will certainly work if Nature is merely random. It is a conservative hedge that protects against the worst plausible case. The Wasserstein constraint prevents it from being paranoid -- only deviations within $\varepsilon$ of the nominal are considered.
2. **Captures clustering and persistence:** Real political risk exhibits clustering (bad events trigger more bad events) and persistence (tariff regimes last years, not days). An adversarial Nature naturally captures this pattern -- it will concentrate bad outcomes when the firm is most vulnerable, which is realistic.

**A6.** Because the supplier is assumed to have no strategic maneuvering room. It mechanically passes 100% of the tariff cost through to the firm. If the supplier cannot choose to absorb part of the tariff, negotiate strategically, or adjust pricing over time, modeling it as a separate player adds complexity without information. The supplier's behavior is folded into Nature's tariff regime dynamics.

**A7.** Nash generalized game theory from **zero-sum** games (where interests are perfectly opposed) to **non-zero-sum** games (where players can have partially aligned or complex interests). He proved that every finite game -- not just zero-sum ones -- has at least one equilibrium point.

**A8.** The **Firm** moves first at each time period, choosing an action (wait, invest, hedge, accelerate, exit). Then **Nature** reveals the next state -- the tariff regime evolves (probabilistically, via a Markov chain), and the state transitions accordingly. In the Bellman equation, this is captured by the min (Firm) over actions followed by the max/expectation (Nature) over next states.

---

**Previous step:** [01 -- Why Sovereignty Matters](01_business_context.md)
**Next step:** [03 -- Dynamic Programming](03_dynamic_programming.md)
