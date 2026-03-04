"""
Operational Resilience Dashboard — Streamlit Application

Interactive dashboard for visualising and managing operational resilience
across critical functions, dependencies, scenarios, and maturity scoring.
"""

import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.dependency_mapper.mapper import DependencyMapper
from src.impact_tolerance.engine import ImpactToleranceEngine
from src.scenario_testing.scenarios import SCENARIO_LIBRARY, list_scenarios
from src.scenario_testing.simulator import ResilienceSimulator
from src.resilience_scorer.scorer import ResilienceScorer, FRAMEWORK_PILLARS
from src.incident_tracker.tracker import IncidentTracker


# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Operational Resilience Toolkit",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {font-size: 2rem; font-weight: 700; color: #1B2A4A; margin-bottom: 0.5rem;}
    .sub-header {font-size: 1rem; color: #2E6B8A; margin-bottom: 2rem;}
    .metric-card {background: #F0F4F7; padding: 1rem; border-radius: 8px; border-left: 4px solid #2E6B8A;}
    .breach-card {background: #FFF0F0; padding: 1rem; border-radius: 8px; border-left: 4px solid #C23B22;}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# LOAD SAMPLE DATA
# ============================================================================
@st.cache_resource
def load_sample_bank():
    mapper = DependencyMapper()
    engine = ImpactToleranceEngine()

    with open("data/sample_bank_config.json") as f:
        config = json.load(f)

    for cf in config["critical_functions"]:
        mapper.add_critical_function(cf["name"], tier=cf["tier"], owner=cf.get("owner", ""))

    for dep in config["dependencies"]:
        mapper.add_dependency(dep["function"], dep["name"], dep_type=dep["type"],
                            criticality=dep.get("criticality", "medium"))

    for sub in config.get("sub_dependencies", []):
        mapper.add_sub_dependency(sub["parent"], sub["child"], dep_type=sub["type"])

    for tol in config["impact_tolerances"]:
        engine.set_tolerance(
            tol["function"],
            max_disruption_hours=tol["max_disruption_hours"],
            recovery_time_objective_hours=tol.get("rto_hours", 0),
            recovery_point_objective_hours=tol.get("rpo_hours", 0),
            financial_impact_limit=tol.get("financial_impact_limit", 0),
            customer_impact=tol.get("customer_impact", "medium"),
            regulatory_reporting_required=tol.get("regulatory_reporting", False),
        )

    return mapper, engine


mapper, engine = load_sample_bank()


# ============================================================================
# SIDEBAR
# ============================================================================
st.sidebar.markdown("## 🏦 Resilience Toolkit")
page = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "🔗 Dependency Map",
    "⚡ Scenario Testing",
    "📈 Maturity Scoring",
    "🚨 Incident Tracker",
])


# ============================================================================
# DASHBOARD
# ============================================================================
if page == "📊 Dashboard":
    st.markdown('<div class="main-header">Operational Resilience Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">2nd Line of Defence — Real-time Resilience Posture</div>', unsafe_allow_html=True)

    report = mapper.generate_summary_report()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Critical Functions", report["total_critical_functions"])
    col2.metric("Dependencies Mapped", report["total_dependencies"])
    col3.metric("Single Points of Failure", report["single_points_of_failure"],
                delta=f"-{report['single_points_of_failure']}" if report["single_points_of_failure"] > 0 else "0",
                delta_color="inverse")
    col4.metric("Concentration Risks", report["concentration_risks"])

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Top Single Points of Failure")
        for spof in report["spof_details"]:
            st.warning(f"**{spof['dependency']}** ({spof['type']}) — "
                      f"Impacts {spof['impact_count']} critical function(s)")

    with col_right:
        st.subheader("Impact Tolerance Overview")
        tol_data = engine.generate_tolerance_dashboard_data()
        df = pd.DataFrame(tol_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================================
# DEPENDENCY MAP
# ============================================================================
elif page == "🔗 Dependency Map":
    st.markdown('<div class="main-header">Critical Function Dependency Map</div>', unsafe_allow_html=True)

    report = mapper.generate_summary_report()

    # Concentration risks chart
    concentrations = mapper.find_concentration_risks()
    if concentrations:
        st.subheader("Concentration Risk Analysis")
        fig = go.Figure(go.Bar(
            x=[c["dependency"] for c in concentrations],
            y=[c["concentration_count"] for c in concentrations],
            marker_color=["#C23B22" if c["risk_level"] == "critical" else "#E8630A"
                         for c in concentrations],
        ))
        fig.update_layout(
            yaxis_title="Dependent Critical Functions",
            xaxis_title="Dependency",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Dependency table
    st.subheader("Full Dependency Register")
    dep_rows = []
    for u, v, d in mapper.graph.edges(data=True):
        dep_rows.append({
            "Critical Function": u if u in mapper.critical_functions else "-",
            "Dependency": v,
            "Type": d.get("dep_type", "unknown"),
            "Criticality": d.get("criticality", "medium"),
        })
    st.dataframe(pd.DataFrame(dep_rows), use_container_width=True, hide_index=True)


# ============================================================================
# SCENARIO TESTING
# ============================================================================
elif page == "⚡ Scenario Testing":
    st.markdown('<div class="main-header">Scenario Testing Framework</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Severe-but-Plausible Disruption Scenarios</div>', unsafe_allow_html=True)

    scenarios = list_scenarios()
    scenario_names = {s["key"]: f"{s['name']} ({s['severity']})" for s in scenarios}
    selected = st.selectbox("Select Scenario", list(scenario_names.keys()),
                           format_func=lambda x: scenario_names[x])

    if st.button("🚀 Run Simulation", type="primary"):
        simulator = ResilienceSimulator(mapper, engine)
        result = simulator.run_scenario(selected)

        # Overall rating
        color = {"pass": "green", "conditional_pass": "orange", "fail": "red"}
        rating_color = color.get(result.overall_resilience_rating, "gray")
        st.markdown(f"### Overall Rating: :{rating_color}[{result.overall_resilience_rating.upper()}]")

        col1, col2, col3 = st.columns(3)
        col1.metric("Functions Impacted", len(result.affected_critical_functions))
        col2.metric("Tolerance Breaches", len(result.tolerance_breaches))
        col3.metric("Est. Recovery (hours)", result.estimated_recovery_hours)

        # Phase timeline
        st.subheader("Scenario Timeline")
        scenario = SCENARIO_LIBRARY[selected]
        timeline_df = pd.DataFrame([
            {"Phase": p.phase_name, "Hours": p.hours_from_start,
             "Severity": p.severity_multiplier, "Description": p.description}
            for p in scenario.phases
        ])
        st.dataframe(timeline_df, use_container_width=True, hide_index=True)

        # Gaps and recommendations
        if result.gaps_identified:
            st.subheader("Gaps Identified")
            for gap in result.gaps_identified:
                st.error(f"🔴 {gap}")

        if result.recommendations:
            st.subheader("Recommendations")
            for rec in result.recommendations:
                st.info(f"💡 {rec}")


# ============================================================================
# MATURITY SCORING
# ============================================================================
elif page == "📈 Maturity Scoring":
    st.markdown('<div class="main-header">Resilience Maturity Assessment</div>', unsafe_allow_html=True)

    framework = st.selectbox("Select Framework", list(FRAMEWORK_PILLARS.keys()))

    scorer = ResilienceScorer()
    assessment = scorer.assess(mapper, engine, framework=framework)

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Score", f"{assessment.overall_score}/5.0")
    col2.metric("Maturity Level", assessment.maturity_level)
    col3.metric("Critical Gaps", len(assessment.critical_gaps))

    # Radar chart
    pillar_names = [p.pillar_name for p in assessment.pillar_scores]
    current_scores = [p.current_score for p in assessment.pillar_scores]
    target_scores = [p.target_score for p in assessment.pillar_scores]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=current_scores + [current_scores[0]],
        theta=pillar_names + [pillar_names[0]],
        fill="toself",
        name="Current",
        fillcolor="rgba(46,107,138,0.3)",
        line_color="#2E6B8A",
    ))
    fig.add_trace(go.Scatterpolar(
        r=target_scores + [target_scores[0]],
        theta=pillar_names + [pillar_names[0]],
        fill="toself",
        name="Target",
        fillcolor="rgba(194,59,34,0.1)",
        line_color="#C23B22",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Pillar detail table
    st.subheader("Pillar Details")
    pillar_df = pd.DataFrame([
        {
            "Pillar": p.pillar_name,
            "Reference": p.reference,
            "Current": p.current_score,
            "Target": p.target_score,
            "Gap": p.gap,
        }
        for p in assessment.pillar_scores
    ])
    st.dataframe(pillar_df, use_container_width=True, hide_index=True)


# ============================================================================
# INCIDENT TRACKER
# ============================================================================
elif page == "🚨 Incident Tracker":
    st.markdown('<div class="main-header">Incident Management</div>', unsafe_allow_html=True)

    tracker = IncidentTracker()

    # Add sample incidents for demo
    tracker.create_incident(
        "Core Banking System Outage", "Unplanned outage during peak hours",
        severity="P1", category="technology",
        affected_functions=["Payments Processing"],
        affected_dependencies=["Core Banking System"],
        downtime_hours=3.5, customers_affected=45000, financial_impact=1_200_000,
    )
    tracker.create_incident(
        "Cloud Provider Latency", "AWS EU region degraded performance",
        severity="P2", category="third_party",
        affected_dependencies=["Cloud Provider A"],
        downtime_hours=1.5, customers_affected=30000,
    )
    tracker.create_incident(
        "KYC Screening Timeout", "Refinitiv API response times exceeding SLA",
        severity="P3", category="third_party",
        affected_dependencies=["KYC Screening Platform"],
        downtime_hours=0.5,
    )
    tracker.add_root_cause("INC-0001", "system_failure", "DB connection pool exhaustion")
    tracker.add_remediation_action("INC-0001", "Implement DB auto-scaling",
                                    "DBA Team", "2026-04-01")

    trends = tracker.get_trend_analysis()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Incidents", trends["total_incidents"])
    col2.metric("Total Downtime", f"{trends['total_downtime_hours']}h")
    col3.metric("Financial Impact", f"CHF {trends['total_financial_impact']:,.0f}")
    col4.metric("Open Actions", trends["open_remediation_actions"])

    # Severity distribution
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("By Severity")
        fig = px.pie(
            values=list(trends["by_severity"].values()),
            names=list(trends["by_severity"].keys()),
            color_discrete_sequence=["#C23B22", "#E8630A", "#D4A843", "#2E6B8A"],
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("By Category")
        fig = px.pie(
            values=list(trends["by_category"].values()),
            names=list(trends["by_category"].keys()),
            color_discrete_sequence=["#2E86AB", "#E8630A", "#7B2D8E", "#2D8E6B"],
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Board messages
    board = tracker.get_board_report_data()
    st.subheader("Key Messages for Board Reporting")
    for msg in board["key_messages"]:
        st.info(msg)


# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown(
    "<div style='text-align: center; color: #999; font-size: 0.8rem;'>"
    "Operational Resilience Toolkit v1.0 | Built by Saranne Ndamba | "
    "DORA · FINMA · PRA · BCBS Aligned</div>",
    unsafe_allow_html=True,
)
