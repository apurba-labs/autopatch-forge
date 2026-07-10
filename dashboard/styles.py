import streamlit as st


def load_styles():
    st.markdown(
        """
<style>

/* ==========================================================
   Global
========================================================== */

html,
body,
[class*="css"]{
    font-family: Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
    max-width:1350px;
}

section.main{
    background:#F8FAFC;
}


/* ==========================================================
   Hero Banner
========================================================== */

.hero{
    padding:22px 28px;
    border-radius:18px;
    background:linear-gradient(135deg,#2563EB,#4F46E5);
    color:white;
    margin-bottom:20px;
    box-shadow:0 8px 24px rgba(37,99,235,.18);
}

.hero h1{
    margin:0;
    font-size:36px;
    font-weight:800;
}

.hero h3{
    margin:6px 0;
    font-size:20px;
    font-weight:600;
}

.hero p{
    margin:4px 0;
    font-size:15px;
    opacity:.9;
}


/* ==========================================================
   Metric Cards
========================================================== */

[data-testid="stMetric"]{
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:14px;
    padding:18px;
    box-shadow:0 3px 10px rgba(15,23,42,.05);
}

[data-testid="stMetricLabel"]{
    font-size:13px;
    font-weight:600;
}

[data-testid="stMetricValue"]{
    font-size:28px;
    font-weight:700;
}


/* ==========================================================
   Inputs
========================================================== */

textarea,
input{
    border-radius:10px !important;
}

textarea{
    font-family:JetBrains Mono,monospace;
}


/* ==========================================================
   Button
========================================================== */

.stButton>button{
    width:100%;
    height:52px;
    border-radius:12px;
    border:none;
    font-size:18px;
    font-weight:700;
    background:#2563EB;
    color:white;
    transition:.25s;
}

.stButton>button:hover{
    background:#1D4ED8;
}


/* ==========================================================
   Success / Warning / Error
========================================================== */

.stSuccess{
    border-radius:10px;
}

.stWarning{
    border-radius:10px;
}

.stError{
    border-radius:10px;
}

.stInfo{
    border-radius:10px;
}


/* ==========================================================
   Code Blocks
========================================================== */

pre{
    border-radius:12px !important;
}

code{
    font-family:JetBrains Mono,monospace;
}


/* ==========================================================
   Expander
========================================================== */

.streamlit-expanderHeader{
    font-weight:600;
}


/* ==========================================================
   Divider
========================================================== */

hr{
    margin-top:2rem;
    margin-bottom:2rem;
}


/* ==========================================================
   Footer
========================================================== */

.footer{
    text-align:center;
    color:#64748B;
    margin-top:50px;
    font-size:14px;
}

</style>
""",
        unsafe_allow_html=True,
    )