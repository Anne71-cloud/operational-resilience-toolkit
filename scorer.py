"""
Resilience Scorer — Maturity assessment against regulatory frameworks.

Scoring: 1=Initial, 2=Developing, 3=Defined, 4=Managed, 5=Optimised
Frameworks: DORA, FINMA, PRA SS1/21, BCBS 516
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..dependency_mapper.mapper import DependencyMapper
from ..impact_tolerance.engine import ImpactToleranceEngine


FRAMEWORK_PILLARS = {
    "DORA": [
        {"name": "ICT Risk Management", "ref": "Art. 5-16", "target": 4.0},
        {"name": "ICT Incident Reporting", "ref": "Art. 17-23", "target": 4.0},
        {"name": "Digital Operational Resilience Testing", "ref": "Art. 24-27", "target": 4.0},
        {"name": "ICT Third-Party Risk", "ref": "Art. 28-44", "target": 4.0},
        {"name": "Information Sharing", "ref": "Art. 45", "target": 3.0},
    ],
    "FINMA": [
        {"name": "Governance & Organisation", "ref": "Cm 10-20", "target": 4.0},
        {"name": "Critical Function Identification", "ref": "Cm 31-35", "target": 4.0},
        {"name": "Dependency Mapping", "ref": "Cm 36-40", "target": 4.0},
        {"name": "Impact Tolerances", "ref": "Cm 41-45", "target": 4.0},
        {"name": "Scenario Testing", "ref": "Cm 50-55", "target": 4.0},
        {"name": "Incident Management", "ref": "Cm 60-65", "target": 4.0},
        {"name": "Third-Party Management", "ref": "Cm 70-75", "target": 4.0},
    ],
    "PRA": [
        {"name": "Important Business Services", "ref": "SS1/21 5.1-5.3", "target": 4.0},
        {"name": "Mapping", "ref": "SS1/21 5.4-5.6", "target": 4.0},
        {"name": "Impact Tolerances", "ref": "SS1/21 6.1-6.4", "target": 4.0},
        {"name": "Scenario Testing", "ref": "SS1/21 7.1-7.5", "target": 4.0},
        {"name": "Self-Assessment", "ref": "SS1/21 8.1-8.3", "target": 3.5},
    ],
    "BCBS": [
        {"name": "Governance", "ref": "P1-P2", "target": 4.0},
        {"name": "Critical Operations", "ref": "P3-P4", "target": 4.0},
        {"name": "Tolerances", "ref": "P5-P6", "target": 4.0},
        {"name": "Testing", "ref": "P7-P8", "target": 4.0},
        {"name": "Incident & Communication", "ref": "P9-P10", "target": 3.5},
        {"name": "Third-Party Dependencies", "ref": "P11-P12", "target": 4.0},
    ],
}


@dataclass
class PillarScore:
    pillar_name: str
    framework: str
    reference: str
    current_score: float
    target_score: float
    gap: float = 0.0
    evidence: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.gap = round(self.target_score - self.current_score, 1)


@dataclass
class ResilienceAssessment:
    framework: str
    assessment_date: str = field(default_factory=lambda: datetime.now().isoformat())
    pillar_scores: list[PillarScore] = field(default_factory=list)
    overall_score: float = 0.0
    overall_target: float = 0.0
    maturity_level: str = ""
    critical_gaps: list[str] = field(default_factory=list)


class ResilienceScorer:
    """Assesses organisational resilience maturity against regulatory frameworks."""

    def __init__(self):
        self.assessments: list[ResilienceAssessment] = []

    def assess(self, mapper: DependencyMapper,
               tolerance_engine: ImpactToleranceEngine,
               framework: str = "DORA",
               manual_scores: dict = None) -> ResilienceAssessment:
        """
        Run a maturity assessment against a regulatory framework.

        If manual_scores not provided, auto-scores based on what's been
        configured in the mapper and tolerance engine.
        """
        if framework not in FRAMEWORK_PILLARS:
            raise ValueError(f"Unknown framework: {framework}. "
                           f"Available: {list(FRAMEWORK_PILLARS.keys())}")

        pillars = FRAMEWORK_PILLARS[framework]
        scores = []

        for pillar in pillars:
            if manual_scores and pillar["name"] in manual_scores:
                current = manual_scores[pillar["name"]]
            else:
                current = self._auto_score_pillar(pillar["name"], mapper, tolerance_engine)

            evidence = self._gather_evidence(pillar["name"], mapper, tolerance_engine)
            actions = self._suggest_actions(pillar["name"], current, pillar["target"])

            scores.append(PillarScore(
                pillar_name=pillar["name"],
                framework=framework,
                reference=pillar["ref"],
                current_score=current,
                target_score=pillar["target"],
                evidence=evidence,
                actions=actions,
            ))

        overall = round(sum(s.current_score for s in scores) / len(scores), 1) if scores else 0
        overall_target = round(sum(s.target_score for s in scores) / len(scores), 1) if scores else 0

        if overall >= 4.0:
            maturity = "Managed"
        elif overall >= 3.0:
            maturity = "Defined"
        elif overall >= 2.0:
            maturity = "Developing"
        else:
            maturity = "Initial"

        critical_gaps = [
            f"{s.pillar_name}: {s.current_score}/{s.target_score} (gap: {s.gap})"
            for s in scores if s.gap >= 2.0
        ]

        assessment = ResilienceAssessment(
            framework=framework,
            pillar_scores=scores,
            overall_score=overall,
            overall_target=overall_target,
            maturity_level=maturity,
            critical_gaps=critical_gaps,
        )
        self.assessments.append(assessment)
        return assessment

    def _auto_score_pillar(self, pillar_name: str,
                           mapper: DependencyMapper,
                           engine: ImpactToleranceEngine) -> float:
        """Auto-score based on what's configured. Conservative scoring."""
        lower = pillar_name.lower()

        if "critical" in lower or "important" in lower or "operations" in lower:
            count = len(mapper.critical_functions)
            if count >= 5:
                return 3.5
            elif count >= 2:
                return 2.5
            elif count >= 1:
                return 2.0
            return 1.0

        if "mapping" in lower or "dependency" in lower:
            edges = mapper.graph.number_of_edges()
            if edges >= 15:
                return 3.5
            elif edges >= 5:
                return 2.5
            elif edges >= 1:
                return 2.0
            return 1.0

        if "tolerance" in lower:
            count = len(engine.tolerances)
            cf_count = max(len(mapper.critical_functions), 1)
            coverage = count / cf_count
            if coverage >= 0.9:
                return 3.5
            elif coverage >= 0.5:
                return 2.5
            elif coverage > 0:
                return 2.0
            return 1.0

        if "testing" in lower or "scenario" in lower:
            return 2.0  # Conservative — need evidence of testing

        if "incident" in lower:
            return 2.0  # Conservative

        if "third" in lower or "ict" in lower:
            third_party_deps = [
                n for n, d in mapper.graph.nodes(data=True)
                if d.get("dep_type") == "third_party"
            ]
            if len(third_party_deps) >= 3:
                return 2.5
            elif len(third_party_deps) >= 1:
                return 2.0
            return 1.5

        return 2.0

    def _gather_evidence(self, pillar_name: str,
                         mapper: DependencyMapper,
                         engine: ImpactToleranceEngine) -> list[str]:
        """Gather evidence supporting the score."""
        evidence = []
        lower = pillar_name.lower()

        if "critical" in lower or "important" in lower:
            evidence.append(f"{len(mapper.critical_functions)} critical functions identified")

        if "mapping" in lower or "dependency" in lower:
            evidence.append(f"{mapper.graph.number_of_edges()} dependency connections mapped")
            spofs = mapper.find_single_points_of_failure()
            evidence.append(f"{len(spofs)} single points of failure identified")

        if "tolerance" in lower:
            evidence.append(f"{len(engine.tolerances)} impact tolerances defined")

        return evidence if evidence else ["No automated evidence available"]

    def _suggest_actions(self, pillar_name: str, current: float, target: float) -> list[str]:
        """Suggest improvement actions to close the gap."""
        gap = target - current
        if gap <= 0:
            return ["Maintain current maturity level. Continue periodic review."]

        actions = []
        if current < 2.0:
            actions.append(f"Establish formal {pillar_name.lower()} processes and documentation.")
        if current < 3.0:
            actions.append(f"Standardise {pillar_name.lower()} approach across all jurisdictions.")
        if current < 4.0:
            actions.append(f"Implement regular measurement and monitoring for {pillar_name.lower()}.")
            actions.append("Conduct independent review or internal audit.")
        if gap >= 2.0:
            actions.append("PRIORITY: Significant gap. Recommend dedicated project and board oversight.")

        return actions

    def generate_heatmap_data(self) -> list[dict]:
        """Generate data for a compliance heatmap across frameworks."""
        heatmap = []
        for fw_name, pillars in FRAMEWORK_PILLARS.items():
            for pillar in pillars:
                heatmap.append({
                    "framework": fw_name,
                    "pillar": pillar["name"],
                    "reference": pillar["ref"],
                    "target": pillar["target"],
                })
        return heatmap

    def compare_frameworks(self, mapper: DependencyMapper,
                           engine: ImpactToleranceEngine) -> dict:
        """Run assessments across all frameworks and compare."""
        results = {}
        for fw in FRAMEWORK_PILLARS:
            assessment = self.assess(mapper, engine, framework=fw)
            results[fw] = {
                "overall_score": assessment.overall_score,
                "maturity_level": assessment.maturity_level,
                "pillars": len(assessment.pillar_scores),
                "critical_gaps": len(assessment.critical_gaps),
            }
        return results
