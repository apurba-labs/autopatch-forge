import streamlit as st


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

def render_header():

    st.markdown(
        """
<div class="hero">

<h1>🚀 AutoPatch Forge</h1>

<h3>Autonomous Self-Healing CI/CD</h3>

<p>
AI Agents • Fireworks AI • Gemma • Docker
</p>

</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Pipeline
# ---------------------------------------------------------

def render_pipeline(response):

    st.subheader("🤖 Autonomous Agent Workflow")

    pipeline = response.get("pipeline", [])

    if not pipeline:
        st.info("Pipeline has not been executed yet.")
        return

    cols = st.columns(len(pipeline))

    for col, stage in zip(cols, pipeline):
        with col:
            st.success(stage.replace("_", " ").title())


# ---------------------------------------------------------
# Analysis
# ---------------------------------------------------------

def render_analysis(response):

    analysis = (
        response.get("telemetry", {})
        .get("analysis", {})
    )

    st.subheader("🔍 Trace Analysis")

    st.metric(
        "Exception",
        analysis.get("exception_type", "-"),
    )

    st.text_input(
        "Target File",
        analysis.get("target_file", "-"),
        disabled=True,
    )

    st.metric(
        "Line Number",
        analysis.get("line_number", "-"),
    )

    if analysis.get("raw_error"):

        st.code(
            analysis.get("raw_error"),
            language="text",
        )


# ---------------------------------------------------------
# Patch
# ---------------------------------------------------------

def render_patch(response):

    patch = (
        response.get("telemetry", {})
        .get("patch", {})
    )

    st.subheader("🩹 Generated Patch")

    st.metric(
        "Operation",
        patch.get("operation", "-"),
    )

    st.code(
        patch.get("content", ""),
        language="python",
    )

    st.info(
        patch.get(
            "reason",
            "No explanation available.",
        )
    )


# ---------------------------------------------------------
# Assessment
# ---------------------------------------------------------

def render_assessment(response):

    assessment = response.get("assessment", {})

    validation = (
        response.get("telemetry", {})
        .get("validation", {})
    )

    st.subheader("🛡 AI Risk Assessment")

    risk = assessment.get("risk", "unknown").lower()

    confidence = float(
        assessment.get("confidence", 0.0)
    )

    if risk == "low":
        st.success("🟢 LOW RISK")

    elif risk == "medium":
        st.warning("🟡 MEDIUM RISK")

    else:
        st.error("🔴 HIGH RISK")

    st.metric(
        "Confidence",
        f"{confidence*100:.0f}%",
    )

    st.write(
        "**Recommendation**"
    )

    st.info(
        validation.get(
            "recommended_action",
            "-",
        )
    )

    st.write(
        "**Reasoning**"
    )

    st.caption(
        validation.get(
            "reasoning",
            "",
        )
    )


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

def render_metrics(response):

    metrics = response.get("metrics", {})

    st.subheader("⚡ Runtime Metrics")

    if not metrics:
        st.info("Metrics unavailable.")
        return

    col1, col2 = st.columns(2)

    items = list(metrics.items())

    midpoint = (len(items) + 1) // 2

    left_items = items[:midpoint]
    right_items = items[midpoint:]

    with col1:

        for key, value in left_items:

            st.metric(
                key.replace("_", " ").title(),
                f"{value} ms",
            )

    with col2:

        for key, value in right_items:

            st.metric(
                key.replace("_", " ").title(),
                f"{value} ms",
            )


# ---------------------------------------------------------
# Raw JSON
# ---------------------------------------------------------

def render_json(response):

    with st.expander(
        "📄 Raw API Response",
        expanded=False,
    ):
        st.json(response)