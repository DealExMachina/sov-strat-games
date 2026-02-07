# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-07

### Added

**Intern Tutorial Syllabus** (`docs/tuto/`):
- 9-step progressive tutorial (approx. 3,000 lines) to onboard newcomers to the framework
- `00_welcome.md` -- Project overview, repo orientation, prerequisites, learning roadmap
- `01_business_context.md` -- Real-world sovereignty problem, why NPV fails, three layers of uncertainty, policy vs. decision
- `02_game_theory_primer.md` -- History (von Neumann, Nash, Shapley), minimax with worked 2x2 example, sequential games, Nature as player
- `03_dynamic_programming.md` -- Bellman's principle, backward induction, hand-solved 3-period DP example, discount factor / WACC
- `04_risk_and_ambiguity.md` -- VaR vs. CVaR with numerical examples, coherence, Wasserstein distance (optimal transport analogy), DRO, time-varying epsilon
- `05_the_model.md` -- Full 64-state space, encoding/decoding, 5 actions, transitions, loss function, progressive hedge effectiveness, complete Bellman-Wasserstein equation
- `06_code_walkthrough.md` -- Notebook section map, key classes and functions annotated, solver loop, Wasserstein LP inner problem, dependencies
- `07_results_and_interpretation.md` -- Four scenarios, policy reading, sovereignty premium computation, sensitivity analysis, CFO interpretation framework
- `08_extensions_and_future.md` -- N-player extensions, mean-field games, sovereignty portfolio, 18-month production roadmap, business value, open problems
- Each step includes a validation quiz (5-8 questions) with detailed answers and explanations

## [1.0.0] - 2026-02-04

### Added

**Notebook Enhancements**:
- Comprehensive disclaimer and context explaining toy model nature
- Reading guide for different audiences (CFOs, technical teams, board)
- Glossary of technical terms in plain business language
- CFO-friendly narrative in sections 1, 5, 8, 9, 11
- LLM-powered executive summary (Ollama/OpenAI/Gemini with fallback)
- Enhanced visualizations with business annotations and insights
- Debugging output for LLM provider detection

**Documentation**:
- Technical README with game-theoretic framing for quants
- Comprehensive game theory tutorial (EN) covering:
  * History from von Neumann to modern robust games
  * Why game theory for adversarial Nature and dependencies
  * Min-max approach and Bellman equation evolution
  * Game theory vs simulation comparison
  * Generalization to n-player games
  * 6-step roadmap for real business implementation
- French version of tutorial (FR) 🇫🇷
- Multi-dimensional sovereignty as portfolio of games
- Epistemological discussion on unknowable costs

**Metadata**:
- Author attribution: Jean-Baptiste Dézard / Deal ex Machina SAS
- License: Creative Commons Attribution 4.0 (CC BY 4.0)
- Proper academic citations and bibliography

### Changed

**Business Logic Fixes**:
- Fixed `post_exit_cost` from 1.0 to 0.0 (correct: zero tariff after exit)
- Implemented progressive hedge effectiveness scaling with migration progress
  * Effectiveness = m / exit_years (0% at m=0 → 100% at m=3)
  * Business logic: hedge becomes more effective as you migrate

**Technical Corrections**:
- Corrected solver documentation: CLARABEL (primary) with SCS fallback
- Fixed indentation errors in rollout function
- Fixed syntax errors in LLM executive summary cell

### Removed

- Obsolete executed notebook file
- Text export of notebook
- Standalone Python run script

### Notes

This is the first official release of the sovereignty strategic game framework.
Consider this a research prototype - use at your own risk as stated in disclaimer.

"This is vibe research - it may contain slop. Use at your own risk :)"
