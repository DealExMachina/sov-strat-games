# Strategic Autonomy Operating System: Implementation Roadmap

## Executive Summary

This document outlines the implementation roadmap for transforming the current Bellman-Wasserstein-DRO toy model into a production-grade Strategic Autonomy Operating System. The roadmap is organized in three phases over 18-24 months, with clear milestones, deliverables, and success criteria.

---

## Current State Assessment

### What Exists Today

| Component | Status | Maturity |
|-----------|--------|----------|
| Single-dependency Bellman solver | Implemented | Prototype |
| Wasserstein-DRO optimization (CVXPY) | Implemented | Prototype |
| CVaR risk measure | Implemented | Prototype |
| State space encoding | Implemented | Prototype |
| Time-varying ambiguity ε(t) | Implemented (toy) | Prototype |
| CFO-friendly notebook | Implemented | Prototype |
| Game theory documentation | Implemented | Complete |

### What Needs to Be Built

| Component | Priority | Complexity |
|-----------|----------|------------|
| Multi-dependency portfolio model | High | High |
| Mean-field game extension | High | High |
| Real indicator integration (EPU, VIX) | High | Medium |
| Multi-criterion solver | High | Medium |
| Trigger/monitoring engine | High | Medium |
| Governance integration | Medium | Low |
| Coalition game module | Medium | High |
| Dashboard/visualization | Medium | Medium |
| API for live monitoring | Low | Medium |

---

## Phase 1: Production Foundation (Months 1-6)

### Objective
Transform the toy model into a calibrated, single-dependency production system with real data integration and governance hooks.

### 1.1 Data Infrastructure (Months 1-2)

#### Deliverables
- [ ] **Indicator data pipeline**: Automated ingestion of EPU, VIX, sanctions watchlists
- [ ] **Parameter mapping module**: Functions to convert observables to model parameters
- [ ] **Historical calibration dataset**: 10+ years of tariff/sanction events for backtesting

#### Technical Specification

```python
# Target module: src/data/indicators.py

class IndicatorPipeline:
    """Automated indicator collection and parameter mapping"""
    
    sources: Dict[str, DataSource] = {
        'epu_us': BakerBloomDavisAPI(),
        'epu_eu': BakerBloomDavisAPI(region='EU'),
        'vix': CBOEDataFeed(),
        'sanctions': OFACWatchlist(),
        'trade_actions': USTRMonitor()
    }
    
    def fetch_current(self) -> IndicatorVector:
        """Fetch latest values for all indicators"""
        pass
    
    def map_to_parameters(self, indicators: IndicatorVector) -> ModelParameters:
        """Convert observables to model parameters (ε, p01, p10, etc.)"""
        pass
```

#### Success Criteria
- Automated daily indicator updates
- Parameter mapping functions validated against historical episodes
- <5 minute latency from data availability to parameter update

### 1.2 Model Calibration (Months 2-4)

#### Deliverables
- [ ] **Cost calibration module**: Map abstract units to actual € exposures
- [ ] **Transition probability estimation**: Historical estimation of p01, p10
- [ ] **Ambiguity radius calibration**: Link ε to forecast error distributions
- [ ] **Backtesting framework**: Validate model against historical decisions

#### Technical Specification

```python
# Target module: src/calibration/costs.py

class CostCalibrator:
    """Calibrate abstract model costs to actual financial exposure"""
    
    def __init__(self, 
                 annual_supplier_spend: float,
                 tariff_rate_range: Tuple[float, float],
                 migration_cost_estimate: float,
                 exit_cost_estimate: float):
        self.base_exposure = annual_supplier_spend
        self.tariff_range = tariff_rate_range
        self.migration_cost = migration_cost_estimate
        self.exit_cost = exit_cost_estimate
    
    def calibrate_spec(self, spec: GameSpec) -> GameSpec:
        """Return calibrated GameSpec with real € values"""
        scale = self.base_exposure / spec.tariff_cost
        return spec.copy(update={
            'tariff_cost': self.base_exposure * self.tariff_range[1],
            'hedged_tariff_cost': self.base_exposure * self.tariff_range[0],
            'capex_invest': self.migration_cost,
            'termination_fee': self.exit_cost * 0.6,
            'cutover_cost': self.exit_cost * 0.25,
            'recert_audit_cost': self.exit_cost * 0.15,
            # ... other parameters
        })
```

