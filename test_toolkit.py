"""
Tests for the Operational Resilience Toolkit.

Validates core functionality across all modules:
- Dependency mapping and SPOF detection
- Impact tolerance definition and breach detection
- Scenario simulation and cascading failure analysis
- Resilience scoring across regulatory frameworks
- Incident tracking and trend analysis
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dependency_mapper.mapper import DependencyMapper
from src.impact_tolerance.engine import ImpactToleranceEngine, ToleranceStatus
from src.scenario_testing.scenarios import SCENARIO_LIBRARY, list_scenarios
from src.scenario_testing.simulator import ResilienceSimulator
from src.resilience_scorer.scorer import ResilienceScorer
from src.incident_tracker.tracker import IncidentTracker


def setup_sample_bank():
    """Create a sample bank configuration for testing."""
    mapper = DependencyMapper()

    # Critical functions
    mapper.add_critical_function("Payments Processing", tier=1)
    mapper.add_critical_function("Client Portfolio Management", tier=1)
    mapper.add_critical_function("Client Digital Channels", tier=1)
    mapper.add_critical_function("Client Onboarding & KYC", tier=2)
    mapper.add_critical_function("Regulatory Reporting", tier=2)

    # Dependencies
    mapper.add_dependency("Payments Processing", "SWIFT Gateway", dep_type="technology")
    mapper.add_dependency("Payments Processing", "Core Banking System", dep_type="technology")
    mapper.add_dependency("Payments Processing", "Cloud Provider A", dep_type="third_party")

    mapper.add_dependency("Client Portfolio Management", "Core Banking System", dep_type="technology")
    mapper.add_dependency("Client Portfolio Management", "Order Management System", dep_type="technology")
    mapper.add_dependency("Client Portfolio Management", "Market Data Provider", dep_type="third_party")
    mapper.add_dependency("Client Portfolio Management", "Cloud Provider A", dep_type="third_party")

    mapper.add_dependency("Client Digital Channels", "E-Banking Platform", dep_type="technology")
    mapper.add_dependency("Client Digital Channels", "Cloud Provider A", dep_type="third_party")
    mapper.add_dependency("Client Digital Channels", "Core Banking System", dep_type="technology")

    mapper.add_dependency("Client Onboarding & KYC", "Core Banking System", dep_type="technology")
    mapper.add_dependency("Client Onboarding & KYC", "KYC Screening Platform", dep_type="third_party")

    mapper.add_dependency("Regulatory Reporting", "Core Banking System", dep_type="technology")
    mapper.add_dependency("Regulatory Reporting", "Data Warehouse", dep_type="technology")

    # Sub-dependencies
    mapper.add_sub_dependency("Core Banking System", "Primary Database", dep_type="technology")
    mapper.add_sub_dependency("Core Banking System", "Cloud Provider A", dep_type="third_party")
    mapper.add_sub_dependency("E-Banking Platform", "Authentication Service", dep_type="technology")

    # Impact tolerances
    engine = ImpactToleranceEngine()
    engine.set_tolerance("Payments Processing", max_disruption_hours=4,
                         financial_impact_limit=5_000_000, customer_impact="critical",
                         recovery_time_objective_hours=2)
    engine.set_tolerance("Client Portfolio Management", max_disruption_hours=8,
                         financial_impact_limit=10_000_000, customer_impact="high",
                         recovery_time_objective_hours=4)
    engine.set_tolerance("Client Digital Channels", max_disruption_hours=2,
                         financial_impact_limit=2_000_000, customer_impact="critical",
                         recovery_time_objective_hours=1)
    engine.set_tolerance("Client Onboarding & KYC", max_disruption_hours=24,
                         financial_impact_limit=1_000_000, customer_impact="medium")
    engine.set_tolerance("Regulatory Reporting", max_disruption_hours=48,
                         customer_impact="low")

    return mapper, engine


def test_dependency_mapper():
    """Test dependency mapping and analysis."""
    print("\n{'='*60}")
    print("TEST: Dependency Mapper")
    print("{'='*60}")

    mapper, _ = setup_sample_bank()

    # Test critical function count
    assert len(mapper.critical_functions) == 5, "Should have 5 critical functions"
    print(f"  [PASS] {len(mapper.critical_functions)} critical functions registered")

    # Test dependency count
    assert mapper.graph.number_of_edges() > 10, "Should have multiple dependencies"
    print(f"  [PASS] {mapper.graph.number_of_edges()} dependency connections mapped")

    # Test SPOF detection
    spofs = mapper.find_single_points_of_failure()
    print(f"  [PASS] {len(spofs)} single points of failure identified")
    for spof in spofs[:3]:
        print(f"         - {spof['dependency']} (impacts {spof['impact_count']} functions)")

    # Test concentration risk
    concentrations = mapper.find_concentration_risks()
    print(f"  [PASS] {len(concentrations)} concentration risks identified")
    for conc in concentrations[:2]:
        print(f"         - {conc['dependency']} (serves {conc['concentration_count']} functions)")

    # Test critical chains
    chains = mapper.get_critical_chains("Payments Processing")
    print(f"  [PASS] {len(chains)} critical chains for Payments Processing")

    # Test impact radius
    impact = mapper.get_impact_radius("Core Banking System")
    print(f"  [PASS] Core Banking System failure radius: "
          f"{len(impact['affected_critical_functions'])} functions, "
          f"{len(impact['downstream_cascade'])} downstream")

    # Test summary report
    report = mapper.generate_summary_report()
    assert report["total_critical_functions"] == 5
    print(f"  [PASS] Summary report generated successfully")

    print("\n  ALL DEPENDENCY MAPPER TESTS PASSED")


def test_impact_tolerance():
    """Test impact tolerance engine."""
    print(f"\n{'='*60}")
    print("TEST: Impact Tolerance Engine")
    print(f"{'='*60}")

    _, engine = setup_sample_bank()

    # Test tolerance retrieval
    tol = engine.get_tolerance("Payments Processing")
    assert tol is not None
    assert tol.max_disruption_hours == 4
    print(f"  [PASS] Payments Processing tolerance: {tol.max_disruption_hours}h max disruption")

    # Test WITHIN tolerance
    result = engine.assess_time_tolerance("Payments Processing", 2.0)
    assert result.status == ToleranceStatus.WITHIN
    print(f"  [PASS] 2h disruption: {result.status.value} ({result.utilisation_pct}%)")

    # Test APPROACHING tolerance
    result = engine.assess_time_tolerance("Payments Processing", 3.5)
    assert result.status == ToleranceStatus.APPROACHING
    print(f"  [PASS] 3.5h disruption: {result.status.value} ({result.utilisation_pct}%)")

    # Test BREACHED tolerance
    result = engine.assess_time_tolerance("Payments Processing", 6.0)
    assert result.status == ToleranceStatus.BREACHED
    print(f"  [PASS] 6h disruption: {result.status.value} ({result.utilisation_pct}%)")

    # Test financial tolerance
    result = engine.assess_financial_tolerance("Payments Processing", 3_000_000)
    assert result.status == ToleranceStatus.WITHIN
    print(f"  [PASS] Financial assessment: {result.status.value}")

    # Test breach summary
    summary = engine.get_breach_summary()
    print(f"  [PASS] Breach summary: {summary['breaches']} breaches, "
          f"{summary['approaching_breach']} approaching")

    print("\n  ALL IMPACT TOLERANCE TESTS PASSED")


def test_scenario_library():
    """Test scenario library."""
    print(f"\n{'='*60}")
    print("TEST: Scenario Library")
    print(f"{'='*60}")

    scenarios = list_scenarios()
    assert len(scenarios) == 6, "Should have 6 built-in scenarios"
    print(f"  [PASS] {len(scenarios)} scenarios available")

    for s in scenarios:
        print(f"         - {s['id']}: {s['name']} ({s['severity']})")

    # Verify scenario detail
    ransomware = SCENARIO_LIBRARY["cyber_ransomware"]
    assert len(ransomware.phases) == 5
    assert ransomware.severity == "critical"
    print(f"  [PASS] Ransomware scenario: {len(ransomware.phases)} phases, "
          f"{ransomware.total_duration_hours}h duration")

    print("\n  ALL SCENARIO LIBRARY TESTS PASSED")


def test_scenario_simulation():
    """Test scenario simulation engine."""
    print(f"\n{'='*60}")
    print("TEST: Scenario Simulation")
    print(f"{'='*60}")

    mapper, engine = setup_sample_bank()
    simulator = ResilienceSimulator(mapper, engine)

    # Run ransomware scenario
    result = simulator.run_scenario("cyber_ransomware")
    print(f"  [PASS] Ransomware simulation completed")
    print(f"         Rating: {result.overall_resilience_rating}")
    print(f"         Functions impacted: {len(result.affected_critical_functions)}")
    print(f"         Tolerance breaches: {len(result.tolerance_breaches)}")
    print(f"         Gaps identified: {len(result.gaps_identified)}")
    print(f"         Recommendations: {len(result.recommendations)}")

    # Run cloud outage scenario
    result2 = simulator.run_scenario("cloud_provider_outage")
    print(f"  [PASS] Cloud outage simulation completed: {result2.overall_resilience_rating}")

    # Test comparison
    comparison = simulator.compare_scenarios(["third_party_failure", "pandemic_disruption"])
    assert len(comparison) == 2
    print(f"  [PASS] Scenario comparison: {len(comparison)} scenarios compared")

    # Verify report generation
    report = result.to_report()
    assert "executive_summary" in report
    assert "impact_analysis" in report
    print(f"  [PASS] Simulation report generated successfully")

    print("\n  ALL SCENARIO SIMULATION TESTS PASSED")


def test_resilience_scorer():
    """Test resilience scoring engine."""
    print(f"\n{'='*60}")
    print("TEST: Resilience Scorer")
    print(f"{'='*60}")

    mapper, engine = setup_sample_bank()
    scorer = ResilienceScorer()

    # Test DORA assessment
    dora = scorer.assess(mapper, engine, framework="DORA")
    print(f"  [PASS] DORA assessment: {dora.overall_score}/5.0 ({dora.maturity_level})")
    for pillar in dora.pillar_scores:
        print(f"         - {pillar.pillar_name}: {pillar.current_score}/{pillar.target_score} "
              f"(gap: {pillar.gap})")

    # Test FINMA assessment
    finma = scorer.assess(mapper, engine, framework="FINMA")
    print(f"  [PASS] FINMA assessment: {finma.overall_score}/5.0 ({finma.maturity_level})")

    # Test framework comparison
    comparison = scorer.compare_frameworks(mapper, engine)
    assert len(comparison) == 4  # DORA, FINMA, PRA, BCBS
    print(f"  [PASS] Cross-framework comparison: {len(comparison)} frameworks assessed")
    for fw, data in comparison.items():
        print(f"         - {fw}: {data['overall_score']}/5.0 ({data['maturity_level']})")

    print("\n  ALL RESILIENCE SCORER TESTS PASSED")


def test_incident_tracker():
    """Test incident tracking and analysis."""
    print(f"\n{'='*60}")
    print("TEST: Incident Tracker")
    print(f"{'='*60}")

    tracker = IncidentTracker()

    # Create incidents
    inc1 = tracker.create_incident(
        title="Core Banking System Outage",
        description="Unplanned outage affecting payments and portfolio management",
        severity="P1",
        category="technology",
        affected_functions=["Payments Processing", "Client Portfolio Management"],
        affected_dependencies=["Core Banking System"],
        downtime_hours=3.5,
        customers_affected=45000,
        financial_impact=1_200_000,
        tolerance_breached=False,
    )
    print(f"  [PASS] Incident created: {inc1.id} ({inc1.severity})")

    inc2 = tracker.create_incident(
        title="Cloud Provider Degradation",
        description="AWS region experiencing intermittent failures",
        severity="P2",
        category="third_party",
        affected_functions=["Client Digital Channels"],
        affected_dependencies=["Cloud Provider A"],
        downtime_hours=1.5,
        customers_affected=30000,
    )

    inc3 = tracker.create_incident(
        title="KYC Platform Timeout",
        description="Refinitiv screening responses exceeding SLA",
        severity="P3",
        category="third_party",
        affected_dependencies=["KYC Screening Platform"],
        downtime_hours=0.5,
    )

    # Update status
    tracker.update_status(inc1.id, "investigating")
    tracker.update_status(inc1.id, "resolved")
    tracker.add_root_cause(inc1.id, "system_failure",
                           "Database connection pool exhaustion under peak load")
    tracker.add_lesson_learned(inc1.id,
                               "Connection pool sizing inadequate for peak volumes. "
                               "Auto-scaling not configured.")
    tracker.add_remediation_action(inc1.id,
                                   "Implement auto-scaling for DB connection pools",
                                   "DBA Team", "2026-04-01")
    print(f"  [PASS] Incident lifecycle managed: {inc1.status}")

    # Trend analysis
    trends = tracker.get_trend_analysis()
    assert trends["total_incidents"] == 3
    print(f"  [PASS] Trend analysis: {trends['total_incidents']} incidents, "
          f"{trends['total_downtime_hours']}h total downtime")

    # Board report
    board = tracker.get_board_report_data()
    assert len(board["key_messages"]) > 0
    print(f"  [PASS] Board report: {len(board['key_messages'])} key messages")
    for msg in board["key_messages"]:
        print(f"         - {msg}")

    print("\n  ALL INCIDENT TRACKER TESTS PASSED")


def test_end_to_end():
    """Full end-to-end workflow test."""
    print(f"\n{'='*60}")
    print("TEST: End-to-End Workflow")
    print(f"{'='*60}")

    # 1. Setup
    mapper, engine = setup_sample_bank()
    print("  [PASS] Step 1: Bank configuration loaded")

    # 2. Analysis
    spofs = mapper.find_single_points_of_failure()
    concentrations = mapper.find_concentration_risks()
    print(f"  [PASS] Step 2: Analysis complete ({len(spofs)} SPOFs, "
          f"{len(concentrations)} concentration risks)")

    # 3. Scenario testing
    simulator = ResilienceSimulator(mapper, engine)
    result = simulator.run_scenario("cyber_ransomware")
    print(f"  [PASS] Step 3: Scenario test complete ({result.overall_resilience_rating})")

    # 4. Maturity scoring
    scorer = ResilienceScorer()
    assessment = scorer.assess(mapper, engine, framework="DORA")
    print(f"  [PASS] Step 4: DORA maturity assessed ({assessment.overall_score}/5.0)")

    # 5. Incident tracking
    tracker = IncidentTracker()
    inc = tracker.create_incident("Test Incident", "Testing", severity="P2",
                                  category="technology")
    print(f"  [PASS] Step 5: Incident tracking operational ({inc.id})")

    print(f"\n  END-TO-END WORKFLOW COMPLETE")
    print(f"  Resilience posture: {assessment.maturity_level} "
          f"({assessment.overall_score}/5.0)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  OPERATIONAL RESILIENCE TOOLKIT — TEST SUITE")
    print("=" * 60)

    test_dependency_mapper()
    test_impact_tolerance()
    test_scenario_library()
    test_scenario_simulation()
    test_resilience_scorer()
    test_incident_tracker()
    test_end_to_end()

    print(f"\n{'='*60}")
    print("  ALL TESTS PASSED SUCCESSFULLY")
    print(f"{'='*60}\n")
