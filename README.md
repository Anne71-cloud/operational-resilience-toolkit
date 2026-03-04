<div align="center">

# 🏦 Operational Resilience Toolkit

**A comprehensive framework for managing operational resilience in financial institutions**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)](https://resilience-toolkit.netlify.app)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![DORA](https://img.shields.io/badge/DORA-Aligned-1B2A4A?style=for-the-badge)](https://www.digital-operational-resilience-act.com)
[![FINMA](https://img.shields.io/badge/FINMA-Aligned-C23B22?style=for-the-badge)](https://www.finma.ch)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

*Built to support 2nd Line of Defence oversight, regulatory compliance, and continuous improvement of resilience posture across DORA, FINMA, PRA, and BCBS frameworks.*

[Live Dashboard](https://resilience-toolkit.netlify.app) · [Documentation](docs/METHODOLOGY.md) · [Regulatory Mapping](docs/REGULATORY_MAPPING.md)

</div>

---

## 🎯 The Problem

Financial institutions face increasing regulatory expectations to demonstrate they can **prevent, withstand, and recover from severe operational disruptions**. Regulations like DORA (EU), FINMA Circular 2023/1 (Switzerland), PRA SS1/21 (UK), and BCBS 516 (Global) require firms to:

- Identify critical business functions and map end-to-end dependencies
- Define impact tolerances — the maximum tolerable disruption
- Test resilience through severe-but-plausible scenarios
- Track incidents, root causes, and lessons learned
- Report resilience posture to boards and regulators

**This toolkit provides a structured, data-driven approach to all of the above.**

---

## 🖥️ Live Dashboard

> **[▶ Launch the Interactive Dashboard](https://resilience-toolkit.netlify.app)**

The dashboard provides real-time visibility across five modules:

| Module | Purpose |
|--------|---------|
| **Dashboard** | Executive overview — SPOFs, concentration risks, tolerance coverage |
| **Dependencies** | Interactive dependency register with concentration risk analysis |
| **Scenarios** | 6 pre-built scenarios with clickable simulations and gap analysis |
| **Maturity** | Radar charts and gap analysis across DORA, FINMA, PRA, BCBS |
| **Incidents** | Incident tracking with severity/category breakdown and board messages |

---

## 📐 Architecture

```
operational-resilience-toolkit/
│
├── index.html                   # Interactive dashboard (Netlify deployment)
│
├── src/                         # Python backend modules
│   ├── dependency_mapper/       # Critical function & dependency mapping
│   │   ├── mapper.py            # Graph-based dependency engine (NetworkX)
│   │   └── visualiser.py        # Network visualisation with risk heat-mapping
│   │
│   ├── impact_tolerance/        # Impact tolerance definition & monitoring
│   │   └── engine.py            # Multi-dimensional tolerance & breach detection
│   │
│   ├── scenario_testing/        # Severe-but-plausible scenario framework
│   │   ├── scenarios.py         # 6 pre-built scenario definitions
│   │   └── simulator.py         # Cascading failure simulation engine
│   │
│   ├── resilience_scorer/       # Regulatory maturity assessment
│   │   └── scorer.py            # DORA/FINMA/PRA/BCBS scoring model
│   │
│   └── incident_tracker/        # Incident lifecycle & lessons learned
│       └── tracker.py           # Full incident management with trend analysis
│
├── app.py                       # Streamlit dashboard (alternative UI)
├── data/                        # Sample bank configuration
├── docs/                        # Regulatory mapping & methodology
├── tests/                       # Comprehensive test suite
├── requirements.txt
└── setup.py
```

---

## 🚀 Quick Start

### Option 1: Interactive Dashboard (No Installation)

**[▶ Open the live dashboard on Netlify](https://resilience-toolkit.netlify.app)**

### Option 2: Python Library

```bash
git clone https://github.com/anne71-cloud/operational-resilience-toolkit.git
cd operational-resilience-toolkit
pip install -r requirements.txt
```

```python
from src.dependency_mapper.mapper import DependencyMapper
from src.impact_tolerance.engine import ImpactToleranceEngine
from src.scenario_testing.simulator import ResilienceSimulator
from src.resilience_scorer.scorer import ResilienceScorer

# 1. Map critical functions and dependencies
mapper = DependencyMapper()
mapper.add_critical_function("Payments Processing", tier=1)
mapper.add_dependency("Payments Processing", "SWIFT Gateway", dep_type="technology")
mapper.add_dependency("Payments Processing", "Core Banking System", dep_type="technology")
mapper.add_dependency("Payments Processing", "Cloud Provider A", dep_type="third_party")

# 2. Identify vulnerabilities
spofs = mapper.find_single_points_of_failure()
# [{'dependency': 'SWIFT Gateway', 'impacted_functions': ['Payments Processing'], 'risk_level': 'high'}]

# 3. Define impact tolerances
engine = ImpactToleranceEngine()
engine.set_tolerance("Payments Processing",
                     max_disruption_hours=4,
                     financial_impact_limit=5_000_000,
                     customer_impact="critical")

# 4. Run scenario simulation
simulator = ResilienceSimulator(mapper, engine)
result = simulator.run_scenario("cyber_ransomware")
# overall_resilience_rating: 'fail'
# tolerance_breaches: [{'function': 'Payments', 'tolerance_hours': 4, 'estimated_disruption_hours': 48}]

# 5. Score maturity against DORA
scorer = ResilienceScorer()
assessment = scorer.assess(mapper, engine, framework="DORA")
# overall_score: 2.5/5.0, maturity_level: 'Developing'
```

### Option 3: Streamlit Dashboard

```bash
streamlit run app.py
```

### Run Tests

```bash
python tests/test_toolkit.py
```

---

## 📊 Module Deep Dive

### 1. Dependency Mapper

Maps critical business functions to their end-to-end dependencies using **directed graph analysis** (NetworkX). Automatically identifies:

- **Single Points of Failure** — dependencies with no alternative path
- **Concentration Risks** — single providers serving multiple critical functions
- **Critical Chains** — end-to-end dependency paths from function to leaf node
- **Blast Radius** — total impact if a specific dependency fails

### 2. Impact Tolerance Engine

Defines and monitors **maximum tolerable disruption levels** across four dimensions, aligned with DORA Art. 11 and PRA SS1/21:

| Dimension | Metrics |
|-----------|---------|
| **Time** | Max Tolerable Disruption (MTD), RTO, RPO |
| **Financial** | Maximum financial loss threshold |
| **Customer** | Impact level, max customers affected |
| **Reputational** | Severity, regulatory notification triggers |

Breach detection uses a traffic-light system: 🟢 Within (<75%) · 🟡 Approaching (75-100%) · 🔴 Breached (>100%)

### 3. Scenario Testing Framework

**6 pre-built severe-but-plausible scenarios** with phased escalation timelines:

| # | Scenario | Severity | Duration | Key Test |
|---|----------|----------|----------|----------|
| 1 | 🔒 Ransomware Attack | Critical | 72h | Cyber recovery and data integrity |
| 2 | ☁️ Cloud Provider Outage | Critical | 24h | Third-party concentration risk |
| 3 | 🏢 Supplier Insolvency | High | 72h | Substitutability and migration |
| 4 | 🦠 Pandemic Disruption | High | 672h | Key person and workforce resilience |
| 5 | ⚡ Data Centre Failure | Critical | 48h | DR failover and RPO validation |
| 6 | 🌊 Compound Event | Extreme | 36h | Concurrent incident response |

Each simulation produces: cascading failure analysis, tolerance breach assessment, gap identification, and actionable recommendations.

### 4. Resilience Scorer

Maturity assessment across **four regulatory frameworks**:

| Framework | Jurisdiction | Pillars Assessed |
|-----------|-------------|-----------------|
| **DORA** | EU | 5 pillars (Art. 5-45) |
| **FINMA** | Switzerland | 7 pillars (Cm 10-75) |
| **PRA SS1/21** | UK | 5 pillars (Sections 5-8) |
| **BCBS 516** | Global | 6 pillars (P1-P12) |

Scoring scale: 1 (Initial) → 2 (Developing) → 3 (Defined) → 4 (Managed) → 5 (Optimised)

### 5. Incident Tracker

Full incident lifecycle management with board-level reporting:

- Severity classification (P1-P4) and root cause categorisation
- Impact tolerance breach flagging
- Lessons learned database with remediation action tracking
- Trend analysis and recurring pattern detection
- Auto-generated key messages for board reporting

---

## 📋 Regulatory Alignment

| Capability | DORA | FINMA | PRA | BCBS |
|---|---|---|---|---|
| Critical function identification | Art. 8 | Cm 31-35 | 5.1-5.3 | P3 |
| Dependency mapping | Art. 8-9 | Cm 36-40 | 5.4-5.6 | P4 |
| Impact tolerances | Art. 11 | Cm 41-45 | 6.1-6.4 | P5 |
| Scenario testing | Art. 26-27 | Cm 50-55 | 7.1-7.5 | P7 |
| Incident management | Art. 17-23 | Cm 60-65 | 8.1-8.3 | P9 |
| Third-party oversight | Art. 28-44 | Cm 70-75 | 9.1-9.4 | P10 |

> See [docs/REGULATORY_MAPPING.md](docs/REGULATORY_MAPPING.md) for detailed mapping.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.9+, NetworkX, Pandas, NumPy |
| **Visualisation** | Matplotlib, Plotly, Chart.js |
| **Dashboard** | Streamlit (Python), HTML/CSS/JS (Netlify) |
| **Data** | JSON configuration, graph-based modelling |

---

## 👤 Author

**Saranne Ndamba**
- MSc Finance & Investment Management — University of Salford
- Operational Resilience · Business Continuity · Non-Financial Risk
- [LinkedIn](https://linkedin.com/in/sarannendamba) · [Portfolio](https://anne71-cloud.github.io/Saranne-portfolio)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