#### Success Criteria
- Model costs match actual budget estimates within 20%
- Transition probabilities validated on 3+ historical episodes
- Backtest shows model would have recommended reasonable actions

### 1.3 Multi-Criterion Extension (Months 3-5)

#### Deliverables
- [ ] **Criterion-specific loss functions**: Financial, EBITDA, Cash, Strategic, Execution, Optionality
- [ ] **Multi-criterion Bellman solver**: Solve for each criterion independently
- [ ] **Action-outcome matrix generator**: Produce decision support tables
- [ ] **Pareto frontier computation**: Identify non-dominated actions

#### Technical Specification

```python
# Target module: src/solver/multi_criterion.py

@dataclass
class Criterion:
    name: str
    loss_fn: Callable[[GameSpec, int, int, int], float]
    weight: float = 1.0
    units: str = "€M"

STANDARD_CRITERIA = [
    Criterion("financial", financial_loss, 1.0, "€M NPV"),
    Criterion("ebitda", ebitda_loss, 1.0, "€M/year"),
    Criterion("cash", cash_loss, 1.0, "€M"),
    Criterion("strategic", strategic_loss, 1.0, "index"),
    Criterion("execution", execution_loss, 1.0, "FTE-months"),
    Criterion("optionality", optionality_loss, 1.0, "€M"),
]

class MultiCriterionSolver:
    """Solve Bellman for multiple criteria"""
    
    def solve_all(self, spec: GameSpec, criteria: List[Criterion], 
                  eps_fn: Callable) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Return {criterion_name: (V, pi)} for each criterion"""
        pass
    
    def action_outcome_matrix(self, state: int, t: int) -> pd.DataFrame:
        """Generate action-contingent outcome table"""
        pass
    
    def pareto_frontier(self, state: int, t: int) -> List[int]:
        """Return list of Pareto-optimal actions"""
        pass
```

#### Success Criteria
- All 6 criteria implemented with validated loss functions
- Action-outcome matrix generated in <30 seconds
- Pareto frontier correctly identifies non-dominated actions

### 1.4 Trigger/Monitoring Engine (Months 4-6)

#### Deliverables
- [ ] **Threshold configuration**: Define trigger thresholds for all parameters
- [ ] **Trigger evaluation engine**: Automated threshold breach detection
- [ ] **Escalation routing**: Route triggers to appropriate governance level
- [ ] **Monitoring dashboard**: Real-time display of system state

#### Technical Specification

```python
# Target module: src/monitoring/triggers.py

@dataclass
class TriggerConfig:
    # Parameter change triggers
    epsilon_change_threshold: float = 0.05
    p_change_threshold: float = 0.03
    mu_change_threshold: float = 0.10
    
    # Model output triggers
    v0_deterioration_threshold: float = 0.15
    policy_change_trigger: bool = True
    
    # Governance escalation
    escalate_committee_threshold: float = 0.20
    escalate_board_threshold: float = 0.35

class TriggerEngine:
    """Evaluate triggers and route escalations"""
    
    def __init__(self, config: TriggerConfig):
        self.config = config
        self.history: List[MonitoringSnapshot] = []
    
    def evaluate(self, current: ModelState, previous: ModelState) -> TriggerResult:
        """Evaluate all triggers and return required actions"""
        pass
    
    def route_escalation(self, result: TriggerResult) -> List[Escalation]:
        """Route triggers to appropriate governance level"""
        pass
```

#### Success Criteria
- Trigger evaluation completes in <1 second
- Zero false negatives on historical threshold breaches
- Escalation routing tested with governance stakeholders

### 1.5 Governance Integration (Months 5-6)

#### Deliverables
- [ ] **Decision rights matrix**: RACI for all decision types
- [ ] **Review cadence calendar**: Quarterly/annual review schedule
- [ ] **Briefing templates**: Standardized formats for Committee/Board
- [ ] **Audit trail**: Logging of all decisions and model runs

