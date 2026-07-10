import streamlit as st

from api import analyze_pipeline
from components import (
    render_header,
    render_pipeline,
    render_analysis,
    render_patch,
    render_assessment,
    render_metrics,
    render_json,
)
from styles import load_styles


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AutoPatch Forge Control Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_styles()

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

render_header()

# ---------------------------------------------------------
# KPI Placeholders (IMPORTANT)
# ---------------------------------------------------------

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

kpi_agents = kpi_col1.empty()
kpi_runtime = kpi_col2.empty()
kpi_risk = kpi_col3.empty()

with kpi_agents:
    st.metric(
        "🤖 AI Agents",
        "5",
        help="Trace Analyzer • Patch Planner • Gemma Risk Assessor • Patch Engine • GitHub Automation",
    )

with kpi_runtime:
    st.metric(
        "⚡ Runtime",
        "--",
    )

with kpi_risk:
    st.metric(
        "🛡 Risk",
        "--",
    )

st.divider()

# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------

left, right = st.columns([1.25, 0.95])

# ---------------------------------------------------------
# Left Panel
# ---------------------------------------------------------

with left:

    st.subheader("Pipeline Input")

    repo = st.text_input(
        "Repository",
        "https://github.com/apurba-labs/autopatch-forge",
    )

    branch = st.text_input(
        "Branch",
        "main",
    )

    commit = st.text_input(
        "Commit SHA",
        "a4f892c900e1215db84f",
    )

    error_log = st.text_area(
        "Pipeline Error Log",
        height=220,
        value="""Traceback (most recent call last):
File "app/utils/helpers.py", line 14
ModuleNotFoundError: No module named 'httpx'""",
    )

    analyze = st.button(
        "🚀 Analyze Pipeline",
        use_container_width=True,
        type="primary",
    )

# ---------------------------------------------------------
# Right Panel
# ---------------------------------------------------------

with right:

    st.subheader("Autonomous Workflow")

    st.info(
        """
1️⃣ Trace Analyzer

⬇️

2️⃣ Patch Planner

⬇️

3️⃣ Gemma Risk Assessment

⬇️

4️⃣ Patch Engine

⬇️

5️⃣ GitHub Automation
"""
    )

    status = st.empty()

    status.info(
        "Waiting for pipeline execution..."
    )

# ---------------------------------------------------------
# Execute
# ---------------------------------------------------------

if analyze:

    with st.spinner("Running autonomous remediation pipeline..."):

        response = analyze_pipeline(
            repo_url=repo,
            branch=branch,
            commit_sha=commit,
            error_log=error_log,
        )

    status.success("Pipeline completed successfully.")

    metrics = response.get("metrics", {})
    assessment = response.get("assessment", {})

    # -------------------------------------------------
    # Update existing KPI cards (NO DUPLICATES)
    # -------------------------------------------------

    with kpi_agents:
        st.metric(
            "🤖 AI Agents",
            "5",
        )

    with kpi_runtime:
        st.metric(
            "⚡ Runtime",
            f'{metrics.get("total_ms","--")} ms',
        )

    with kpi_risk:
        st.metric(
            "🛡 Risk",
            assessment.get(
                "risk",
                "--",
            ).upper(),
        )

    st.divider()

    render_pipeline(response)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        render_analysis(response)

    with col2:
        render_patch(response)

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        render_assessment(response)

    with col4:
        render_metrics(response)

    st.divider()

    render_json(response)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "🚀 AutoPatch Forge • Fireworks AI • Google DeepMind Gemma • FastAPI • Docker"
)