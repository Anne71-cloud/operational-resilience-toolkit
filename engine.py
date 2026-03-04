"""
Impact Tolerance Engine — Define and monitor maximum tolerable disruption levels.

Implements the concept of impact tolerances as defined by:
- DORA Art. 11: Setting impact tolerances for ICT disruptions
- FINMA Cm 41-45: Defining acceptable disruption levels
- PRA SS1/21 6.1-6.4: Impact tolerances for important business services
- BCBS 516 P5: Setting tolerances for disruption

Impact tolerances are the maximum tolerable level of disruption to a critical
function, measured across multiple dimensions: time, financial, customer, and
reputational impact.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ImpactSeverity(Enum):
    """Severity classification for impact assessments."""
    NEGLIGIBLE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class ToleranceStatus(Enum):
    """Current status relative to defined tolerance."""
    WITHIN = "within_tolerance"
    APPROACHING = "approaching_breach"  # >75% of tolerance
    BREACHED = "tolerance_breached"
    NOT_SET = "tolerance_not_defined"


@dataclass
class ImpactTolerance:
    """
    Defines the maximum tolerable disruption for a critical function.
    
    Multi-dimensional tolerance covering time, financial, customer, and
    reputational impact, aligned with regulatory expectations.
    """
    function_name: str
    
    # Time-based tolerances
    max_disruption_hours: float = 0.0          # Maximum acceptable downtime
    recovery_time_objective_hours: float = 0.0  # Target recovery time (RTO)
    recovery_point_objective_hours: float = 0.0 # Maximum data loss window (RPO)
    
    # Financial tolerances
    financial_impact_limit: float = 0.0         # Max financial loss (CHF/EUR/USD)
    revenue_at_risk_per_hour: float = 0.0       # Revenue impact per hour of disruption
    
    # Customer impact tolerances
    customer_impact: str = "medium"              # low, medium, high, critical
    max_customers_affected: int = 0
    max_complaints_threshold: int = 0
    
    # Reputational tolerances
    reputational_severity: str = "medium"        # low, medium, high, critical
    regulatory_reporting_required: bool = False
    media_exposure_risk: str = "low"
    
    # Metadata
    approved_by: str = ""
    approval_date: str = ""
    review_frequency_months: int = 12
    last_reviewed: str = ""
    
    def to_dict(self) -> dict:
        return {
            "function_name": self.function_name,
            "time": {
                "max_disruption_hours": self.max_disruption_hours,
                "rto_hours": self.recovery_time_objective_hours,
                "rpo_hours": self.recovery_point_objective_hours,
            },
            "financial": {
                "max_loss": self.financial_impact_limit,
                "revenue_at_risk_per_hour": self.revenue_at_risk_per_hour,
            },
            "customer": {
                "impact_level": self.customer_impact,
                "max_affected": self.max_customers_affected,
            },
            "reputational": {
                "severity": self.reputational_severity,
                "regulatory_reporting": self.regulatory_reporting_required,
            },
        }


@dataclass
class ToleranceAssessment:
    """Result of assessing current state against defined tolerances."""
    function_name: str
    dimension: str  # time, financial, customer, reputational
    tolerance_value: float
    current_value: float
    utilisation_pct: float
    status: ToleranceStatus
    breach_details: str = ""
    assessed_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ImpactToleranceEngine:
    """
    Engine for defining, monitoring, and assessing impact tolerances
    across all critical functions.
    """
    
    def __init__(self):
        self.tolerances: dict[str, ImpactTolerance] = {}
        self.assessment_history: list[ToleranceAssessment] = []
    
    def set_tolerance(self, function_name: str, **kwargs) -> ImpactTolerance:
        """Define or update impact tolerance for a critical function."""
        tolerance = ImpactTolerance(function_name=function_name, **kwargs)
        self.tolerances[function_name] = tolerance
        return tolerance
    
    def get_tolerance(self, function_name: str) -> Optional[ImpactTolerance]:
        """Retrieve the impact tolerance for a critical function."""
        return self.tolerances.get(function_name)
    
    def assess_time_tolerance(self, function_name: str,
                               actual_disruption_hours: float) -> ToleranceAssessment:
        """
        Assess whether a disruption duration is within the defined time tolerance.
        
        Returns status: WITHIN, APPROACHING (>75%), or BREACHED.
        """
        tolerance = self.tolerances.get(function_name)
        if not tolerance or tolerance.max_disruption_hours == 0:
            return ToleranceAssessment(
                function_name=function_name,
                dimension="time",
                tolerance_value=0,
                current_value=actual_disruption_hours,
                utilisation_pct=0,
                status=ToleranceStatus.NOT_SET,
            )
        
        utilisation = (actual_disruption_hours / tolerance.max_disruption_hours) * 100
        
        if utilisation > 100:
            status = ToleranceStatus.BREACHED
            details = (f"BREACH: {actual_disruption_hours:.1f}h disruption exceeds "
                      f"{tolerance.max_disruption_hours:.1f}h tolerance by "
                      f"{actual_disruption_hours - tolerance.max_disruption_hours:.1f}h")
        elif utilisation > 75:
            status = ToleranceStatus.APPROACHING
            details = (f"WARNING: {utilisation:.0f}% of time tolerance consumed. "
                      f"{tolerance.max_disruption_hours - actual_disruption_hours:.1f}h remaining.")
        else:
            status = ToleranceStatus.WITHIN
            details = f"Within tolerance: {utilisation:.0f}% utilised."
        
        assessment = ToleranceAssessment(
            function_name=function_name,
            dimension="time",
            tolerance_value=tolerance.max_disruption_hours,
            current_value=actual_disruption_hours,
            utilisation_pct=round(utilisation, 1),
            status=status,
            breach_details=details,
        )
        self.assessment_history.append(assessment)
        return assessment
    
    def assess_financial_tolerance(self, function_name: str,
                                    actual_financial_impact: float) -> ToleranceAssessment:
        """Assess financial impact against defined tolerance."""
        tolerance = self.tolerances.get(function_name)
        if not tolerance or tolerance.financial_impact_limit == 0:
            return ToleranceAssessment(
                function_name=function_name,
                dimension="financial",
                tolerance_value=0,
                current_value=actual_financial_impact,
                utilisation_pct=0,
                status=ToleranceStatus.NOT_SET,
            )
        
        utilisation = (actual_financial_impact / tolerance.financial_impact_limit) * 100
        
        if utilisation > 100:
            status = ToleranceStatus.BREACHED
            details = (f"BREACH: Financial impact of {actual_financial_impact:,.0f} exceeds "
                      f"tolerance of {tolerance.financial_impact_limit:,.0f}")
        elif utilisation > 75:
            status = ToleranceStatus.APPROACHING
            details = f"WARNING: {utilisation:.0f}% of financial tolerance consumed."
        else:
            status = ToleranceStatus.WITHIN
            details = f"Within tolerance: {utilisation:.0f}% utilised."
        
        assessment = ToleranceAssessment(
            function_name=function_name,
            dimension="financial",
            tolerance_value=tolerance.financial_impact_limit,
            current_value=actual_financial_impact,
            utilisation_pct=round(utilisation, 1),
            status=status,
            breach_details=details,
        )
        self.assessment_history.append(assessment)
        return assessment
    
    def run_full_assessment(self, function_name: str,
                            disruption_hours: float = 0,
                            financial_impact: float = 0) -> list[ToleranceAssessment]:
        """Run assessments across all dimensions for a critical function."""
        results = []
        
        if disruption_hours > 0:
            results.append(self.assess_time_tolerance(function_name, disruption_hours))
        
        if financial_impact > 0:
            results.append(self.assess_financial_tolerance(function_name, financial_impact))
        
        return results
    
    def get_breach_summary(self) -> dict:
        """Get summary of all tolerance breaches from assessment history."""
        breaches = [a for a in self.assessment_history
                   if a.status == ToleranceStatus.BREACHED]
        approaching = [a for a in self.assessment_history
                      if a.status == ToleranceStatus.APPROACHING]
        
        return {
            "total_assessments": len(self.assessment_history),
            "breaches": len(breaches),
            "approaching_breach": len(approaching),
            "within_tolerance": len(self.assessment_history) - len(breaches) - len(approaching),
            "breach_details": [
                {
                    "function": b.function_name,
                    "dimension": b.dimension,
                    "utilisation_pct": b.utilisation_pct,
                    "details": b.breach_details,
                }
                for b in breaches
            ],
        }
    
    def generate_tolerance_dashboard_data(self) -> list[dict]:
        """Generate data formatted for dashboard display."""
        dashboard_data = []
        
        for name, tolerance in self.tolerances.items():
            dashboard_data.append({
                "function": name,
                "max_disruption_hours": tolerance.max_disruption_hours,
                "financial_limit": tolerance.financial_impact_limit,
                "customer_impact": tolerance.customer_impact,
                "rto_hours": tolerance.recovery_time_objective_hours,
                "rpo_hours": tolerance.recovery_point_objective_hours,
                "regulatory_reporting": tolerance.regulatory_reporting_required,
                "review_frequency_months": tolerance.review_frequency_months,
            })
        
        return dashboard_data