#### Success Criteria
- Governance framework approved by Strategy Committee
- First quarterly review completed
- Audit trail captures all model runs with parameters

### Phase 1 Milestone: Single-Dependency Production System

**Demonstration**: Run calibrated model on one critical dependency with:
- Real indicator data feeding parameter updates
- Multi-criterion action-outcome matrix
- Active trigger monitoring
- Governance escalation tested

**Go/No-Go Criteria**:
- [ ] Model calibrated to actual costs (±20%)
- [ ] Backtested on 2+ historical episodes
- [ ] Trigger system operational for 30 days
- [ ] Governance framework approved
- [ ] First escalation successfully routed

---

## Phase 2: Multi-Dependency Portfolio (Months 7-12)

### Objective
Extend to multiple dependencies with portfolio optimization and mean-field approximation for industry dynamics.

### 2.1 Portfolio State Space (Months 7-8)

#### Deliverables
- [ ] **Multi-dependency state encoding**: Efficient representation for N dependencies
- [ ] **Correlation structure**: Model correlated risk factors across dependencies
- [ ] **Constraint specification**: Budget, capacity, sequencing constraints

#### Technical Specification

```python
# Target module: src/model/portfolio.py

@dataclass
class DependencyPortfolio:
    dependencies: List[Dependency]
    correlation_matrix: np.ndarray
    budget_constraint: float
    capacity_constraint: float
    sequencing_constraints: List[Tuple[int, int]]  # (i, j) means i before j
    
    @property
    def joint_state_count(self) -> int:
        """Total states (may be intractable for N > 3)"""
        return np.prod([d.state_count for d in self.dependencies])
    
    def needs_approximation(self) -> bool:
        """True if state space too large for exact solution"""
        return self.joint_state_count > 10000
```

#### Success Criteria
- Support 3 dependencies with exact solution
- Correlation structure validated against historical co-movements
- Constraints correctly enforce budget/capacity limits

### 2.2 Portfolio Bellman Solver (Months 8-10)

#### Deliverables
- [ ] **Exact solver for N ≤ 3**: Full joint state space Bellman
- [ ] **Approximate solver for N > 3**: Decomposition or sampling-based
- [ ] **Portfolio action-outcome matrix**: Multi-dependency decision support

#### Technical Specification

```python
# Target module: src/solver/portfolio.py

class PortfolioBellmanSolver:
    """Solve multi-dependency Bellman with constraints"""
    
    def __init__(self, portfolio: DependencyPortfolio, spec: GameSpec):
        self.portfolio = portfolio
        self.spec = spec
    
    def solve_exact(self, eps_fn: Callable) -> Tuple[np.ndarray, np.ndarray]:
        """Exact solution for small state spaces"""
        pass
    
    def solve_approximate(self, eps_fn: Callable, 
                          method: str = "decomposition") -> Tuple[np.ndarray, np.ndarray]:
        """Approximate solution for large state spaces"""
        pass
    
    def optimal_sequencing(self) -> List[int]:
        """Return optimal order of dependency migrations"""
        pass
```

#### Success Criteria
- Exact solver handles 3 dependencies in <10 minutes
- Approximate solver scales to 10 dependencies
- Sequencing recommendations validated by operations team

### 2.3 Mean-Field Game Module (Months 9-11)

#### Deliverables
- [ ] **Mean-field state representation**: Industry distribution μ
- [ ] **Forward-backward iteration**: MFE computation algorithm
- [ ] **Industry coupling functions**: How μ affects firm costs
- [ ] **Equilibrium convergence diagnostics**: Verify MFE quality

#### Technical Specification

