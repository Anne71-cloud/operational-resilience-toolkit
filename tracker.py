"""
Incident Tracker — Incident lifecycle management and lessons learned.

Manages operational incidents from detection through root cause analysis
to lessons learned, with trend analysis and pattern detection.

Regulatory alignment:
- DORA Art. 17-23: ICT-related incident management
- FINMA Cm 60-65: Incident reporting and management
- PRA SS1/21 8.1-8.3: Self-assessment including incident learning
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from collections import Counter


@dataclass
class Incident:
    """An operational resilience incident."""
    id: str
    title: str
    description: str
    severity: str  # P1 (critical), P2 (high), P3 (medium), P4 (low)
    category: str  # technology, process, people, third_party, external, cyber
    status: str = "open"  # open, investigating, mitigating, resolved, closed

    # Affected areas
    affected_functions: list[str] = field(default_factory=list)
    affected_dependencies: list[str] = field(default_factory=list)

    # Timeline
    detected_at: str = ""
    acknowledged_at: str = ""
    mitigated_at: str = ""
    resolved_at: str = ""
    closed_at: str = ""

    # Impact
    downtime_hours: float = 0.0
    customers_affected: int = 0
    financial_impact: float = 0.0
    tolerance_breached: bool = False
    regulatory_notification: bool = False

    # Root cause
    root_cause_category: str = ""  # human_error, system_failure, config_change,
                                    # third_party, capacity, security, external
    root_cause_description: str = ""

    # Lessons learned
    lessons_learned: list[str] = field(default_factory=list)
    remediation_actions: list[dict] = field(default_factory=list)
    # Each action: {"description": str, "owner": str, "due_date": str, "status": str}

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class IncidentTracker:
    """Manages operational incidents and extracts resilience insights."""

    def __init__(self):
        self.incidents: dict[str, Incident] = {}
        self._counter = 0

    def create_incident(self, title: str, description: str,
                        severity: str = "P3", category: str = "technology",
                        **kwargs) -> Incident:
        """Register a new operational incident."""
        self._counter += 1
        incident_id = f"INC-{self._counter:04d}"

        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            detected_at=datetime.now().isoformat(),
            **kwargs,
        )
        self.incidents[incident_id] = incident
        return incident

    def update_status(self, incident_id: str, new_status: str,
                      notes: str = "") -> Incident:
        """Update incident status with timestamp."""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.status = new_status
        now = datetime.now().isoformat()

        if new_status == "investigating":
            incident.acknowledged_at = now
        elif new_status == "mitigating":
            incident.mitigated_at = now
        elif new_status == "resolved":
            incident.resolved_at = now
        elif new_status == "closed":
            incident.closed_at = now

        return incident

    def add_root_cause(self, incident_id: str, category: str,
                       description: str) -> Incident:
        """Record root cause analysis results."""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.root_cause_category = category
        incident.root_cause_description = description
        return incident

    def add_lesson_learned(self, incident_id: str, lesson: str) -> Incident:
        """Add a lesson learned from an incident."""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.lessons_learned.append(lesson)
        return incident

    def add_remediation_action(self, incident_id: str, description: str,
                                owner: str, due_date: str) -> Incident:
        """Add a remediation action to track."""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.remediation_actions.append({
            "description": description,
            "owner": owner,
            "due_date": due_date,
            "status": "open",
            "created_at": datetime.now().isoformat(),
        })
        return incident

    def get_trend_analysis(self) -> dict:
        """Analyse incident trends for board reporting."""
        if not self.incidents:
            return {"total": 0, "message": "No incidents recorded"}

        incidents = list(self.incidents.values())

        severity_dist = Counter(i.severity for i in incidents)
        category_dist = Counter(i.category for i in incidents)
        root_cause_dist = Counter(
            i.root_cause_category for i in incidents if i.root_cause_category
        )
        status_dist = Counter(i.status for i in incidents)

        tolerance_breaches = sum(1 for i in incidents if i.tolerance_breached)

        total_downtime = sum(i.downtime_hours for i in incidents)
        total_financial = sum(i.financial_impact for i in incidents)
        total_customers = sum(i.customers_affected for i in incidents)

        # Recurring patterns
        recurring_deps = Counter()
        for i in incidents:
            for dep in i.affected_dependencies:
                recurring_deps[dep] += 1
        repeat_offenders = {k: v for k, v in recurring_deps.items() if v >= 2}

        return {
            "total_incidents": len(incidents),
            "by_severity": dict(severity_dist),
            "by_category": dict(category_dist),
            "by_root_cause": dict(root_cause_dist),
            "by_status": dict(status_dist),
            "tolerance_breaches": tolerance_breaches,
            "total_downtime_hours": round(total_downtime, 1),
            "total_financial_impact": round(total_financial, 2),
            "total_customers_affected": total_customers,
            "repeat_offender_dependencies": repeat_offenders,
            "open_remediation_actions": sum(
                1 for i in incidents
                for a in i.remediation_actions if a["status"] == "open"
            ),
        }

    def get_board_report_data(self) -> dict:
        """Generate data suitable for board-level reporting."""
        trends = self.get_trend_analysis()
        p1_p2 = [
            {
                "id": i.id,
                "title": i.title,
                "severity": i.severity,
                "status": i.status,
                "downtime_hours": i.downtime_hours,
                "tolerance_breached": i.tolerance_breached,
                "root_cause": i.root_cause_category,
                "open_actions": sum(
                    1 for a in i.remediation_actions if a["status"] == "open"
                ),
            }
            for i in self.incidents.values()
            if i.severity in ("P1", "P2")
        ]

        return {
            "reporting_period": datetime.now().strftime("%Y-%m"),
            "summary": trends,
            "critical_high_incidents": p1_p2,
            "key_messages": self._generate_key_messages(trends),
        }

    def _generate_key_messages(self, trends: dict) -> list[str]:
        """Generate key messages for board reporting."""
        messages = []
        total = trends.get("total_incidents", 0)
        messages.append(f"{total} operational incidents recorded in the period.")

        breaches = trends.get("tolerance_breaches", 0)
        if breaches > 0:
            messages.append(
                f"WARNING: {breaches} incident(s) resulted in impact tolerance breaches."
            )

        repeat = trends.get("repeat_offender_dependencies", {})
        if repeat:
            top = max(repeat, key=repeat.get)
            messages.append(
                f"Recurring issue: '{top}' involved in {repeat[top]} incidents. "
                f"Recommend targeted remediation."
            )

        open_actions = trends.get("open_remediation_actions", 0)
        if open_actions > 0:
            messages.append(f"{open_actions} remediation action(s) remain open.")

        return messages
