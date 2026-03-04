"""
Scenario Library — Severe-but-Plausible Disruption Scenarios.

Pre-built scenarios aligned with regulatory expectations for resilience testing:
- DORA Art. 26-27: Digital operational resilience testing
- FINMA Cm 50-55: Scenario testing requirements
- PRA SS1/21 7.1-7.5: Testing for important business services
- BCBS 516 P7: Scenario testing principles

Each scenario defines:
- Trigger event and narrative
- Affected dependency types
- Severity levels and escalation paths
- Expected cascading effects
- Recovery milestones
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScenarioPhase:
    """A phase within a disruption scenario (escalation timeline)."""
    phase_name: str
    hours_from_start: float
    description: str
    affected_dep_types: list[str]
    severity_multiplier: float = 1.0  # How much worse things get
    additional_failures: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    """A severe-but-plausible disruption scenario for resilience testing."""
    id: str
    name: str
    category: str  # cyber, technology, third_party, pandemic, infrastructure, compound
    description: str
    narrative: str  # Detailed storyline for the scenario
    severity: str   # high, critical, extreme
    
    # What gets hit
    primary_affected_types: list[str]  # technology, third_party, people, etc.
    trigger_event: str
    
    # Timeline
    phases: list[ScenarioPhase] = field(default_factory=list)
    total_duration_hours: float = 0.0
    
    # Impact assumptions
    systems_affected_pct: float = 0.0      # % of relevant systems impacted
    workforce_affected_pct: float = 0.0     # % of workforce impacted
    data_loss_risk: bool = False
    customer_facing_impact: bool = True
    regulatory_notification_required: bool = True
    
    # Recovery assumptions
    estimated_recovery_hours: float = 0.0
    requires_manual_workaround: bool = False
    external_support_required: bool = False


# ============================================================================
# PRE-BUILT SCENARIO LIBRARY
# ============================================================================

SCENARIO_LIBRARY = {
    "cyber_ransomware": Scenario(
        id="SCN-001",
        name="Ransomware Attack on Core Banking Systems",
        category="cyber",
        description="A sophisticated ransomware attack encrypts core banking systems, "
                    "disrupting payments processing, client reporting, and trading operations.",
        narrative=(
            "At 02:00 on a Monday morning, the SOC detects unusual encryption activity across "
            "the primary data centre. By 04:00, it is confirmed that a ransomware variant has "
            "encrypted 60% of production servers including the core banking platform, payment "
            "gateway, and client portfolio management system. Backup systems are partially "
            "compromised. The attack vector was a phishing email opened by a third-party "
            "contractor with elevated network privileges."
        ),
        severity="critical",
        primary_affected_types=["technology", "data", "infrastructure"],
        trigger_event="Ransomware encryption of production servers via compromised contractor credentials",
        phases=[
            ScenarioPhase(
                phase_name="Initial Detection",
                hours_from_start=0,
                description="SOC alerts triggered. Core banking platform unresponsive.",
                affected_dep_types=["technology"],
                severity_multiplier=1.0,
            ),
            ScenarioPhase(
                phase_name="Escalation",
                hours_from_start=2,
                description="60% of production servers confirmed encrypted. Payment processing halted.",
                affected_dep_types=["technology", "infrastructure"],
                severity_multiplier=2.0,
                additional_failures=["Core Banking System", "Payment Gateway"],
            ),
            ScenarioPhase(
                phase_name="Containment",
                hours_from_start=6,
                description="Network segmented. Forensic analysis begins. Manual workarounds deployed.",
                affected_dep_types=["technology", "process"],
                severity_multiplier=1.5,
            ),
            ScenarioPhase(
                phase_name="Recovery",
                hours_from_start=24,
                description="Clean backups identified. Restoration of critical systems begins.",
                affected_dep_types=["technology"],
                severity_multiplier=0.8,
            ),
            ScenarioPhase(
                phase_name="Full Restoration",
                hours_from_start=72,
                description="All critical systems restored. Enhanced monitoring in place.",
                affected_dep_types=[],
                severity_multiplier=0.2,
            ),
        ],
        total_duration_hours=72,
        systems_affected_pct=60,
        data_loss_risk=True,
        customer_facing_impact=True,
        regulatory_notification_required=True,
        estimated_recovery_hours=48,
        requires_manual_workaround=True,
        external_support_required=True,
    ),
    
    "cloud_provider_outage": Scenario(
        id="SCN-002",
        name="Major Cloud Provider Multi-Region Outage",
        category="technology",
        description="Primary cloud provider experiences a multi-region outage affecting "
                    "hosted applications, data storage, and disaster recovery capabilities.",
        narrative=(
            "The bank's primary cloud provider (hosting 70% of production workloads) "
            "experiences a cascading failure across two regions due to a network configuration "
            "error during a routine maintenance window. The outage affects compute, storage, "
            "and networking services. The provider's own DR failover fails to activate correctly. "
            "Estimated time to resolution from the provider: 12-24 hours."
        ),
        severity="critical",
        primary_affected_types=["technology", "third_party", "infrastructure"],
        trigger_event="Cloud provider multi-region outage due to network misconfiguration",
        phases=[
            ScenarioPhase(
                phase_name="Service Degradation",
                hours_from_start=0,
                description="Applications hosted on cloud begin experiencing latency and errors.",
                affected_dep_types=["technology", "third_party"],
            ),
            ScenarioPhase(
                phase_name="Full Outage",
                hours_from_start=1,
                description="All cloud-hosted services unavailable. No provider ETA.",
                affected_dep_types=["technology", "third_party", "infrastructure"],
                severity_multiplier=3.0,
            ),
            ScenarioPhase(
                phase_name="Workaround Activation",
                hours_from_start=4,
                description="On-premise fallback activated for Tier 1 functions where available.",
                affected_dep_types=["technology"],
                severity_multiplier=1.5,
            ),
            ScenarioPhase(
                phase_name="Provider Recovery",
                hours_from_start=18,
                description="Cloud services gradually restored. Data integrity checks required.",
                affected_dep_types=["technology"],
                severity_multiplier=0.5,
            ),
        ],
        total_duration_hours=24,
        systems_affected_pct=70,
        data_loss_risk=False,
        customer_facing_impact=True,
        regulatory_notification_required=True,
        estimated_recovery_hours=18,
        external_support_required=True,
    ),
    
    "third_party_failure": Scenario(
        id="SCN-003",
        name="Critical Third-Party Supplier Insolvency",
        category="third_party",
        description="A critical third-party provider (market data, custody, or clearing) "
                    "enters insolvency, requiring immediate transition to alternatives.",
        narrative=(
            "The bank's primary market data provider — used across trading, risk management, "
            "and client reporting — files for insolvency protection. Service continues for "
            "48 hours under administrator control but with degraded quality and no guarantee "
            "of continuity. The bank must activate backup providers and migrate data feeds "
            "across 15+ consuming applications within the service window."
        ),
        severity="high",
        primary_affected_types=["third_party", "data", "process"],
        trigger_event="Critical supplier insolvency filing with 48-hour service guarantee",
        phases=[
            ScenarioPhase(
                phase_name="Notification",
                hours_from_start=0,
                description="Supplier insolvency announced. Services continue under administrator.",
                affected_dep_types=["third_party"],
            ),
            ScenarioPhase(
                phase_name="Assessment",
                hours_from_start=4,
                description="Impact assessment: 15+ applications dependent. Backup provider activated.",
                affected_dep_types=["third_party", "data"],
                severity_multiplier=1.5,
            ),
            ScenarioPhase(
                phase_name="Migration",
                hours_from_start=12,
                description="Data feed migration to backup provider begins. Manual reconciliation.",
                affected_dep_types=["third_party", "process", "data"],
                severity_multiplier=2.0,
            ),
            ScenarioPhase(
                phase_name="Stabilisation",
                hours_from_start=48,
                description="Backup provider fully integrated. Quality validation complete.",
                affected_dep_types=["process"],
                severity_multiplier=0.3,
            ),
        ],
        total_duration_hours=72,
        systems_affected_pct=30,
        customer_facing_impact=True,
        estimated_recovery_hours=48,
        requires_manual_workaround=True,
    ),
    
    "pandemic_disruption": Scenario(
        id="SCN-004",
        name="Pandemic Workforce Disruption",
        category="pandemic",
        description="A severe pandemic wave renders 40%+ of the workforce unavailable, "
                    "with particular impact on specialist operational roles.",
        narrative=(
            "A new pandemic variant causes rapid spread. Within two weeks, 45% of the "
            "workforce is unavailable due to illness, caring responsibilities, or government "
            "restrictions. Key person dependencies are exposed: the payments operations team "
            "in Zurich is reduced to 2 of 8 staff, the IT infrastructure team loses its only "
            "DBA, and the Singapore branch has only 1 operational risk officer remaining."
        ),
        severity="high",
        primary_affected_types=["people", "process"],
        trigger_event="Pandemic variant causing 45% workforce unavailability over 2 weeks",
        phases=[
            ScenarioPhase(
                phase_name="Early Spread",
                hours_from_start=0,
                description="15% workforce affected. BCP activated.",
                affected_dep_types=["people"],
            ),
            ScenarioPhase(
                phase_name="Peak Impact",
                hours_from_start=168,  # 1 week
                description="45% workforce unavailable. Key person dependencies critical.",
                affected_dep_types=["people", "process"],
                severity_multiplier=3.0,
            ),
            ScenarioPhase(
                phase_name="Sustained Disruption",
                hours_from_start=336,  # 2 weeks
                description="Workforce gradually recovering. Cross-training gaps exposed.",
                affected_dep_types=["people"],
                severity_multiplier=2.0,
            ),
            ScenarioPhase(
                phase_name="Recovery",
                hours_from_start=672,  # 4 weeks
                description="Workforce at 85%. Lessons learned review initiated.",
                affected_dep_types=["people"],
                severity_multiplier=0.5,
            ),
        ],
        total_duration_hours=672,
        workforce_affected_pct=45,
        customer_facing_impact=True,
        estimated_recovery_hours=504,
        requires_manual_workaround=True,
    ),
    
    "data_centre_failure": Scenario(
        id="SCN-005",
        name="Primary Data Centre Infrastructure Failure",
        category="infrastructure",
        description="Complete loss of primary data centre due to power/cooling failure, "
                    "requiring full failover to disaster recovery site.",
        narrative=(
            "A cascading power failure at the primary data centre in Zurich — triggered by "
            "a transformer explosion during a heatwave — causes the UPS to fail after 4 hours "
            "and the backup generators to overheat. All systems in the primary DC go offline. "
            "The DR site in Geneva must be activated, but the last full sync was 2 hours ago "
            "and some applications have never been tested in DR failover."
        ),
        severity="critical",
        primary_affected_types=["infrastructure", "technology"],
        trigger_event="Cascading power failure and cooling system collapse at primary DC",
        phases=[
            ScenarioPhase(
                phase_name="Power Failure",
                hours_from_start=0,
                description="Mains power lost. UPS activated. 4-hour battery life.",
                affected_dep_types=["infrastructure"],
            ),
            ScenarioPhase(
                phase_name="Full Outage",
                hours_from_start=4,
                description="UPS depleted. All primary DC systems offline.",
                affected_dep_types=["infrastructure", "technology"],
                severity_multiplier=3.0,
                additional_failures=["Primary DC"],
            ),
            ScenarioPhase(
                phase_name="DR Activation",
                hours_from_start=6,
                description="DR site activation begins. Some apps fail to start in DR.",
                affected_dep_types=["technology"],
                severity_multiplier=2.0,
            ),
            ScenarioPhase(
                phase_name="Partial Recovery",
                hours_from_start=12,
                description="Tier 1 systems operational in DR. Tier 2/3 still recovering.",
                affected_dep_types=["technology"],
                severity_multiplier=1.0,
            ),
        ],
        total_duration_hours=48,
        systems_affected_pct=100,
        data_loss_risk=True,
        customer_facing_impact=True,
        regulatory_notification_required=True,
        estimated_recovery_hours=12,
        external_support_required=True,
    ),
    
    "compound_event": Scenario(
        id="SCN-006",
        name="Multi-Hazard Compound Event",
        category="compound",
        description="Simultaneous cyber attack during a cloud provider degradation, "
                    "compounding impact and overwhelming response capacity.",
        narrative=(
            "During an ongoing cloud provider performance degradation (reduced to 60% capacity), "
            "the bank experiences a targeted DDoS attack on its client-facing web services. "
            "The incident response team is already stretched managing the cloud issues. "
            "The DDoS attack exploits the reduced cloud capacity to cause significantly "
            "greater customer impact than either event alone."
        ),
        severity="extreme",
        primary_affected_types=["technology", "third_party", "infrastructure", "people"],
        trigger_event="Concurrent cloud degradation and targeted DDoS attack",
        phases=[
            ScenarioPhase(
                phase_name="Cloud Degradation",
                hours_from_start=0,
                description="Cloud provider at 60% capacity. IR team deployed.",
                affected_dep_types=["technology", "third_party"],
            ),
            ScenarioPhase(
                phase_name="DDoS Attack",
                hours_from_start=3,
                description="Targeted DDoS on client portals. IR team overwhelmed.",
                affected_dep_types=["technology", "infrastructure"],
                severity_multiplier=4.0,
                additional_failures=["Client Web Portal", "Mobile Banking"],
            ),
            ScenarioPhase(
                phase_name="Compound Impact",
                hours_from_start=6,
                description="Client services fully down. Media attention. Board escalation.",
                affected_dep_types=["technology", "third_party", "people"],
                severity_multiplier=5.0,
            ),
            ScenarioPhase(
                phase_name="Staged Recovery",
                hours_from_start=18,
                description="DDoS mitigated. Cloud slowly recovering. Services restored.",
                affected_dep_types=["technology"],
                severity_multiplier=1.0,
            ),
        ],
        total_duration_hours=36,
        systems_affected_pct=80,
        customer_facing_impact=True,
        regulatory_notification_required=True,
        estimated_recovery_hours=18,
        requires_manual_workaround=True,
        external_support_required=True,
    ),
}


def get_scenario(scenario_id: str) -> Optional[Scenario]:
    """Retrieve a pre-built scenario by ID."""
    return SCENARIO_LIBRARY.get(scenario_id)


def list_scenarios() -> list[dict]:
    """List all available scenarios with summary information."""
    return [
        {
            "id": s.id,
            "key": key,
            "name": s.name,
            "category": s.category,
            "severity": s.severity,
            "duration_hours": s.total_duration_hours,
            "description": s.description,
        }
        for key, s in SCENARIO_LIBRARY.items()
    ]


def build_custom_scenario(**kwargs) -> Scenario:
    """Build a custom scenario with user-defined parameters."""
    return Scenario(**kwargs)