```python
# Target module: src/solver/mean_field.py

@dataclass
class MeanFieldState:
    """Aggregate industry state distribution"""
    migration_distribution: np.ndarray  # P(migration_progress = k)
    capacity_utilization: float
    coalition_strength: float

class MeanFieldGameSolver:
    """Solve mean-field game for industry equilibrium"""
    
    def __init__(self, spec: GameSpec, coupling: IndustryCoupling):
        self.spec = spec
        self.coupling = coupling
    
    def solve_mfe(self, initial_mu: MeanFieldState, 
                  tolerance: float = 1e-4,
                  max_iterations: int = 100) -> Tuple[Policy, MeanFieldState]:
        """
        Iterate to mean-field equilibrium:
        1. Backward pass: Solve Bellman given μ
        2. Forward pass: Update μ given policy
        3. Repeat until convergence
        """
        pass
    
    def industry_scenario(self, mu_scenario: MeanFieldState) -> Policy:
        """Firm's optimal policy given hypothetical industry state"""
        pass
```

#### Success Criteria
- MFE convergence in <50 iterations for typical parameters
- Industry coupling validated against market data
- Scenario analysis produces intuitive results

### 2.4 Coalition Assessment Module (Months 10-12)

#### Deliverables
- [ ] **Coalition value computation**: Shapley value for cost sharing
- [ ] **Commitment credibility scoring**: Assess partner reliability
- [ ] **Coalition decision framework**: Join/form/avoid recommendations

#### Technical Specification

```python
# Target module: src/model/coalition.py

@dataclass
class Coalition:
    members: List[str]
    shared_investment: float
    governance_structure: str
    exit_clauses: List[str]

class CoalitionAnalyzer:
    """Analyze coalition formation opportunities"""
    
    def compute_standalone_cost(self, firm: str, dependency: Dependency) -> float:
        """Cost of individual migration"""
        pass
    
    def compute_coalition_cost(self, coalition: Coalition, 
                               dependency: Dependency) -> Dict[str, float]:
        """Cost allocation using Shapley value"""
        pass
    
    def coalition_benefit(self, firm: str, coalition: Coalition) -> float:
        """Net benefit of joining coalition vs standalone"""
        pass
    
    def recommend(self, firm: str, 
                  available_coalitions: List[Coalition]) -> CoalitionRecommendation:
        """Recommend join/form/avoid for each coalition opportunity"""
        pass
```

#### Success Criteria
- Shapley value computation correct on test cases
- Coalition recommendations reviewed by BD/Strategy team
- At least one coalition opportunity assessed

### Phase 2 Milestone: Multi-Dependency System

**Demonstration**: Run portfolio model on 3 critical dependencies with:
- Joint optimization respecting constraints
- Mean-field industry dynamics
- Coalition opportunity assessment
- Integrated dashboard

**Go/No-Go Criteria**:
- [ ] Portfolio model optimizes 3 dependencies jointly
- [ ] Mean-field equilibrium computed for industry scenario
- [ ] Coalition analysis completed for 1 opportunity
- [ ] Dashboard displays portfolio state

---

## Phase 3: Enterprise Integration (Months 13-18)

### Objective
Integrate the system into enterprise strategic planning, risk management, and governance processes.

### 3.1 API and Integration Layer (Months 13-14)

#### Deliverables
- [ ] **REST API**: Expose model endpoints for integration
- [ ] **Event streaming**: Real-time trigger notifications
- [ ] **ERP integration**: Connect to financial planning systems
- [ ] **Risk system integration**: Feed into enterprise risk dashboards

### 3.2 Advanced Visualization (Months 14-16)

#### Deliverables
- [ ] **Executive dashboard**: Board-ready visualizations
- [ ] **Scenario explorer**: Interactive what-if analysis
- [ ] **Historical replay**: Visualize past decisions and outcomes
- [ ] **Trigger timeline**: Track trigger history and escalations

### 3.3 Learning and Adaptation (Months 15-17)

#### Deliverables
- [ ] **Bayesian parameter update**: Learn from observed outcomes
- [ ] **Model performance tracking**: Compare predictions to actuals
- [ ] **Adaptive thresholds**: Auto-tune trigger thresholds

### 3.4 External Validation (Months 16-18)

#### Deliverables
- [ ] **Academic review**: CREST/INRIA partnership for methodology validation
- [ ] **Peer benchmarking**: Compare to industry approaches
- [ ] **Audit certification**: External audit of model and governance

