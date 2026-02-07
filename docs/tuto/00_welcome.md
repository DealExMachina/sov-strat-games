# Step 0 -- Welcome and Roadmap

## Learning Objectives

By the end of this introduction, you will:

- Understand what this project is about at a high level
- Know who built it and why
- Have a clear picture of the learning path ahead
- Be able to navigate the repository and find key files
- Understand the prerequisites for the rest of the tutorial

---

## What Is This Project?

This repository implements a **game-theoretic framework for strategic sovereignty decisions under political risk**. In plain language: it helps a firm decide what to do when it depends on a foreign supplier and that dependency is threatened by geopolitical tensions (tariffs, sanctions, regulatory divergence).

The core idea is that sovereignty is **not** a simple cost-benefit calculation. It is a **dynamic sequential game** between the firm and an adversarial environment ("Nature"), where the firm must choose adaptive strategies over time -- wait, invest in migration, hedge, accelerate, or exit -- while Nature controls the political risk landscape.

The model combines three mathematical pillars:

1. **Dynamic Programming (Bellman equations)** -- to find optimal sequential strategies
2. **CVaR (Conditional Value-at-Risk)** -- to focus on tail risk, not just averages
3. **Wasserstein Distributionally Robust Optimization (DRO)** -- to protect against forecast errors

---

## Who Built This and Why

This project was created by **Jean-Baptiste Dezard** at **Deal ex Machina SAS**. It is a research prototype ("toy model") designed to demonstrate a rigorous approach to a problem that most firms handle with intuition, spreadsheets, or static NPV analysis.

The motivation is practical: in an era of trade wars, technology decoupling, and regulatory fragmentation, firms need better tools to make sovereignty decisions. This model provides **actionable policies** (if-then rules), not just cost estimates.

**Important disclaimer**: This is described as "vibe research" by the author. It is a first-draft toy model for education and research purposes, not a production system. But the mathematical framework is sound and the roadmap to production is documented.

---

## What You Will Learn

This tutorial is organized as a progressive syllabus in 9 steps (including this one). Each step builds on the previous ones:

| Step | Title | What You Will Learn |
|------|-------|---------------------|
| **00** | Welcome and Roadmap | Project overview, how to navigate the repo |
| **01** | Why Sovereignty Matters | The business problem, why traditional tools fail |
| **02** | Game Theory Primer | Players, strategies, Nash equilibrium, minimax |
| **03** | Dynamic Programming | Bellman equations, backward induction, policies |
| **04** | Risk and Ambiguity | CVaR, Wasserstein distance, DRO |
| **05** | The Model | State space, actions, transitions, the full equation |
| **06** | Code Walkthrough | Reading the notebook, key classes and functions |
| **07** | Results and Interpretation | Scenarios, sovereignty premium, CFO lens |
| **08** | Extensions and Future | N-player games, mean-field, production roadmap |

After completing all steps, you will understand:

- **Why** firms need this (business motivation)
- **How** the model works (mathematical foundations)
- **What** the code does (implementation)
- **So what** (interpreting results for decision-makers)
- **What next** (extensions and practical deployment)

---

## Prerequisites

To get the most from this tutorial, you should have:

- **Basic probability**: You know what a probability distribution is, what expected value means, and what a random variable is.
- **Some Python**: You can read Python code, understand classes and functions, and have used NumPy before.
- **Optimization intuition**: You understand the idea of minimizing a function. No need for convex optimization theory yet -- we will build that up.
- **Business awareness**: You have a general sense of what a CFO does, what NPV means, and why firms care about risk.

If any of these feel shaky, don't worry. The tutorial explains concepts from the ground up with examples. The math is introduced progressively, always with intuition first.

---

## How to Navigate the Repository

Here is the structure you should be aware of:

```
DP-CVaR-Wasserstein/
|
|-- README.md                          <-- Start here for the project overview
|-- sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb
|                                      <-- The main (and only) implementation notebook
|-- LLM_context_prompt.md             <-- Context for generating executive summaries
|
|-- docs/
|   |-- game_theory_tutorial.md        <-- Comprehensive game theory guide
|   |-- game_theory_tutorial_fr.md     <-- French version of the above
|   |-- bellman_wasserstein_mean_field_framework.md
|   |                                  <-- Unified framework document (v2.0)
|   |-- implementation_roadmap.md      <-- 18-month production roadmap
|   |-- tuto/                          <-- You are here! The tutorial syllabus
|
|-- Livre_Blanc_*.tex                  <-- LaTeX white papers (French)
|-- refs_v6.bib                        <-- Bibliography
|-- CHANGELOG.md                       <-- Version history
```

**Key files to open now:**

1. `README.md` -- Read the "Overview" and "Why Games?" sections
2. `sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb` -- Skim the first two cells (the introduction and glossary)
3. `docs/game_theory_tutorial.md` -- This is the detailed theoretical companion

---

## Estimated Time

Each step takes approximately **30-45 minutes** to read through carefully, work the examples, and complete the quiz. The full syllabus is roughly **5-6 hours** of focused learning.

Recommended approach:

- Do 1-2 steps per day
- Take notes as you go
- Try the quizzes *before* looking at the answers
- Come back to earlier steps if later material feels unclear

---

## Validation Quiz

Test your initial orientation in the repository. Try to answer these before looking at the solutions below.

### Questions

**Q1.** What is the main implementation file in this repository? (Hint: it is not a `.py` file.)

**Q2.** Name the three mathematical pillars that the model combines (you can find them in the README).

**Q3.** What does the acronym CVaR stand for?

**Q4.** The model frames sovereignty as a game between two players. Who are they?

**Q5.** True or False: This is a production-ready system designed for immediate deployment in a firm.

**Q6.** In which file would you find the 18-month roadmap to transform the toy model into a production system?

**Q7.** What license is this project released under?

---

### Answers

**A1.** `sovereignty_dp_cvar_wasserstein_ultraCFO.ipynb` -- a Jupyter notebook. The entire implementation lives in this single notebook, not in a package of Python files.

**A2.** The three pillars are:
1. Dynamic Programming (Bellman equations)
2. CVaR (Conditional Value-at-Risk) for tail risk
3. Wasserstein DRO (Distributionally Robust Optimization) for ambiguity aversion

These appear in the README under "Mathematical Formulation" and in the notebook title itself: "DP-CVaR-Wasserstein."

**A3.** CVaR stands for **Conditional Value-at-Risk**. It measures the average loss in the worst fraction of scenarios (e.g., the worst 10%).

**A4.** The two players are:
- **Player 1 (Firm)**: Chooses actions (wait, invest, hedge, accelerate, exit) to **minimize** cost
- **Player 2 (Nature)**: Controls tariff regime transitions and can select adversarial probability distributions to **maximize** cost within a Wasserstein ball

**A5.** **False.** The README and notebook both explicitly state this is a "first-draft toy model for research and education purposes." The disclaimer even says "this is vibe research -- it may contain slop." A production roadmap exists in `docs/implementation_roadmap.md`, but the current code is a prototype.

**A6.** `docs/implementation_roadmap.md` -- it describes a three-phase, 18-24 month plan covering production foundation, multi-dependency portfolio, and enterprise integration.

**A7.** **Creative Commons Attribution 4.0 International (CC BY 4.0)**. You are free to share and adapt the material for any purpose, including commercially, as long as you give appropriate credit.

---

**Next step:** [01 -- Why Sovereignty Matters](01_business_context.md)
