# Framework Methodology

## Operational Resilience Lifecycle

This toolkit implements the full operational resilience lifecycle:

1. **Identify** — Map critical functions and their end-to-end dependencies
2. **Define** — Set impact tolerances across time, financial, customer, and reputational dimensions
3. **Test** — Execute severe-but-plausible scenarios to validate recovery capabilities
4. **Assess** — Score maturity against regulatory frameworks (DORA, FINMA, PRA, BCBS)
5. **Track** — Manage incidents, root causes, and lessons learned
6. **Improve** — Drive continuous improvement through gap analysis and remediation

## Dependency Mapping Methodology

Dependencies are modelled as directed graphs using NetworkX. Critical functions are root nodes, and dependencies form chains that represent end-to-end service delivery paths.

**Analysis capabilities:**
- Single Point of Failure (SPOF) detection via path analysis
- Concentration risk identification via in-degree analysis
- Critical chain mapping via depth-first traversal
- Blast radius calculation via ancestor/descendant analysis

## Impact Tolerance Methodology

Impact tolerances are defined across four dimensions:
- **Time**: Maximum Tolerable Disruption (MTD), Recovery Time Objective (RTO), Recovery Point Objective (RPO)
- **Financial**: Maximum financial loss threshold
- **Customer**: Maximum customer impact level and count
- **Reputational**: Severity assessment and regulatory reporting triggers

Breach detection uses a traffic-light system: Green (<75%), Amber (75-100%), Red (>100%).

## Scenario Testing Methodology

Scenarios follow a phased approach with escalating severity:
1. Initial trigger event
2. Escalation and cascading failures
3. Containment and workaround activation
4. Recovery and restoration

Each phase defines affected dependency types and severity multipliers. The simulator propagates failures through the dependency graph to estimate total impact.

## Maturity Scoring Methodology

Maturity is assessed on a 1-5 scale per pillar:
- 1 = Initial (ad hoc)
- 2 = Developing (some processes)
- 3 = Defined (standardised)
- 4 = Managed (measured and monitored)
- 5 = Optimised (continuous improvement)

Auto-scoring uses heuristics based on configuration completeness. Manual override is supported for accurate assessment.

## Author

Saranne Ndamba — MSc Finance & Investment Management