### Phase 3 Milestone: Enterprise-Grade System

**Demonstration**: Full integration with:
- Live API serving multiple consumers
- Executive dashboard in production
- 12+ months of model performance tracking
- External validation complete

**Go/No-Go Criteria**:
- [ ] API serves 10+ daily requests reliably
- [ ] Dashboard used in 2+ Board presentations
- [ ] Bayesian learning improves parameter estimates
- [ ] External validation report positive

---

## Resource Requirements

### Team Structure

| Role | Phase 1 | Phase 2 | Phase 3 | Skills |
|------|---------|---------|---------|--------|
| **Quant Lead** | 1.0 FTE | 1.0 FTE | 0.5 FTE | Optimization, game theory, Python |
| **Data Engineer** | 0.5 FTE | 0.5 FTE | 0.5 FTE | ETL, APIs, databases |
| **Full-Stack Dev** | 0.0 FTE | 0.5 FTE | 1.0 FTE | Dashboard, API, integration |
| **Strategy Analyst** | 0.5 FTE | 0.5 FTE | 0.5 FTE | Business validation, governance |
| **Project Manager** | 0.25 FTE | 0.25 FTE | 0.25 FTE | Coordination, stakeholder mgmt |

### Infrastructure

| Component | Phase 1 | Phase 2 | Phase 3 |
|-----------|---------|---------|---------|
| **Compute** | Local/cloud VM | Dedicated server | Kubernetes cluster |
| **Storage** | PostgreSQL | PostgreSQL + TimescaleDB | Enterprise data lake |
| **Monitoring** | Basic logging | Prometheus/Grafana | Enterprise APM |

### Budget Estimate (Indicative)

| Category | Phase 1 | Phase 2 | Phase 3 | Total |
|----------|---------|---------|---------|-------|
| Personnel | €150K | €200K | €175K | €525K |
| Infrastructure | €10K | €25K | €50K | €85K |
| Data/APIs | €15K | €20K | €25K | €60K |
| External validation | €0 | €0 | €50K | €50K |
| **Total** | **€175K** | **€245K** | **€300K** | **€720K** |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data source unavailability | Medium | High | Multiple redundant sources, caching |
| Model calibration failure | Medium | High | Conservative defaults, human override |
| Governance adoption resistance | Medium | Medium | Early stakeholder engagement, pilot |
| Computational scalability | Low | High | Approximate methods, cloud burst |
| External validation negative | Low | Medium | Iterative improvement, academic partnership |

---

## Success Metrics

### Phase 1 KPIs
- Model calibration accuracy: ±20% of actual costs
- Trigger latency: <5 minutes from indicator change
- Governance adoption: 1+ quarterly review completed

### Phase 2 KPIs
- Portfolio optimization: 3 dependencies jointly optimized
- Mean-field convergence: <50 iterations
- Coalition analysis: 1+ opportunity assessed

### Phase 3 KPIs
- API reliability: 99.5% uptime
- Prediction accuracy: Track forecast vs. outcome
- User adoption: Dashboard used in Board presentations

---

## Governance and Oversight

### Steering Committee
- **Chair**: CFO or Chief Strategy Officer
- **Members**: CRO, CIO, Head of Procurement, Head of Strategy
- **Cadence**: Quarterly review of roadmap progress

### Technical Review
- **Lead**: Quant Lead
- **Members**: Data Engineer, External advisor (CREST/INRIA)
- **Cadence**: Monthly model review

### Change Management
- All parameter changes logged with rationale
- Trigger threshold changes require Committee approval
- Model structure changes require Steering Committee approval

---

## Next Steps

1. **Immediate (Week 1)**: Secure executive sponsorship and budget approval
2. **Week 2-4**: Recruit/assign Quant Lead and Data Engineer
3. **Month 1**: Establish data pipeline for primary indicators
4. **Month 2**: Begin cost calibration with Finance team
5. **Month 3**: First calibrated model run on priority dependency

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-05  
**Author**: Strategic Autonomy Working Group  
**Status**: Draft for Review
