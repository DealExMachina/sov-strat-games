# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
