"""
Resilience Simulator — Cascading failure simulation engine.

Simulates the propagation of disruptions through dependency chains,
estimating recovery timelines and comparing against impact tolerances.

This module brings together the Dependency Mapper, Impact Tolerance Engine,
and Scenario Library to execute end-to-end resilience tests.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..dependency_mapper.mapper import DependencyMapper
from ..impact_tolerance.engine import ImpactToleranceEngine, ToleranceStatus
from .scenarios import Scenario, SCENARIO_LIBRARY


@dataclass
class SimulationResult:
    """Complete result of a scenario simulation run."""
    scenario_name: str
    scenario_id: str
    run_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Impact summary
    affected_critical_functions: list[str] = field(default_factory=list)
    affected_dependencies: list[str] = field(default_factory=list)
    cascading_failures: list[dict] = field(default_factory=list)
    
    # Recovery analysis
    estimated_recovery_hours: float = 0.0
    tolerance_breaches: list[dict] = field(default_factory=list)
    tolerance_near_misses: list[dict] = field(default_factory=list)
    
    # Phase-by-phase timeline
    phase_timeline: list[dict] = field(default_factory=list)
    
    # Gaps and recommendations
    gaps_identified: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    
    # Overall assessment
    overall_resilience_rating: str = ""  # pass, conditional_pass, fail
    
    def to_report(self) -> dict:
        """Generate a structured report from the simulation results."""
        return {
            "executive_summary": {
                "scenario": self.scenario_name,
                "run_date": self.run_timestamp,
                "overall_rating": self.overall_resilience_rating,
                "critical_functions_impacted": len(self.affected_critical_functions),
                "tolerance_breaches": len(self.tolerance_breaches),
                "estimated_recovery_hours": self.estimated_recovery_hours,
            },
            "impact_analysis": {
                "affected_functions": self.affected_critical_functions,
                "cascading_failures": self.cascading_failures,
                "total_dependencies_impacted": len(self.affected_dependencies),
            },
            "tolerance_assessment": {
                "breaches": self.tolerance_breaches,
                "near_misses": self.tolerance_near_misses,
            },
            "timeline": self.phase_timeline,
            "gaps_and_recommendations": {
                "gaps": self.gaps_identified,
                "recommendations": self.recommendations,
            },
        }


class ResilienceSimulator:
    """
    Executes scenario-based resilience testing by simulating disruption
    propagation through dependency graphs and comparing outcomes against
    defined impact tolerances.
    """
    
    def __init__(self, mapper: DependencyMapper, tolerance_engine: ImpactToleranceEngine):
        self.mapper = mapper
        self.tolerance_engine = tolerance_engine
        self.simulation_history: list[SimulationResult] = []
    
    def run_scenario(self, scenario_key: str) -> SimulationResult:
        """
        Execute a full scenario simulation.
        
        1. Load the scenario definition
        2. Identify which dependencies are directly affected
        3. Simulate cascading failures through the dependency graph
        4. Estimate recovery timelines per critical function
        5. Compare against impact tolerances
        6. Generate gaps and recommendations
        """
        scenario = SCENARIO_LIBRARY.get(scenario_key)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_key}. "
                           f"Available: {list(SCENARIO_LIBRARY.keys())}")
        
        result = SimulationResult(
            scenario_name=scenario.name,
            scenario_id=scenario.id,
        )
        
        # Step 1: Identify directly affected dependencies
        directly_affected = self._identify_affected_dependencies(scenario)
        result.affected_dependencies = directly_affected
        
        # Step 2: Simulate cascading failures
        cascade = self._simulate_cascading_failures(directly_affected, scenario)
        result.cascading_failures = cascade["failure_chain"]
        result.affected_critical_functions = cascade["impacted_functions"]
        
        # Step 3: Build phase timeline
        result.phase_timeline = self._build_phase_timeline(scenario, cascade)
        
        # Step 4: Estimate recovery and check tolerances
        recovery = self._assess_recovery(scenario, cascade)
        result.estimated_recovery_hours = recovery["estimated_hours"]
        result.tolerance_breaches = recovery["breaches"]
        result.tolerance_near_misses = recovery["near_misses"]
        
        # Step 5: Generate gaps and recommendations
        analysis = self._generate_gap_analysis(scenario, cascade, recovery)
        result.gaps_identified = analysis["gaps"]
        result.recommendations = analysis["recommendations"]
        
        # Step 6: Overall rating
        if len(result.tolerance_breaches) == 0:
            result.overall_resilience_rating = "pass"
        elif len(result.tolerance_breaches) <= 2:
            result.overall_resilience_rating = "conditional_pass"
        else:
            result.overall_resilience_rating = "fail"
        
        self.simulation_history.append(result)
        return result
    
    def _identify_affected_dependencies(self, scenario: Scenario) -> list[str]:
        """Identify which mapped dependencies match the scenario's affected types."""
        affected = []
        
        for dep_name, dep_data in self.mapper.graph.nodes(data=True):
            if dep_data.get("node_type") != "dependency":
                continue
            
            dep_type = dep_data.get("dep_type", "")
            if dep_type in scenario.primary_affected_types:
                affected.append(dep_name)
        
        # Also add any specifically named failures from scenario phases
        for phase in scenario.phases:
            for failure in phase.additional_failures:
                if failure in self.mapper.graph and failure not in affected:
                    affected.append(failure)
        
        return affected
    
    def _simulate_cascading_failures(self, directly_affected: list[str],
                                      scenario: Scenario) -> dict:
        """Simulate how failures cascade through the dependency graph."""
        failure_chain = []
        all_affected = set(directly_affected)
        impacted_functions = set()
        
        for dep in directly_affected:
            if dep not in self.mapper.graph:
                continue
            
            # Get the blast radius
            impact = self.mapper.get_impact_radius(dep)
            
            for cf in impact["affected_critical_functions"]:
                impacted_functions.add(cf)
            
            for downstream in impact["downstream_cascade"]:
                all_affected.add(downstream)
            
            failure_chain.append({
                "trigger": dep,
                "cascading_to": impact["downstream_cascade"],
                "functions_impacted": impact["affected_critical_functions"],
                "total_radius": impact["total_impact_radius"],
            })
        
        return {
            "failure_chain": failure_chain,
            "impacted_functions": list(impacted_functions),
            "total_affected_nodes": len(all_affected),
        }
    
    def _build_phase_timeline(self, scenario: Scenario, cascade: dict) -> list[dict]:
        """Build a detailed timeline of the scenario progression."""
        timeline = []
        
        for phase in scenario.phases:
            timeline.append({
                "phase": phase.phase_name,
                "hours_from_start": phase.hours_from_start,
                "description": phase.description,
                "severity_multiplier": phase.severity_multiplier,
                "affected_types": phase.affected_dep_types,
                "additional_failures": phase.additional_failures,
                "impacted_functions": cascade["impacted_functions"],
            })
        
        return timeline
    
    def _assess_recovery(self, scenario: Scenario, cascade: dict) -> dict:
        """Assess recovery timelines against impact tolerances."""
        breaches = []
        near_misses = []
        
        for cf_name in cascade["impacted_functions"]:
            tolerance = self.tolerance_engine.get_tolerance(cf_name)
            if not tolerance:
                breaches.append({
                    "function": cf_name,
                    "issue": "No impact tolerance defined",
                    "type": "governance_gap",
                })
                continue
            
            # Check time tolerance
            time_assessment = self.tolerance_engine.assess_time_tolerance(
                cf_name, scenario.estimated_recovery_hours
            )
            
            if time_assessment.status == ToleranceStatus.BREACHED:
                breaches.append({
                    "function": cf_name,
                    "dimension": "time",
                    "tolerance_hours": tolerance.max_disruption_hours,
                    "estimated_disruption_hours": scenario.estimated_recovery_hours,
                    "overshoot_hours": scenario.estimated_recovery_hours - tolerance.max_disruption_hours,
                    "details": time_assessment.breach_details,
                })
            elif time_assessment.status == ToleranceStatus.APPROACHING:
                near_misses.append({
                    "function": cf_name,
                    "dimension": "time",
                    "utilisation_pct": time_assessment.utilisation_pct,
                    "details": time_assessment.breach_details,
                })
        
        return {
            "estimated_hours": scenario.estimated_recovery_hours,
            "breaches": breaches,
            "near_misses": near_misses,
        }
    
    def _generate_gap_analysis(self, scenario: Scenario,
                                cascade: dict, recovery: dict) -> dict:
        """Generate actionable gaps and recommendations."""
        gaps = []
        recommendations = []
        
        # Gap: Tolerance breaches
        for breach in recovery["breaches"]:
            if breach.get("type") == "governance_gap":
                gaps.append(f"No impact tolerance defined for '{breach['function']}'")
                recommendations.append(
                    f"Define and approve impact tolerances for '{breach['function']}' "
                    f"covering time, financial, and customer dimensions."
                )
            else:
                gaps.append(
                    f"'{breach['function']}' recovery time ({breach['estimated_disruption_hours']}h) "
                    f"exceeds tolerance ({breach['tolerance_hours']}h) by {breach['overshoot_hours']}h"
                )
                recommendations.append(
                    f"Enhance recovery capabilities for '{breach['function']}' to achieve "
                    f"recovery within {breach['tolerance_hours']}h. Consider: redundancy, "
                    f"automated failover, pre-positioned manual workarounds."
                )
        
        # Gap: SPOFs in affected chains
        spofs = self.mapper.find_single_points_of_failure()
        affected_spofs = [
            s for s in spofs
            if any(f in cascade["impacted_functions"] for f in s["impacted_functions"])
        ]
        for spof in affected_spofs:
            gaps.append(
                f"Single point of failure: '{spof['dependency']}' "
                f"(affects {', '.join(spof['impacted_functions'])})"
            )
            recommendations.append(
                f"Eliminate SPOF on '{spof['dependency']}': implement redundancy, "
                f"alternative supplier, or automated failover path."
            )
        
        # Gap: Concentration risks
        concentrations = self.mapper.find_concentration_risks()
        for conc in concentrations:
            gaps.append(
                f"Concentration risk: '{conc['dependency']}' serves "
                f"{conc['concentration_count']} critical functions"
            )
            recommendations.append(
                f"Reduce concentration on '{conc['dependency']}': diversify across "
                f"multiple providers or implement isolation boundaries."
            )
        
        # Scenario-specific recommendations
        if scenario.requires_manual_workaround:
            recommendations.append(
                "Develop, document, and regularly test manual workaround procedures "
                "for all Tier 1 critical functions."
            )
        
        if scenario.external_support_required:
            recommendations.append(
                "Pre-negotiate retainer agreements with external incident response "
                "providers. Conduct joint exercises annually."
            )
        
        if scenario.data_loss_risk:
            recommendations.append(
                "Review and reduce RPO for all critical functions. Implement "
                "continuous data replication where RPO < 1 hour."
            )
        
        return {
            "gaps": gaps,
            "recommendations": recommendations,
        }
    
    def compare_scenarios(self, scenario_keys: list[str]) -> list[dict]:
        """Run multiple scenarios and compare their impact."""
        comparisons = []
        
        for key in scenario_keys:
            result = self.run_scenario(key)
            comparisons.append({
                "scenario": result.scenario_name,
                "rating": result.overall_resilience_rating,
                "functions_impacted": len(result.affected_critical_functions),
                "tolerance_breaches": len(result.tolerance_breaches),
                "recovery_hours": result.estimated_recovery_hours,
                "gaps_found": len(result.gaps_identified),
            })
        
        return comparisons
